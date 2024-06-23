import pickle
import os
import itertools
import time
import json
import datetime

import numpy as np
import pandas as pd


class Extractor:
    def __init__(self):
        # Define paths to XLSX files
        paths = {
            "AF": os.getenv("XLSX_AF"),
            "GK": os.getenv("XLSX_GK"),
            "LP": os.getenv("XLSX_LP"),
            "RZ": os.getenv("XLSX_RZ"),
        }
        apontamentos_dir = os.getenv("APONTAMENTOS_DIR")
        self.xlsx = {k: f"{apontamentos_dir}{v}" for k, v in paths.items()}

        self.colleague_list = None
        self.filename_colleagues = None
        self.data = None
        self.product_project_list = None

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
                    
                    
    def _get_colleagues(self) -> list[str]:
        # Get the name of colleagues
        filename_colleagues = {
            xlsx: [
                sheet
                for sheet in pd.ExcelFile(xlsx).sheet_names
                if sheet not in ["KEYS", "INÍCIO", "PowerQuery"]
            ]
            for xlsx in self.xlsx.values()
        }

        # If config is defined, use it
        try:
            with open('config.json') as f:
                config = json.load(f)
                colleague_list_json = config.get('colleague_list', None)
                if not isinstance(colleague_list_json, list):
                    # TODO: Add log
                    print(TypeError("colleague_list must be a list"))
                elif None in colleague_list_json:
                    # TODO: Add log
                    pass
                else:
                    self.colleague_list = colleague_list_json
        except FileNotFoundError:
            # TODO: log "no config file"
            pass

        # If colleagues_list is invalid, use all colleagues
        self.filename_colleagues = filename_colleagues
        self._filter_desired()
        

    def _get_df(self, file_name: str, colleague: str) -> pd.DataFrame:
        # Log colleague
        print(" >>", colleague)

        # Get df
        columns = ["Data", "Projeto", "Produto", "Atividade", "Horas totais"]
        df = pd.read_excel(file_name, colleague, usecols=columns)

        # Columns in lowercase
        df.columns = ["date", "project", "product", "activity", "hours"]

        # Set colleague name
        df["colleague"] = colleague

        return df

    def get_dfs(self) -> None:
        """
        Get colleague list and set the state
        """
        # Get colleagues
        self._get_colleagues()

        filename_colleagues = [(filename, colleague) for filename, colleagues in self.filename_colleagues.items() for colleague in colleagues]
        total_iterations = len(filename_colleagues)

        # Get DataFrames
        ti = time.time()
        data = [self._get_df(filename, colleague) for filename, colleague in filename_colleagues]

        # Concatenate to single DataFrame
        data = pd.concat(data).reset_index(drop=True)

        # Validate and clean
        data, invalid = self._clean(data)

        # Store in class
        self.data = data
        self.invalid = invalid

        # Print elapsed time
        tf = time.time()
        print("Elapsed time:", int(tf - ti), "s")

        # Save state
        extractor._save_state()

    def _validate(self, data: pd.DataFrame):
        """Separate valid and invalid subsets"""
        # Mask for a valid codex register
        date_not_empty = ~data["date"].isna()
        project_codex = data["project"].str.lower() == "codex"
        product_is_empty = data["product"].isna()
        activity_codex = data["activity"].fillna("dummy").str.contains("Codex")
        hours_not_null = data["hours"] != 0
        valid_codex = date_not_empty & \
            project_codex & \
            product_is_empty & \
            activity_codex & \
            hours_not_null

        # Mask for a valid project register
        # TODO: extend validation to check if product is allowed under given project
        date_not_empty = ~data["date"].isna()
        project_not_codex = data["project"].str.lower() != "codex"
        project_not_empty = ~data["project"].isna()
        project_is_string = data["project"].apply(lambda x: isinstance(x, str))
        product_not_empty = ~data["product"].isna()
        product_is_string = data["product"].apply(lambda x: isinstance(x, str))
        activity_not_empty = ~data["activity"].isna()
        activity_is_string = data["activity"].apply(lambda x: isinstance(x, str))
        activity_not_codex = ~data["activity"].fillna("dummy").str.contains("Codex")
        hours_not_null = data["hours"] != 0
        valid_project = date_not_empty & \
            project_not_codex & \
            project_not_empty & \
            project_is_string & \
            product_not_empty & \
            product_is_string & \
            activity_not_empty & \
            activity_is_string & \
            activity_not_codex & \
            hours_not_null
        
        valid_mask = valid_codex | valid_project
        valid = data[valid_mask].copy().reset_index(drop=True)
        invalid = data[~valid_mask].copy().reset_index(drop=True)
        return valid, invalid

    def _clean(self, data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        # Drop registers when all is NA (mind you, empty hours are 0 hours)
        mask = (data["date"].isna()) & \
            (data["product"].isna()) & \
            (data["project"].isna()) & \
            (data["hours"] == datetime.time(0, 0))
        data = data[~mask].reset_index(drop=True)

        # Convert to hour
        # TODO: what if the element is a string?
        data.loc[:, "hours"] = data["hours"].apply(
            lambda time: round(time.hour + time.minute / 60 + time.second / 3600, 2)
            if pd.notnull(time) else np.nan
        )

        # Validate business rules
        data, invalid = self._validate(data)
        
        # Remove time from date
        data["date"] = pd.to_datetime(data["date"]).apply(lambda x: x.date())

        return data, invalid

    def _define_name(self, row):
        # Deprecated
        if str(row.Produto) == "nan":
            return f"{row.Projeto}\n{row.Atividade}"
        else:
            return f"{row.Projeto}\n{row.Produto}"

    def _save_state(self):
        # Save the extractor
        if not os.path.exists("app/cache"):
            os.makedirs("app/cache")

        with open("app/cache/state.pickle", "wb") as f:
            pickle.dump(extractor, f)



# Load the extractor if it exists in cache
if os.path.exists("app/cache/state.pickle"):
    with open("app/cache/state.pickle", "rb") as f:
        extractor = pickle.load(f)
else:
    extractor = Extractor()
    extractor.get_dfs()
    extractor._save_state()
