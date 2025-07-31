import asyncio
from dotenv import load_dotenv
from app import render, db_config, set_env

import logging
from colorlog import ColoredFormatter

handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    }
)
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def main():
  load_dotenv()
  
  db_config()

  asyncio.run(render())  

if __name__ == "__main__":
  set_env()
  main()
