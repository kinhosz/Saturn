import unittest
from app.algorithms import Queue

class TestQueue(unittest.TestCase):
  def setUp(self):
    self.queue = Queue()

  def test_add_elements(self):
    self.queue.push(3)
    self.queue.push(4)
    self.queue.push(5)
    self.queue.push(6)

    self.assertEqual(self.queue.front(), 3, "Should be 3")
    self.queue.pop()
    self.assertEqual(self.queue.front(), 4, "Should be 4")
    self.assertEqual(self.queue.size(), 3, "queue.size() should be 3")
    self.queue.pop()
    self.queue.pop()
    self.queue.pop()
    with self.assertRaises(Exception):
      self.queue.pop()
    
    self.assertEqual(self.queue.front(), None, "Should be None")

  def tearDown(self):
    self.queue = None

if __name__ == "__main__":
  unittest.main()