from enum import Enum

class State(Enum):
  START = 0
  WAITING_FOR_EMAIL = 1
  WAITING_FOR_PASSWORD = 2
  LOGGED = 3
