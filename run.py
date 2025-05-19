import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import app

log = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        app.run_server(host="0.0.0.0", port=8050)
    except Exception:
        log.exception("Erro!")
