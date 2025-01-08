from telegram import Update
from dotenv import load_dotenv
import os

load_dotenv()
ADMIN_ID = os.getenv('ADMIN_ID')

def is_admin(update: Update) -> bool:
    return str(update.message.from_user.id) == str(ADMIN_ID)
