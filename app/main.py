import asyncio
from dotenv import load_dotenv
from app import render, db_config, set_env

def main():
  load_dotenv()
  
  db_config()

  asyncio.run(render())  

if __name__ == "__main__":
  set_env()
  main()
