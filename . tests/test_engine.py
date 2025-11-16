import unittest
from engine import run_bulk_simulation

class TestSimulation(unittest.TestCase):
    def test_basic_run(self):
        results = run_bulk_simulation(["Alice", "Bob"], rounds=2)
        self.assertIn("Alice", results)
        self.assertIn("Bob", results)
        self.assertTrue(all(isinstance(actions, list) for actions in results.values()))

if __name__ == "__main__":
    unittest.main()
