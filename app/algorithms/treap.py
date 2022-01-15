from datetime import datetime
import random

# a reference to Node (like C pointers)
class pNode(object):
  def __init__(self, node):
    self._node = node

  @property
  def node(self):
    return self._node

  @node.setter
  def node(self, node):
    self._node = node

# the node class
class Node(object):
  def __init__(self, key, value):
    self.key = key
    self.prior = random.random()
    self.value = value
    self.size = 1
    self._pl = pNode(None)
    self._pr = pNode(None)

  @property
  def pl(self):
    return self._pl
  
  @property
  def pr(self):
    return self._pr

  @pl.setter
  def pl(self, node):
    self._pl.node = node
  
  @pr.setter
  def pr(self, node):
    self._pr.node = node

class Treap(object):
  def __init__(self):
    self.__root = pNode(None)

  def __split(self, p, key, pl, pr):
    if p.node == None:
      pl.node = None
      pr.node = None
    elif p.node.key <= key:
      pl.node = p.node
      self.__split(p.node.pr, key, p.node.pr, pr)
    else:
      pr.node = p.node
      self.__split(p.node.pl, key, pl, p.node.pl)

    self.__update(p)

  def __insert(self, p, item):
    if p.node == None:
      p.node = item
    elif item.prior > p.node.prior:
      self.__split(p, item.key, item.pl, item.pr)
      p.node = item
    elif p.node.key <= item.key:
      self.__insert(p.node.pr, item)
    else:
      self.__insert(p.node.pl, item)
    
    self.__update(p)
  
  def __merge(self, p, pl, pr):
    if pl.node == None or pr.node == None:
      p.node = (pl.node if pl.node else pr.node)
    elif (pl.node.prior > pr.node.prior):
      self.__merge(pl.node.pr, pl.node.pr, pr)
      p.node = pl.node
    else:
      self.__merge(pr.node.pl, pl, pr.node.pl)
      p.node = pr.node

    self.__update(p)

  def __erase(self, p, key):
    t = p.node

    if t == None:
      return None 

    if t.key == key:
      self.__merge(p, t.pl, t.pr)
    elif t.key < key:
      self.__erase(t.pr, key)
    else:
      self.__erase(t.pl, key)

    self.__update(p)

  def __getValue(self, p):
    if p.node == None:
      return None

    return p.node.value

  def __getSize(self, p):
    if p.node == None:
      return 0

    return p.node.size

  def __update(self, p):
    if p.node == None:
      return None

    p.node.size = 1
    p.node.size += self.__getSize(p.node.pl)
    p.node.size += self.__getSize(p.node.pr)

  def __prefix(self, p, key):
    if p.node == None:
      return 0

    t = p.node

    if t.key <= key:
      return self.__getSize(t.pl) + self.__prefix(t.pr, key) + 1
    else:
      return self.__prefix(t.pl, key)

  # public methods

  def add(self, key):
    i = Node(key, key)
    self.__insert(self.__root, i)

  def remove(self, key):
    self.__erase(self.__root, key)

  def prefix(self, key):
    return self.__prefix(self.__root, key)

  def getAllKeys(self, t=None, firstCall=True):
    if firstCall:
      t = self.__root

    if t.node == None:
      return []

    ls = []
    ls = ls + self.getAllKeys(t.node.pl, False)
    ls.append(t.node.key)
    ls = ls + self.getAllKeys(t.node.pr, False)

    return ls
