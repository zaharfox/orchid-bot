import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "7981471983:AAHYm03vmirzqpQfMq7fQDZVHbpy1fVnfKc")
DATABASE_URL = os.getenv("DATABASE_URL", "orchids.db")
