from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app import app


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)
