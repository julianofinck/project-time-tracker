import io
import logging
import os

import pandas as pd
from dotenv import load_dotenv
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.files.file import File

load_dotenv()


log = logging.getLogger(__name__)


class SharepointHandler:
    def __init__(self):
        self.url = os.getenv("SHAREPOINT_URL")
        self.username = os.getenv("SHAREPOINT_USER")
        self.password = os.getenv("SHAREPOINT_PASSWORD")
        self.client_context = None

    def __auth__(self):
        try:
            client_context_auth = AuthenticationContext(self.url)
            if not client_context_auth.acquire_token_for_user(
                self.username, self.password
            ):
                log.exception(
                    f"Authentication failed: {client_context_auth.get_last_error()}"
                )

            client_context = ClientContext(self.url, client_context_auth)

            # Get the current user
            current_user = client_context.web.current_user
            client_context.load(current_user)
            client_context.execute_query()

            web = client_context.web
            user = client_context.web.current_user

            client_context.load(web, ["Title"])
            client_context.load(user)
            client_context.execute_query()

            log.info(
                f"Accessed SharePoint site: '{web.properties['Title']}' at {self.url}"
            )
            log.info(
                f"Logged in as '{user.properties['Title']}' ({user.properties['LoginName']})"
            )

        except Exception as e:
            print(e)
            log.exception(
                f"Authentication failed: {client_context_auth.get_last_error()}"
            )
            raise RuntimeError("Auth error!")

        self.client_context = client_context

    def get_excel_file(self, relative_url):
        # Get context if it does not exist
        if not self.client_context:
            self.__auth__()

        response = File.open_binary(self.client_context, relative_url)
        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)

        return pd.ExcelFile(bytes_file_obj, engine="openpyxl")
