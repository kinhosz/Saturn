import unittest
from algorithms import Treap

class TestTreap(unittest.TestCase):
  def setUp(self):
    self.treap = Treap()

  def add_elements(self):
    self.treap.add(5)
    self.assertEqual(self.treap.prefix(5), 1, "Should be 1")
    self.assertEqual(self.treap.getAllKeys(), [5], "expected: [5]")
    
    self.treap.add(6)
    self.assertEqual(self.treap.prefix(6), 2, "Should be 2. [5 6]")
    self.assertEqual(self.treap.getAllKeys(), [5, 6], "expected: [5, 6]")
    
    self.treap.add(1)
    self.assertEqual(self.treap.prefix(1), 1, "Should be 1. [1 5 6]")
    self.assertEqual(self.treap.getAllKeys(), [1, 5, 6], "expected: [1, 5, 6]")
    
    self.treap.add(2)
    self.assertEqual(self.treap.prefix(2), 2, "Should be 2. [1 2 5 6]")
    self.assertEqual(self.treap.getAllKeys(), [1, 2, 5, 6], "expected: [1, 2, 5, 6]")
    
    self.treap.remove(5)
    self.assertEqual(self.treap.getAllKeys(), [1, 2, 6], "expected: [1, 2, 6]")

    self.assertEqual(self.treap.prefix(1), 1, "Should be 1. [1 2 6]")
    self.assertEqual(self.treap.prefix(2), 2, "Should be 2. [1 2 6]")
    self.assertEqual(self.treap.prefix(4), 2, "Should be 2. [1 2 6]")
    self.assertEqual(self.treap.prefix(6), 3, "Should be 3. [1 2 6]")

  # repeats are necessary because treap isnt deterministic
  def test_add_elements_try1(self):
    self.add_elements()

  '''def test_add_elements_try2(self):
    self.add_elements()
  
  def test_add_elements_try3(self):
    self.add_elements()
  
  def test_add_elements_try4(self):
    self.add_elements()
  
  def test_add_elements_try5(self):
    self.add_elements()'''

  def tearDown(self):
    self.treap = None

if __name__ == "__main__":
  unittest.main()