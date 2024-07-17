from dotenv import load_dotenv
from app import app


# Load environment variables
load_dotenv()

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)  # , debug=True)
