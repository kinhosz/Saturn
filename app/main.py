import asyncio
from dotenv import load_dotenv
from app import render

def main():
  load_dotenv()
  
  asyncio.run(render())  

if __name__ == "__main__":
  main()