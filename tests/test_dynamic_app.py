import unittest
import os
import json
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config.manager import save_config, load_config, CONFIG_FILE
from modules.calculation import dispatch_calculation

class TestDynamicApp(unittest.TestCase):

    def setUp(self):
        """Set up a dummy config file for testing."""
        self.test_config = [
            {
                "name": "Test Module 2-Comp",
                "module_type": "2-Component Corrector",
                "total_volume": 240.0,
                "chemicals": [
                    {"name": "Acid", "unit": "ml/L", "target": 120.0, "internal_id": "A"},
                    {"name": "Brightener", "unit": "ml/L", "target": 50.0, "internal_id": "B"}
                ]
            },
            {
                "name": "Test Module 3-Comp",
                "module_type": "3-Component Corrector",
                "total_volume": 250.0,
                "chemicals": [
                    {"name": "Conditioner", "unit": "ml/L", "target": 180.0, "internal_id": "cond"},
                    {"name": "Copper", "unit": "g/L", "target": 20.0, "internal_id": "cu"},
                    {"name": "Peroxide", "unit": "ml/L", "target": 7.0, "internal_id": "h2o2"}
                ]
            }
        ]
        save_config(self.test_config)

    def tearDown(self):
        """Remove the dummy config file after tests."""
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

    def test_config_file_creation(self):
        """Test that the config file is created and loaded correctly."""
        loaded = load_config()
        self.assertIsNotNone(loaded)
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['name'], "Test Module 2-Comp")

    def test_dispatch_2_component_corrector(self):
        """Test the dispatcher for a 2-component module."""
        module_config = self.test_config[0]
        inputs = {
            "current_volume": 100.0,
            "current_A": 150.0,
            "current_B": 45.0,
            "target_A": 120.0,
            "target_B": 50.0,
            "makeup_A": 120.0,
            "makeup_B": 50.0
        }

        result = dispatch_calculation(module_config, inputs)

        self.assertIn("status", result)
        self.assertEqual(result['status'], "OPTIMAL_FORTIFICATION")
        self.assertGreater(result['add_makeup'], 0)
        self.assertAlmostEqual(result['final_A'], 122.59, places=2)
        self.assertAlmostEqual(result['final_B'], 43.79, places=2)

    def test_dispatch_3_component_corrector_dilution(self):
        """Test the dispatcher for a 3-component module in a dilution case."""
        module_config = self.test_config[1]
        inputs = {
            "current_volume": 180.0,
            "current_cond": 190.0,
            "current_cu": 22.0,
            "current_h2o2": 7.5,
            "target_cond": 180.0,
            "target_cu": 20.0,
            "target_h2o2": 7.0,
            "makeup_cond": 180.0,
            "makeup_cu": 20.0,
            "makeup_h2o2": 7.0
        }

        result = dispatch_calculation(module_config, inputs)

        self.assertIn("status", result)
        self.assertEqual(result['status'], "OPTIMAL_DILUTION")
        self.assertGreater(result['add_water'], 0)
        self.assertEqual(result['add_makeup'], 0)

    def test_edit_and_save_config(self):
        """Test that editing a configuration and saving it works."""
        # Load the initial config
        config = load_config()
        # "Edit" a value
        config[0]['chemicals'][0]['target'] = 999.0
        # "Save" the changes
        save_config(config)
        # Load it again to check
        new_config = load_config()
        self.assertEqual(new_config[0]['chemicals'][0]['target'], 999.0)

    def test_simulation_dispatcher(self):
        """Test the simulation dispatcher for a 2-component module."""
        from modules.calculation import dispatch_simulation
        module_config = self.test_config[0]
        sim_inputs = {
            "current_volume": 100.0,
            "current_A": 150.0,
            "current_B": 60.0,
            "makeup_A": 120.0,
            "makeup_B": 50.0,
            "water_to_add": 10.0,
            "makeup_to_add": 20.0
        }

        results = dispatch_simulation(module_config, sim_inputs)

        self.assertAlmostEqual(results['new_volume'], 130.0)
        self.assertAlmostEqual(results['new_A'], 133.85, places=2)
        self.assertAlmostEqual(results['new_B'], 53.85, places=2)


if __name__ == '__main__':
    unittest.main()
