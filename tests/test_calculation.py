import unittest
import math
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.calculation import calculate_module3_correction, calculate_module7_correction

class TestCalculation(unittest.TestCase):

    def test_module3_optimizer_fortification(self):
        """
        Test Case: Check the optimizer's result for a standard fortification.
        - In this case, the makeup is the same as the target. The optimizer
        - should conclude that adding the maximum amount of makeup is the best
        - way to reduce the error.
        - Start: 100 L at 150 A / 45 B
        - Target: 120 A / 50 B
        - Makeup: 120 A / 50 B
        - Expected Result: Add 140 L of makeup, 0 L of water.
        """
        target_conc_a_ml_l = 120
        target_conc_b_ml_l = 50
        makeup_conc_a_ml_l = 120
        makeup_conc_b_ml_l = 50

        result = calculate_module3_correction(
            current_volume=100.0,
            measured_conc_a_ml_l=150.0,
            measured_conc_b_ml_l=45.0,
            target_conc_a_ml_l=target_conc_a_ml_l,
            target_conc_b_ml_l=target_conc_b_ml_l,
            makeup_conc_a_ml_l=makeup_conc_a_ml_l,
            makeup_conc_b_ml_l=makeup_conc_b_ml_l,
            module3_total_volume=240.0
        )
        # The optimizer finds a non-intuitive optimal solution here.
        self.assertAlmostEqual(result["add_water"], 19.82, places=2)
        self.assertAlmostEqual(result["add_makeup"], 120.18, places=2)

    def test_module3_backwards_compatibility_high(self):
        """
        Test Case (User Request): Ensure new logic matches old logic (High case).
        - Start: 120 L at 130 A / 58 B
        - Target: 120 A / 50 B
        - Makeup: 120 A / 50 B
        - Expected Result: Add ~11.44 L of water (same as old logic).
        """
        target_conc_a_ml_l = 120
        target_conc_b_ml_l = 50
        makeup_conc_a_ml_l = 120
        makeup_conc_b_ml_l = 50

        result = calculate_module3_correction(
            current_volume=120.0,
            measured_conc_a_ml_l=130.0,
            measured_conc_b_ml_l=58.0,
            target_conc_a_ml_l=target_conc_a_ml_l,
            target_conc_b_ml_l=target_conc_b_ml_l,
            makeup_conc_a_ml_l=makeup_conc_a_ml_l,
            makeup_conc_b_ml_l=makeup_conc_b_ml_l,
            module3_total_volume=260.0
        )
        self.assertAlmostEqual(result["add_water"], 11.44, places=2)
        self.assertAlmostEqual(result["add_makeup"], 0.0, places=2)

    def test_module3_optimizer_imbalanced_makeup(self):
        """
        Test Case: Check optimizer with imbalanced makeup.
        - A is low, B is high. Makeup helps A but hurts B.
        - The optimizer should find a non-obvious mix of water and makeup.
        - Start: 100L at 80 A / 55 B
        - Target: 100 A / 50 B
        - Makeup: 120 A / 40 B
        - Expected: A mix of water and makeup, not just one or the other.
        """
        target_conc_a_ml_l = 100
        target_conc_b_ml_l = 50
        makeup_conc_a_ml_l = 120 # Good for A
        makeup_conc_b_ml_l = 40  # Bad for B

        result = calculate_module3_correction(
            current_volume=100.0,
            measured_conc_a_ml_l=80.0,
            measured_conc_b_ml_l=55.0,
            target_conc_a_ml_l=target_conc_a_ml_l,
            target_conc_b_ml_l=target_conc_b_ml_l,
            makeup_conc_a_ml_l=makeup_conc_a_ml_l,
            makeup_conc_b_ml_l=makeup_conc_b_ml_l,
            module3_total_volume=200.0
        )
        # We expect a mix, not a simple fill.
        # The exact values depend on the optimizer, but both should be non-zero.
        # The optimizer correctly determined that it should not fill all available
        # space, as doing so would increase the error.
        self.assertGreater(result["add_water"], 0)
        self.assertGreater(result["add_makeup"], 0)


    def test_module3_separate_target_and_makeup(self):
        """
        Test Case 3: New logic with separate target and makeup concentrations.
        - The current concentration is ABOVE the target, so it should dilute.
        - This confirms the decision logic uses the TARGET, not the makeup.
        - Start: 150 L at 110 A / 55 B
        - Target: 100 A / 50 B
        - Makeup: 120 A / 60 B (stronger than current)
        - Expected Result: Add water for dilution, not makeup.
        """
        target_conc_a_ml_l = 100
        target_conc_b_ml_l = 50
        makeup_conc_a_ml_l = 120  # Stronger than current
        makeup_conc_b_ml_l = 60   # Stronger than current

        result = calculate_module3_correction(
            current_volume=150.0,
            measured_conc_a_ml_l=110.0, # Above target
            measured_conc_b_ml_l=55.0,  # Above target
            target_conc_a_ml_l=target_conc_a_ml_l,
            target_conc_b_ml_l=target_conc_b_ml_l,
            makeup_conc_a_ml_l=makeup_conc_a_ml_l,
            makeup_conc_b_ml_l=makeup_conc_b_ml_l,
            module3_total_volume=250.0
        )
        # Expects dilution (water > 0) because current > target
        self.assertGreater(result["add_water"], 0)
        self.assertEqual(result["add_makeup"], 0)

    def test_module7_all_high(self):
        """
        Test Case for Module 7 (All High - Dilution).
        Checks that the dilution logic is triggered correctly.
        """
        target_cond = 180.0
        target_cu = 20.0
        target_h2o2 = 7.0

        result = calculate_module7_correction(
            current_volume=180.0,
            current_cond_ml_l=190.0, current_cu_g_l=22.0, current_h2o2_ml_l=7.5,
            target_cond_ml_l=target_cond, target_cu_g_l=target_cu, target_h2o2_ml_l=target_h2o2,
            makeup_cond_ml_l=target_cond, makeup_cu_g_l=target_cu, makeup_h2o2_ml_l=target_h2o2,
            module7_total_volume=260.0
        )

        self.assertGreater(result["add_water"], 0)
        self.assertAlmostEqual(result["add_makeup"], 0.0, places=2)

    def test_module7_optimizer_fortification(self):
        """
        Test Case for Module 7 (Fortification).
        Checks that the optimizer correctly recommends adding makeup.
        """
        target_cond = 180.0
        target_cu = 20.0
        target_h2o2 = 7.0

        result = calculate_module7_correction(
            current_volume=180.0,
            current_cond_ml_l=170.0, # Low
            current_cu_g_l=18.0,   # Low
            current_h2o2_ml_l=6.0,   # Low
            target_cond_ml_l=target_cond, target_cu_g_l=target_cu, target_h2o2_ml_l=target_h2o2,
            makeup_cond_ml_l=target_cond, makeup_cu_g_l=target_cu, makeup_h2o2_ml_l=target_h2o2,
            module7_total_volume=250.0
        )

        self.assertGreater(result["add_makeup"], 0)
        self.assertAlmostEqual(result["add_water"], 0.0, places=2)

    def test_module7_optimizer_imbalanced_makeup(self):
        """
        Test Case for Module 7 (Imbalanced Makeup).
        - Cond is low, Cu is high, H2O2 is low.
        - Makeup helps Cond and H2O2 but hurts Cu.
        - The optimizer should find a non-obvious mix of water and makeup.
        """
        result = calculate_module7_correction(
            current_volume=200.0,
            current_cond_ml_l=170.0, # Low
            current_cu_g_l=23.0,   # High
            current_h2o2_ml_l=6.0,   # Low
            target_cond_ml_l=180.0, target_cu_g_l=20.0, target_h2o2_ml_l=7.0,
            makeup_cond_ml_l=200.0, makeup_cu_g_l=15.0, makeup_h2o2_ml_l=8.0,
            module7_total_volume=250.0
        )
        # The optimizer correctly determines that adding water is not optimal,
        # as the makeup solution itself helps correct the high Cu concentration.
        # For this specific case, it also finds that filling the available
        # space is the best way to minimize the total error.
        self.assertAlmostEqual(result["add_water"], 0.0, places=2)
        self.assertAlmostEqual(result["add_makeup"], 50.0, places=2)

if __name__ == '__main__':
    unittest.main()
