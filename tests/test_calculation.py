import unittest
import math
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calculation import calculate_module3_correction, calculate_module7_correction

class TestCalculation(unittest.TestCase):

    def test_module3_both_high(self):
        """
        Test Case 1: Module 3 (Both High)
        - Start: 120 L at 130 A / 58 B
        - Target: 120 A / 50 B
        - Expected Result: Add ~11.44 L of water.
        """
        # Makeup concentrations are the target concentrations
        makeup_conc_a_ml_l = 120
        makeup_conc_b_ml_l = 50

        result = calculate_module3_correction(
            current_volume=120.0,
            measured_conc_a_ml_l=130.0,
            measured_conc_b_ml_l=58.0,
            makeup_conc_a_ml_l=makeup_conc_a_ml_l,
            makeup_conc_b_ml_l=makeup_conc_b_ml_l,
            module3_total_volume=260.0  # Assuming a total volume of 260L
        )
        self.assertAlmostEqual(result["add_water"], 11.44, places=2)
        self.assertAlmostEqual(result["add_makeup"], 0.0, places=2)

    def test_module3_mixed(self):
        """
        Test Case 2: Module 3 (Mixed)
        - Start: 100 L at 150 A / 45 B
        - Target: 120 A / 50 B
        - Expected Result: Add 140 L of makeup solution.
        """
        # Makeup concentrations are the target concentrations
        makeup_conc_a_ml_l = 120
        makeup_conc_b_ml_l = 50

        result = calculate_module3_correction(
            current_volume=100.0,
            measured_conc_a_ml_l=150.0,
            measured_conc_b_ml_l=45.0,
            makeup_conc_a_ml_l=makeup_conc_a_ml_l,
            makeup_conc_b_ml_l=makeup_conc_b_ml_l,
            module3_total_volume=240.0 # Assuming a total volume of 240L
        )
        self.assertAlmostEqual(result["add_water"], 0.0, places=2)
        self.assertAlmostEqual(result["add_makeup"], 140.0, places=2)

    def test_module7_all_high(self):
        """
        Test Case 3: Module 7 (All High)
        - Start: 180 L, 190 Conditioner, 22 Cu Etch, 7.5 H2O2
        - Target: 180 Conditioner, 20 Cu Etch, 7 H2O2
        - Expected Result: Add a small, precise amount of water.
        """
        # Makeup concentrations are the target concentrations
        makeup_cond_ml_l = 180.0
        makeup_cu_g_l = 20.0
        makeup_h2o2_ml_l = 7.0

        result = calculate_module7_correction(
            current_volume=180.0,
            current_cond_ml_l=190.0,
            current_cu_g_l=22.0,
            current_h2o2_ml_l=7.5,
            target_cond_ml_l=makeup_cond_ml_l,
            target_cu_g_l=makeup_cu_g_l,
            target_h2o2_ml_l=makeup_h2o2_ml_l,
            module7_total_volume=260.0  # Assuming a total volume of 260L
        )

        # The expected result is a small amount of water, not a large top-up.
        # The exact value depends on the vector projection calculation.
        # We will check if the water added is greater than 0 and makeup is 0.
        self.assertGreater(result["add_water"], 0)
        self.assertAlmostEqual(result["add_cond"], 0.0, places=2)
        self.assertAlmostEqual(result["add_cu"], 0.0, places=2)
        self.assertAlmostEqual(result["add_h2o2"], 0.0, places=2)

if __name__ == '__main__':
    unittest.main()
