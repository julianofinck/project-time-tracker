import logging
import sys
from pathlib import Path

# Make sure app/ is importable
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from src.app.main import app

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=8050)
    except Exception:
        logger.exception("Erro ao rodar o servidor de densenvolvimento!")
        raise
