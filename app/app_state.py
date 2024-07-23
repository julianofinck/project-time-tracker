import datetime
import itertools
import json
import os
import pickle
import time
from dataclasses import dataclass, field

import numpy as np
import pandas as pd


class AppState:
    def __init__(self):
        paths = {
            "AF": os.getenv("XLSX_AF"),
            "GK": os.getenv("XLSX_GK"),
            "LP": os.getenv("XLSX_LP"),
            "RZ": os.getenv("XLSX_RZ"),
        }
        apontamentos_dir = os.getenv("APONTAMENTOS_DIR")
        self.xlsx = {
            initials: os.path.join(apontamentos_dir, xlsx_filepath)
            for initials, xlsx_filepath in paths.items()
        }
        self.colleague_list = None
        self.filename_colleagues = None
        self.data = Data()

        self.progress = 0

    def _filter_desired(self):
        if self.colleague_list is not None:
            state = self.filename_colleagues.copy()
            for k, vs in state.items():
                if any([colleague in vs for colleague in self.colleague_list]):
                    for v in vs.copy():
                        if v not in self.colleague_list:
                            self.filename_colleagues[k].remove(v)
                else:
                    del self.filename_colleagues[k]

    def get_colleagues(self) -> list[str]:
        filename_colleagues = {
            xlsx: [
                sheet
                for sheet in pd.ExcelFile(xlsx).sheet_names
                if sheet not in ["KEYS", "INÍCIO", "PowerQuery"]
            ]
            for xlsx in self.xlsx.values()
        }

        self.filename_colleagues = filename_colleagues
        self.colleague_list = [
            colleague
            for colleagues in self.filename_colleagues.values()
            for colleague in colleagues
        ]
        self._filter_desired()

    def _get_df(self, file_name: str, colleague: str) -> pd.DataFrame:
        # Log colleague
        print(" >>", colleague)
        if colleague == "Juliano":
            pass

        # Read Excel sheetname of the specific Colleague
        first_columns = ["Data", "Projeto", "Produto", "Atividade"]
        columns = first_columns + [
            "Horário 1 - Inicio", "Horário 1 - fim",
            "Horário 2 - Inicio", "Horário 2 - fim",
            "Horário 3 - Inicio", "Horário 3 - fim",
            "Horário 4 - Inicio", "Horário 4 - fim",
        ]
        # Try read. If it fails, remove name from AppState, warn error, return "None"
        df = pd.read_excel(file_name, colleague, usecols=columns)

        # Workaround for empty dataframes (when people add news sheets inadvertently)
        if df.columns.empty:
            self.colleague_list.remove(colleague)
            self.filename_colleagues[file_name].remove(colleague)
            print(
                f" WARNING: '{colleague}' has no data. Warning: REMOVED from data importer."
            )
            return None

        # Keep row number
        df["index"] = df.index + 2

        # Explode activity in its block hours (explode 1:N relationships)
        lista = []
        for i in range(1, 5):
            workhour_block = df[
                first_columns + [f"Horário {i} - Inicio", f"Horário {i} - fim", "index"]
            ].copy()
            workhour_block.columns = first_columns + [
                "Horário - Inicio",
                "Horário - fim",
                "index",
            ]
            lista.append(workhour_block)
        df = pd.concat(lista, axis=0, ignore_index=True)

        # Drop rows with empty values
        all_columns_null = df[[c for c in df.columns if c != "index"]].isna().all(axis=1)
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
            "index",
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
        mask_not_all_na = ((df.start_time.isna()) | (df.start_time.isna())) & (~df.drop(columns=["index"]).isna().all(axis=1)) & (df.date.isna())
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

        # Create "colleague"
        df["colleague"] = colleague

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
        hours_not_null = data["hours"] > 0
        valid_codex_growth = (
            date_is_datetime_not_na
            & project_codex_growth
            & product_is_empty
            & hours_not_null
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
        hours_not_null = data["hours"] > 0
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
            & hours_not_null
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
        # Create
        os.makedirs("app/cache", exist_ok=True)

        with open("app/cache/state.pickle", "wb") as f:
            pickle.dump(self, f)

            # For integration purposes
            self.data.valid.to_pickle("app/cache/valid_data.pickle")

    def get_dfs(self) -> None:
        """
        Get colleague list and set the state
        """
        # Get colleagues
        self.get_colleagues()

        filename_colleagues = [
            (filename, colleague)
            for filename, colleagues in self.filename_colleagues.items()
            for colleague in colleagues
        ]
        total_iterations = len(filename_colleagues)

        # Get DataFrames
        ti = time.time()
        data = list()
        self.progress = 0
        for i, (filename, colleague) in enumerate(filename_colleagues):
            df = self._get_df(filename, colleague)
            if isinstance(df, pd.DataFrame):
                data.append(df.dropna(axis=1, how="all"))
            self.progress = (i + 1) / total_iterations * 100

        # Concatenate to single DataFrame
        data = pd.concat(data)

        # Validate and clean
        data, invalid = self._clean(data)

        # Store in class
        self.data.valid = data
        self.data.invalid = invalid

        # Print elapsed time
        tf = time.time()
        print("Elapsed time:", int(tf - ti), "s")

        # Save state
        self.save_state()


@dataclass
class Data:
    valid: pd.DataFrame = field(default_factory=pd.DataFrame)
    invalid: pd.DataFrame = field(default_factory=pd.DataFrame)


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




str