# =====================================================================================
# CONFIGURATION MANAGER
# =====================================================================================
# This module handles loading, saving, and managing the application's
# dynamic configuration from a JSON file.
# =====================================================================================

import json
import streamlit as st
from typing import Dict, List, Any, Optional

# The name of the configuration file
CONFIG_FILE = "config.json"

# Define the structure of a single chemical
class Chemical:
    def __init__(self, name: str, unit: str, target: float, internal_id: str):
        self.name = name
        self.unit = unit
        self.target = target
        self.internal_id = internal_id  # e.g., "A", "B", "cond", "cu", "h2o2"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "unit": self.unit,
            "target": self.target,
            "internal_id": self.internal_id
        }

# Define the structure of a single module
class Module:
    def __init__(self, name: str, module_type: str, total_volume: float, chemicals: List[Chemical]):
        self.name = name
        self.module_type = module_type  # e.g., "2-Component Corrector"
        self.total_volume = total_volume
        self.chemicals = chemicals

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "module_type": self.module_type,
            "total_volume": self.total_volume,
            "chemicals": [c.to_dict() for c in self.chemicals]
        }

# --- Core Functions ---

def load_config() -> Optional[List[Dict[str, Any]]]:
    """
    Loads the configuration from config.json.
    Returns the config as a list of dictionaries, or None if the file doesn't exist.
    """
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        # Handle cases where the file is corrupted or empty
        return None

def save_config(config: List[Dict[str, Any]]):
    """
    Saves the provided configuration list to config.json.
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_module_types() -> Dict[str, List[str]]:
    """
    Returns a dictionary of available module types and the internal chemical IDs
    they require. This defines the "calculation engines" available.
    """
    return {
        "2-Component Corrector": ["A", "B"],
        "3-Component Corrector": ["cond", "cu", "h2o2"],
        # Add other types like sandboxes here in the future
    }
