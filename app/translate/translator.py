import os
import pandas as pd
from dotenv import load_dotenv


load_dotenv()

class Translator:
    def __init__(self, language: str):
        # Save language
        self.language = language

        # Load translations
        df = pd.read_csv(
            "app/translate/translations.csv",
            usecols=["ENGLISH", self.language])
        self.translations: pd.DataFrame = df.set_index("ENGLISH")

    def translate(self, text: str) -> str:
        if self.language == "ENGLISH":
            return text
        else:
            return self.translations.loc[text, self.language]

target_language = os.getenv("LANGUAGE", "ENGLISH")
translator = Translator(target_language)
