import pickle
import os
import itertools
from time import time
import json

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
        print(" >>", colleague)
        # Get df
        df = pd.read_excel(file_name, sheet_name=colleague)

        # Drop na
        mask = (~df["Colaborador"].isna()) & (~df["Horas totais"].isna())
        df = df[mask]

        # Relevant for dash
        df_dash = df[["Data", "Projeto", "Produto", "Atividade", "Horas totais"]]
        df_dash.loc[:, "Horas totais"] = df_dash["Horas totais"].apply(
            lambda time: round(time.hour + time.minute / 60 + time.second / 3600, 2)
        )

        return df_dash

    def get_dfs(self) -> None:
        """
        Get colleague list and set the state
        """
        # Get colleagues
        self._get_colleagues()

        filename_colleagues = [(filename, colleague) for filename, colleagues in self.filename_colleagues.items() for colleague in colleagues ]
        total_iterations = len(filename_colleagues)
        # If not specified, use all colleagues
        ti = time()
        data = dict()
        for i, (filename, colleague) in enumerate(filename_colleagues):
            data[colleague] = self._get_df(filename, colleague) 

        self.data = data
        tf = time()
        print("Elapsed time:", int(tf - ti), "s")
        self.colleague_list = list(self.data.keys())

        self.product_project_list = {
            colleague: df[["Produto", "Projeto"]].drop_duplicates()
            for colleague, df in self.data.items()
        }

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
