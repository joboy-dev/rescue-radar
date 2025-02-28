import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(module)s:%(funcName)s:%(lineno)d: %(message)s",
    handlers=[
        logging.FileHandler("logs/app_logs.log"),
        logging.StreamHandler(),
    ],
)

# Create a logger for the application
app_logger = logging.getLogger("app")  # Use a specific logger name for your application

# Get the logger for the problematic module
problematic_logger = logging.getLogger("main")
problematic_logger.setLevel(logging.INFO)  # Suppress INFO-level logs