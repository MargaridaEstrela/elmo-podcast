import logging


class EmoShowLogger:
    """
    A class representing the logger class for the Emo-Show game.

    Attributes:
        log_file (str): The name of the log file.
        logger (object): The logger object.

    Methods:
        set_window(window): Connects the interface with the logger.
        set_filename(filename): Sets the filename of the log file.
        log_message(message): Logs a debug message with the provided message.
        log_error(message): Logs an error message with the provided message.
        close(): Closes the file handler and shuts down the logging system.
    """

    def __init__(self, log_file="logs/emoshow.log"):
        self.log_file = log_file
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def set_window(self, window):
        """
        Connects the interface with the logger.

        Args:
            window (object): The window object.
        """
        self.window = window

    def set_filename(self, filename):
        """
        Sets the filename of the log file.

        Args:
            filename (str): The name of the log file.
        """
        self.log_file = f"logs/{filename}"
        self.handler.close()
        self.handler = logging.FileHandler(self.log_file)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def log_message(self, message):
        """
        Logs a debug message with the provided message.

        Args:
            message (str): The message to be logged.
        """
        try:
            self.logger.info(f"{message}")
            # print(message)
        except Exception as e:
            self.logger.error(f"Error logging message: {e}")

    def log_error(self, message):
        """
        Logs an error message with the provided message.

        Args:
            message (str): The error message to be logged.
        """
        try:
            self.logger.error(f"{message}")
        except Exception as e:
            self.logger.error(f"Error logging error message: {e}")

    def close(self):
        """
        Closes the file handler and shuts down the logging system.
        """
        self.handler.close()
        logging.shutdown()
