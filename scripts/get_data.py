import numpy as np
import pandas as pd


class Extractor:
    def __init__(self, xlsx):
        self.xlsx = xlsx
        self.colleagues = None
        self.data = None

    def get_colleagues(self) -> list[str]:
        # Get the name of all sheets in the Excel file
        excel = pd.ExcelFile(self.xlsx)
        sheet_names = excel.sheet_names

        for name in ["KEYS", "INÍCIO", "PowerQuery"]:
            sheet_names.remove(name)

        self.colleagues = sheet_names
        return sheet_names

    def get_dfs(self, colleagues=None) -> dict[str : pd.DataFrame]:
        # Get colleagues
        if colleagues is None:
            if self.colleagues is None:
                self.get_colleagues()
        else:
            self.colleagues = colleagues

        dfs = {colleague: self.get_df(colleague) for colleague in self.colleagues}

        return dfs

    def _define_name(self, row):
        # Deprecated
        if str(row.Produto) == "nan":
            return f"{row.Projeto}\n{row.Atividade}"
        else:
            return f"{row.Projeto}\n{row.Produto}"

    def get_df(self, colleague: str) -> pd.DataFrame:
        print(" >>", colleague)
        # Get df
        df = pd.read_excel(self.xlsx, sheet_name=colleague)

        # Drop na
        mask = (~df["Colaborador"].isna()) & (~df["Horas totais"].isna())
        df = df[mask]

        # Relevant for dash
        df_dash = df[["Data", "Projeto", "Produto", "Atividade", "Horas totais"]]
        df_dash.loc[:, "Horas totais"] = df_dash["Horas totais"].apply(
            lambda time: round(time.hour + time.minute / 60 + time.second / 3600, 2)
        )

        return df_dash
