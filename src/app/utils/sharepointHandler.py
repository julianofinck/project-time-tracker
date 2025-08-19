import io
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

# Azure Device Code Credentials

load_dotenv()


log = logging.getLogger(__name__)


class SharepointHandler:
    def __init__(self):
        self.url = os.getenv("SHAREPOINT_URL")
        self.username = os.getenv("SHAREPOINT_USER")
        self.password = os.getenv("SHAREPOINT_PASSWORD")
        self.client_id = os.getenv("SHAREPOINT_CLIENT_ID")
        self.client_secret = os.getenv("SHAREPOINT_CLIENT_SECRET")
        self.client_context = None

    def __auth__(self):
        try:
            # Metodo antigo
            metodo = "user_credential"

            if metodo == "antigo":
                client_context_auth = AuthenticationContext(self.url)
                if not client_context_auth.acquire_token_for_user(
                    self.username, self.password
                ):
                    log.exception(
                        f"Authentication failed: {client_context_auth.get_last_error()}"
                    )

                ctx = ClientContext(self.url, client_context_auth)

            elif metodo == "user_credential":
                ctx = ClientContext(self.url).with_credentials(UserCredential(self.username, self.password))
                with open("aqui.xlsx", "wb") as f:
                    file = ctx.web.get_file_by_server_relative_url("/sites/Codex-Operao/general/A_ao_F_APONTAMENTOS_OPE_2023.xlsx")
                    file.download(f).execute_query()

                web = ctx.web.get().execute_query()
                print(web.url)

            elif metodo == "azure_ad":
                ctx = ClientContext(self.url).with_client_credentials(self.client_id, self.client_secret)
                web = ctx.web.get().execute_query()
                print(web.url)

            # Get the current user
            current_user = ctx.web.current_user
            ctx.load(current_user)
            ctx.execute_query()

            web = ctx.web
            user = ctx.web.current_user

            ctx.load(web, ["Title"])
            ctx.load(user)
            ctx.execute_query()

            log.info(
                f"Accessed SharePoint site: '{web.properties['Title']}' at {self.url}"
            )
            log.info(
                f"Logged in as '{user.properties['Title']}' ({user.properties['LoginName']})"
            )

        except Exception:
            log.exception("Authentication failed")
            raise RuntimeError("Auth error!")

        self.client_context = ctx

    def get_excel_file(self, relative_url):
        # Get context if it does not exist
        if not self.client_context:
            self.__auth__()

        response = File.open_binary(self.client_context, relative_url)
        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)

        return pd.ExcelFile(bytes_file_obj, engine="openpyxl")
