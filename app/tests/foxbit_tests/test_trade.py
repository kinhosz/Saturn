import unittest
from foxbit import Trade

class TestTrade(unittest.TestCase):
  def setUp(self):
    self.trade = Trade(historyLimit=5, valleyPercent=0.2, profit=0.1)
  
  def add_prices(self):
    # fill the trade
    self.assertFalse(self.trade.addPrice(5), "Should be False. [5]")
    self.assertFalse(self.trade.addPrice(6), "Should be False. [5, 6]")
    self.assertFalse(self.trade.addPrice(3), "Should be False. [5, 6, 3]")
    self.assertFalse(self.trade.addPrice(7), "Should be False. [5, 6, 3, 7]")
    self.assertFalse(self.trade.addPrice(9), "Should be False. [5, 6, 3, 7, 9]")

    self.assertFalse(self.trade.addPrice(4), "Should be false. [6, 3, 7, 9, 4]")
    self.assertTrue(self.trade.addPrice(2), "Should be True. [3, 7, 9, 4, 2]")

  def test_add_prices_try1(self):
    self.add_prices()

  def test_add_prices_try2(self):
    self.add_prices()
  
  def test_add_prices_try3(self):
    self.add_prices()
  
  def test_add_prices_try4(self):
    self.add_prices()
  
  def test_add_prices_try5(self):
    self.add_prices()

  def tearDown(self):
    self.treap = None

if __name__ == "__main__":
  unittest.main()