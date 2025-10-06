import logging

class VBLogger:
    def __init__(self, id, log_filename=None):
        """Initialize the logger with a specific log file."""
        if log_filename is None:
            self.log_filename = f"vb_{id}.log"
        else:
            self.log_filename = log_filename
        
        logging.basicConfig(
            filename=self.log_filename,
            level=logging.DEBUG,  # Set to DEBUG to catch all logs
            format="%(asctime)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(f"VerbalBehaviours_id")
        self.logger.setLevel(logging.DEBUG)  # Ensure the logger level is set

    def log_info(self, message):
        """Log an informational message."""
        self.logger.info(message)

    def log_error(self, message):
        """Log an error message."""
        self.logger.error(message)

    def log_json(self, action, data):
        """Log a JSON message"""
        message = f"{action} - {data}"
        self.logger.info(message)

    def log_exception(self, message, exc):
        """Log exceptions with a custom message."""
        self.logger.exception(f"{message}: {exc}")

def init_logger(id, log_filename):
    return VBLogger(id, log_filename)
