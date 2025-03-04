import datetime
import os
import pickle
import time
from dataclasses import dataclass, field
from app.alternative_to_onedrive import SharepointHandler

import pandas as pd


@dataclass
class Data:
    valid: pd.DataFrame = field(default_factory=pd.DataFrame)
    invalid: pd.DataFrame = field(default_factory=pd.DataFrame)


class AppState:
    def __init__(self):
        self.spHandler = SharepointHandler()
        self.relUrl = "/sites/Codex-Operao/Documentos Compartilhados/General/"
        self.xlsx = None
        self.employee_list = None
        self.filename_employees = None
        self.data = Data()
        self.progress = 0

    def getSpHandlers(self) -> dict[str: pd.io.excel.ExcelFile]:
        """ Get Sharepoint Handlers """
        # Load the io handlers for each Excel
        d = dict()
        for sigla in ("AF", "GK", "LP", "RZ"):
            d[sigla] = self.spHandler.get_excel_file(f"{self.relUrl}{os.getenv(f'XLSX_{sigla}')}")
            print("Got io handler:", sigla)

        return d

    def _filter_desired(self):
        if self.employee_list is not None:
            state = self.filename_employees.copy()
            for k, vs in state.items():
                if any([employee in vs for employee in self.employee_list]):
                    for v in vs.copy():
                        if v not in self.employee_list:
                            self.filename_employees[k].remove(v)
                else:
                    del self.filename_employees[k]

    def get_employee_list(self) -> list[str]:
        filename_employees = {
            sigla: [
                sheet_name
                for sheet_name in workbook.sheet_names
                if sheet_name not in ["KEYS", "INÍCIO", "PowerQuery"]
            ]
            for sigla, workbook in self.xlsx.items()
        }

        self.filename_employees = filename_employees
        self.employee_list = [
            employee
            for employees in self.filename_employees.values()
            for employee in employees
        ]
        self._filter_desired()

    def _get_df(self, excel_file: pd.io.excel.ExcelFile, employee: str) -> pd.DataFrame:
        # Log employee
        print(" >>", employee)

        # Read Excel sheetname of the specific employee
        first_columns = ["Data", "Projeto", "Produto", "Atividade"]
        columns = first_columns + [
            "Horário 1 - Inicio",
            "Horário 1 - fim",
            "Horário 2 - Inicio",
            "Horário 2 - fim",
            "Horário 3 - Inicio",
            "Horário 3 - fim",
            "Horário 4 - Inicio",
            "Horário 4 - fim",
        ]
        # Try read. If it fails, remove name from AppState, warn error, return "None"
        df = pd.read_excel(excel_file, employee, usecols=columns)

        # Workaround for empty dataframes (when people add news sheets inadvertently)
        if df.columns.empty:
            self.employee_list.remove(employee)
            sigla = "antes_era_algo_outro"
            self.filename_employees[sigla].remove(employee)
            print(
                f" WARNING: '{employee}' has no data. Warning: REMOVED from data importer."
            )
            return None

        # Keep row number
        df["line"] = df.index + 2

        # Explode activity in its block hours (explode 1:N relationships)
        lista = []
        for i in range(1, 5):
            workhour_block = df[
                first_columns + [f"Horário {i} - Inicio", f"Horário {i} - fim", "line"]
            ].copy()
            workhour_block.columns = first_columns + [
                "Horário - Inicio",
                "Horário - fim",
                "line",
            ]
            lista.append(workhour_block)
        df = pd.concat(lista, axis=0, ignore_index=True)

        # Drop rows with empty values
        all_columns_null = df[[c for c in df.columns if c != "line"]].isna().all(axis=1)
        df = df[~all_columns_null]

        # Drop duplicates resulting of exploding activity in block hours
        df = df.drop_duplicates()

        # Columns in lowercase
        df.columns = [
            "date",
            "project",
            "product",
            "activity",
            "start_time",
            "end_time",
            "line",
        ]

        # Adjust decimal to time
        for column in ["start_time", "end_time"]:
            series = df[column].apply(
                lambda x: decimal_to_time(x) if isinstance(x, (int, float)) else x
            )
            df.loc[:, column] = series.apply(
                lambda x: x.time() if isinstance(x, (datetime.datetime)) else x
            )

        # Save for later
        mask_start_time = (~df["start_time"].isna()) & (
            df["start_time"].apply(lambda x: not isinstance(x, datetime.time))
        )
        mask_final_time = (~df["end_time"].isna()) & (
            df["end_time"].apply(lambda x: not isinstance(x, datetime.time))
        )
        # start_time OR end_time is NA but not all is NA
        mask_not_all_na = (
            ((df.start_time.isna()) | (df.start_time.isna()))
            & (~df.drop(columns=["line"]).isna().all(axis=1))
            & (df.date.isna())
        )
        mask = mask_start_time | mask_final_time | mask_not_all_na
        df_wrong = df[mask].copy()
        df_wrong["hours"] = None
        df_wrong["hours"] = df_wrong["hours"].astype("float64")

        # Drop NA
        df = df[~mask].dropna(subset=["start_time", "end_time"])

        # Create "hours"
        end_time = pd.to_datetime(df["end_time"], format="%H:%M:%S")
        start_time = pd.to_datetime(df["start_time"], format="%H:%M:%S")
        hours = end_time - start_time
        hours = hours.dt.total_seconds() / 3600
        df["hours"] = hours.round(2)

        # Recover wrong registers
        df = pd.concat([df, df_wrong])

        # Create "employee"
        df["employee"] = employee

        # Set index to search by controller
        df = df.sort_values(by=["date", "start_time"])
        df = df.reset_index(drop=True)

        return df

    def _validate(self, data: pd.DataFrame):
        """Separate valid and invalid subsets"""
        # Mask for a valid codex register
        date_is_datetime_not_na = (
            data["date"].apply(lambda x: isinstance(x, datetime.datetime))
            & ~data["date"].isna()
        )
        project_codex_growth = data["project"].str.lower().isin(["codex", "growth"])
        product_is_empty = data["product"].isna()
        hours_positive = data["hours"] > 0
        valid_codex_growth = (
            date_is_datetime_not_na
            & project_codex_growth
            & product_is_empty
            & hours_positive
        )

        # Mask for a valid project register
        date_is_datetime_not_na = (
            data["date"].apply(lambda x: isinstance(x, datetime.datetime))
            & ~data["date"].isna()
        )
        project_not_codex = data["project"].str.lower() != "codex"
        project_not_empty = ~data["project"].isna()
        project_is_string = data["project"].apply(lambda x: isinstance(x, str))
        product_not_empty = ~data["product"].isna()
        product_is_string = data["product"].apply(lambda x: isinstance(x, str))
        activity_not_empty = ~data["activity"].isna()
        activity_is_string = data["activity"].apply(lambda x: isinstance(x, str))
        activity_not_codex = ~data["activity"].fillna("dummy").str.contains("Codex")
        activity_not_growth = ~data["activity"].fillna("dummy").str.contains("Growth")
        hours_positive = data["hours"] > 0
        valid_project = (
            date_is_datetime_not_na
            & project_not_codex
            & project_not_empty
            & project_is_string
            & product_not_empty
            & product_is_string
            & activity_not_empty
            & activity_is_string
            & activity_not_codex
            & activity_not_growth
            & hours_positive
        )

        valid_mask = valid_codex_growth | valid_project
        valid = data[valid_mask].copy().reset_index(drop=True)
        invalid = data[~valid_mask].copy().reset_index(drop=True)
        return valid, invalid

    def _clean(self, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        # Drop registers when all is NA (mind you, empty hours are 0 hours)
        mask = (
            (data["date"].isna())
            & (data["product"].isna())
            & (data["project"].isna())
            & (data["hours"] == datetime.time(0, 0))
        )
        data = data[~mask].reset_index(drop=True)

        # CODEX "Reuniao interna" does not matter wherefrom
        data["activity"] = data["activity"].apply(
            lambda x: "Reunião interna" if "Reunião interna" in str(x) else x
        )

        # Validate business rules
        data, invalid = self._validate(data)

        # Remove time from date
        data["date"] = pd.to_datetime(data["date"]).apply(lambda x: x.date())

        return data, invalid

    def save_state(self):
        cache_folder = "app/cache"

        # Create
        os.makedirs(cache_folder, exist_ok=True)

        # Clean CTX from Office 365
        self.spHandler.ctx = None
        self.xlsx = None

        # Save as pickle
        with open(f"{cache_folder}/state.pickle", "wb") as f:
            pickle.dump(self, f)

            # For integration purposes
            self.data.valid.to_pickle(f"{cache_folder}/valid_data.pickle")

        # Save as .xlsx
        folder = "/mnt/c/SharedCache"
        if os.path.exists(folder):
            # Remove xlsx
            for file in os.listdir(folder):
                if file.endswith(".xlsx"):
                    os.remove(os.path.join(folder, file))
        yyyymmdd = datetime.datetime.now().strftime("%Y%m%d_%H%m%S")
        self.data.valid.to_excel(f"{folder}/{yyyymmdd}_valid.xlsx")
        self.data.invalid.to_excel(f"{folder}/{yyyymmdd}_invalid.xlsx")

    def get_dfs(self) -> None:
        """
        Get employee list and set the state
        """
        # Get employees
        sigla__pdIoExcelHandlers = self.getSpHandlers()

        # Filename
        filename_employees = {
            sigla: [
                sheet_name
                for sheet_name in workbook.sheet_names
                if sheet_name not in ["KEYS", "INÍCIO", "PowerQuery"]
            ]
            for sigla, workbook in sigla__pdIoExcelHandlers.items()
        }

        # Get [(sigla, name), ...]
        filename_employees = [
            (filename, employee)
            for filename, employees in filename_employees.items()
            for employee in employees
        ]
        total_iterations = len(filename_employees)

        # Get DataFrames
        ti = time.time()
        data = list()
        self.progress = 0
        for i, (filename, employee) in enumerate(filename_employees):
            df = self._get_df(sigla__pdIoExcelHandlers[filename], employee)
            if isinstance(df, pd.DataFrame):
                data.append(df.dropna(axis=1, how="all"))
            self.progress = int((i + 1) / total_iterations * 100)

        # Concatenate to single DataFrame
        data = pd.concat(data)

        # Validate and clean
        valid, invalid = self._clean(data)

        # Store in class
        self.data.valid = valid
        self.data.invalid = invalid

        self.employee_list = list(valid.employee.unique()) + list(invalid.employee.unique())
        self.employee_list.sort()

        # Print elapsed time
        tf = time.time()
        print("Elapsed time:", int(tf - ti), "s")

        # Save state
        self.save_state()


def decimal_to_time(decimal):
    if pd.isna(decimal):
        return None
    try:
        decimal = float(decimal)
        total_seconds = int(decimal * 24 * 3600)
        return (
            datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=total_seconds)
        ).time()
    except ValueError:
        return None
