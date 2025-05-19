import io
import os
import logging

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
        self.ctx = None

    def __auth__(self):
        ctx_auth = AuthenticationContext(self.url)
        if ctx_auth.acquire_token_for_user(self.username, self.password):
            ctx = ClientContext(self.url, ctx_auth)
            web = ctx.web
            ctx.load(web)
            ctx.execute_query()
            log.info("Web title: {0}".format(web.properties["Title"]))
        else:
            log.info(ctx_auth.get_last_error())

        self.ctx = ctx

    def get_excel_file(self, relative_url):
        # Get context if it does not exist
        if not self.ctx:
            self.__auth__()

        response = File.open_binary(self.ctx, relative_url)
        bytes_file_obj = io.BytesIO()
        bytes_file_obj.write(response.content)
        bytes_file_obj.seek(0)

        return pd.ExcelFile(bytes_file_obj, engine="openpyxl")
