import unittest
from algorithms import Treap

class TestTreap(unittest.TestCase):
  def setUp(self):
    self.treap = Treap()

  def add_elements_for_test_sort(self):
    self.treap.add(5)
    self.assertEqual(self.treap.getAllKeys(), [5])
    self.assertEqual(self.treap.prefix(5), 1)
    
    self.treap.add(6)
    self.assertEqual(self.treap.getAllKeys(), [5, 6])
    self.assertEqual(self.treap.prefix(6), 2)
    
    self.treap.add(1)
    self.assertEqual(self.treap.getAllKeys(), [1, 5, 6])
    self.assertEqual(self.treap.prefix(5), 2)
    self.assertEqual(self.treap.prefix(6), 3)
    
    self.treap.add(2)
    self.assertEqual(self.treap.getAllKeys(), [1, 2, 5, 6])
    self.assertEqual(self.treap.prefix(6), 4)
    
    self.treap.remove(5)
    self.assertEqual(self.treap.getAllKeys(), [1, 2, 6])
    self.assertEqual(self.treap.prefix(5), 2)
    self.assertEqual(self.treap.prefix(6), 3)

    self.treap.add(8)
    self.assertEqual(self.treap.getAllKeys(), [1, 2, 6, 8])
    self.assertEqual(self.treap.prefix(8), 4)

    self.treap.remove(2)
    self.assertEqual(self.treap.getAllKeys(), [1, 6, 8])
    self.assertEqual(self.treap.prefix(9), 3)

    self.treap.add(-4)
    self.assertEqual(self.treap.getAllKeys(), [-4, 1, 6, 8])
    self.assertEqual(self.treap.prefix(7), 3)
    
    self.treap.add(6)
    self.assertEqual(self.treap.getAllKeys(), [-4, 1, 6, 6, 8])
    self.assertEqual(self.treap.prefix(6), 4)

    self.treap.add(9)
    self.assertEqual(self.treap.getAllKeys(), [-4, 1, 6, 6, 8, 9])
    self.assertEqual(self.treap.prefix(9), 6)

    self.treap.add(12)
    self.assertEqual(self.treap.getAllKeys(), [-4, 1, 6, 6, 8, 9, 12])
    self.assertEqual(self.treap.prefix(12), 7)

    self.treap.remove(6)
    self.assertEqual(self.treap.getAllKeys(), [-4, 1, 6, 8, 9, 12])
    self.assertEqual(self.treap.prefix(12), 6)

    self.treap.add(7)
    self.assertEqual(self.treap.getAllKeys(), [-4, 1, 6, 7, 8, 9, 12])
    self.assertEqual(self.treap.prefix(12), 7)

  # 5 attempts for random reasons
  def test_sort_try1(self):
    self.add_elements_for_test_sort()

  def test_sort_try2(self):
    self.add_elements_for_test_sort()
  
  def test_sort_try3(self):
    self.add_elements_for_test_sort()
  
  def test_sort_try4(self):
    self.add_elements_for_test_sort()
  
  def test_sort_try5(self):
    self.add_elements_for_test_sort()

  def tearDown(self):
    self.treap = None

if __name__ == "__main__":
  unittest.main()