# src/utils/logger.py
import logging
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from functools import wraps
from typing import Callable, Any

class MafiaLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MafiaLogger, cls).__new__(cls)
            cls._instance._initialize_logger()
        return cls._instance

    def _initialize_logger(self):
        """Initialize the logger only once."""
        self.logger = logging.getLogger("mafia_bot")
        
        # Only add handlers if they haven't been added yet
        if not self.logger.handlers:
            # Create logs directory if it doesn't exist
            logs_dir = "logs"
            os.makedirs(logs_dir, exist_ok=True)
            
            # Set up file handler
            file_handler = logging.FileHandler(os.path.join(logs_dir, "bot.log"))
            file_handler.setLevel(logging.INFO)
            
            # Set up console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # Create formatter and add it to the handlers
            log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(log_format)
            console_handler.setFormatter(log_format)
            
            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)

            # Suppress third-party library logs
            for noisy_logger in ["telegram", "telegram.ext", "urllib3", "requests", "httpx", "httpcore"]:
                logging.getLogger(noisy_logger).setLevel(logging.WARNING)

    def log_command(self, update: Update, command: str, args: str = None) -> None:
        """Log command usage with username and arguments."""
        username = update.effective_user.username or update.effective_user.id
        if args:
            self.logger.info(f"User [{username}] called command [{command}] with args [{args}]")
        else:
            self.logger.info(f"User [{username}] called command [{command}]")

    def log_callback(self, update: Update, callback_data: str) -> None:
        """Log callback query with username."""
        username = update.effective_user.username or update.effective_user.id
        self.logger.info(f"User [{username}] triggered callback [{callback_data}]")

    def log_action(self, update: Update, action: str) -> None:
        """Log general user actions."""
        username = update.effective_user.username or update.effective_user.id
        self.logger.info(f"User [{username}] performed action [{action}]")

    def log_error(self, update: Update, error: str) -> None:
        """Log errors with username context."""
        username = update.effective_user.username or update.effective_user.id
        self.logger.error(f"Error for user [{username}]: {error}")

    def info(self, message: str) -> None:
        """Log general info message."""
        self.logger.info(message)

    def error(self, message: str) -> None:
        """Log general error message."""
        self.logger.error(message)

    def warning(self, message: str) -> None:
        """Log general warning message."""
        self.logger.warning(message)

def log_command_usage(command_name: str) -> Callable:
    """Decorator to log command usage."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args: Any, **kwargs: Any) -> Any:
            # Get command arguments if they exist
            args_text = " ".join(context.args) if context.args else None
            MafiaLogger().log_command(update, command_name, args_text)
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
