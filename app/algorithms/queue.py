class Node(object):
  def __init__(self, value):
    self.value = value
    self.next = None

class Queue(object):
  def __init__(self):
    self.__tail = None
    self.__head = None
    self.__size = 0

  def push(self, value):
    node = Node(value)
    self.__size += 1

    if self.__size == 1:
      self.__tail = node
      self.__head = node
    else:
      self.__tail.next = node
      self.__tail = node
  
  def pop(self):
    if self.__size > 0:
      self.__head = self.__head.next
      self.__size -= 1
    else:
      raise Exception("Cannot pop an empty queue")
  
  def front(self):
    if self.__size == 0:
      return None
    else:
      return self.__head.value

  def size(self):
    return self.__size