from pydantic_settings  import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

# Now you can access:
MONGO_URI = f"mongodb://{os.getenv('MONGO_USERNAME')}:" \
            f"{os.getenv('MONGO_PASSWORD')}@" \
            f"{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}"
MONGO_DB = os.getenv("MONGO_DATABASE")
