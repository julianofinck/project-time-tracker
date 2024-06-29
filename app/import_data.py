import datetime
import itertools
import json
import os
import pickle
import time

import numpy as np
import pandas as pd


class DataImporter:
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
        self.data = None
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
        self._filter_desired()

    def _get_df(self, file_name: str, colleague: str) -> pd.DataFrame:
        # Log colleague
        print(" >>", colleague)
        if colleague == "Nicholas Becker":
            pass

        # Get df
        columns = ["Data", "Projeto", "Produto", "Atividade", "Horas totais"]
        df = pd.read_excel(file_name, colleague, usecols=columns)

        # Columns in lowercase
        df.columns = ["date", "project", "product", "activity", "hours"]

        # Set colleague name
        df["colleague"] = colleague

        # Set index to search by controller
        df.index = df.index + 2

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
        hours_not_null = data["hours"] != 0
        valid_codex_growth = (
            date_is_datetime_not_na
            & project_codex_growth
            & product_is_empty
            & hours_not_null
        )

        # Mask for a valid project register
        # TODO: extend validation to check if product is allowed under given project
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
        hours_not_null = data["hours"] != 0
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

        # Convert to hour
        # TODO: what if the element is a string?
        data.loc[:, "hours"] = data["hours"].apply(
            lambda time: (
                round(time.hour + time.minute / 60 + time.second / 3600, 2)
                if pd.notnull(time)
                else np.nan
            )
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
            self.data.to_pickle("app/cache/data.pickle")

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
        # data = [self._get_df(filename, colleague) for filename, colleague in filename_colleagues]
        data = list()
        self.progress = 0
        for i, (filename, colleague) in enumerate(filename_colleagues):
            df = self._get_df(filename, colleague)
            data.append(df.dropna(axis=1, how="all"))
            self.progress = (i + 1) / total_iterations * 100

        # Concatenate to single DataFrame
        data = pd.concat(data).reset_index()
        # The behavior of DataFrame concatenation with empty or all-NA entries is deprecated. In a future version, this will no longer exclude empty or all-NA columns when determining the result dtypes. To retain the old behavior, exclude the relevant entries before the concat operation.

        # Validate and clean
        data, invalid = self._clean(data)

        # Store in class
        self.data = data
        self.invalid = invalid

        # Print elapsed time
        tf = time.time()
        print("Elapsed time:", int(tf - ti), "s")

        # Save state
        self.save_state()
