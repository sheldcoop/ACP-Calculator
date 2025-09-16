# =====================================================================================
# THEME DEFINITIONS MODULE
# =====================================================================================
# This module contains the data structures and definitions for the different
# visual themes that can be applied to the application.
# =====================================================================================

from dataclasses import dataclass, field
from typing import List, Dict
import copy

@dataclass
class Theme:
    """Dataclass to hold all the properties of a visual theme."""
    name: str

    # --- Base Streamlit theme values (for config.toml overrides) ---
    primaryColor: str
    backgroundColor: str
    secondaryBackgroundColor: str
    textColor: str
    font: str

    # --- Custom CSS values ---
    # Font URLs and families
    base_font_url: str = "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
    base_font_family: str = "'Inter', sans-serif"
    mono_font_url: str = "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500&display=swap"
    mono_font_family: str = "'IBM Plex Mono', monospace"

    # "Glass" panel effect
    glass_bg_color: str = "rgba(44, 58, 71, 0.5)"
    glass_border_color: str = "rgba(255, 255, 255, 0.1)"
    glass_blur_radius: str = "10px"
    card_box_shadow: str = "0 4px 30px rgba(0, 0, 0, 0.1)"

    # Gauge colors
    gauge_good_color: str = "#00A9FF"
    gauge_danger_color: str = "#3D566D"
    gauge_target_color: str = "#FFFFFF"
    gauge_needle_color: str = "rgba(0, 169, 255, 0.7)"

    # Alert box border colors
    alert_success_border: str = "rgba(51, 255, 153, 0.5)"
    alert_info_border: str = "rgba(0, 169, 255, 0.5)"
    alert_warning_border: str = "rgba(255, 195, 0, 0.5)"
    alert_error_border: str = "rgba(255, 107, 107, 0.5)"

    # Special flags
    use_aurora_bg: bool = False
    custom_css_rules: Dict[str, str] = field(default_factory=dict)

# =====================================================================================
# BASE THEME DEFINITIONS
# =====================================================================================

# Define the base themes that will be customized
BASE_THEMES = {
    "Mission Control": Theme(
        name="Mission Control",
        primaryColor="#00A9FF",
        backgroundColor="#1A202C",
        secondaryBackgroundColor="#2C3A47",
        textColor="#F0F2F6",
        font="sans serif",
    ),
    "Swiss": Theme(
        name="Swiss",
        primaryColor="#D22B2B", # Default to Red
        backgroundColor="#FFFFFF",
        secondaryBackgroundColor="#F0F2F6",
        textColor="#31333F",
        font="sans serif",
        base_font_family="'Inter', sans-serif",
        mono_font_family="'Inter', sans-serif",
        glass_bg_color="rgba(255, 255, 255, 0.8)",
        glass_border_color="rgba(0, 0, 0, 0.05)",
        glass_blur_radius="0px",
        card_box_shadow="0 1px 4px rgba(0, 0, 0, 0.05)",
        gauge_danger_color="#E0E0E0",
        gauge_target_color="#31333F",
        alert_success_border="#28a745",
        alert_info_border="#17a2b8",
        alert_warning_border="#ffc107",
        alert_error_border="#dc3545",
    )
}

# =====================================================================================
# THEME CUSTOMIZATIONS
# =====================================================================================

def create_swiss_variant(name: str, color: str, needle_color: str) -> Theme:
    """Creates a Swiss theme variant with a specific accent color."""
    variant = copy.deepcopy(BASE_THEMES["Swiss"])
    variant.name = name
    variant.primaryColor = color
    variant.gauge_good_color = color
    variant.gauge_needle_color = needle_color
    return variant

THEMES = {
    "Mission Control": BASE_THEMES["Mission Control"],
    "Swiss - Red": create_swiss_variant("Swiss - Red", "#D22B2B", "rgba(210, 43, 43, 0.7)"),
    "Swiss - Blue": create_swiss_variant("Swiss - Blue", "#004488", "rgba(0, 68, 136, 0.7)"),
    "Swiss - Green": create_swiss_variant("Swiss - Green", "#28a745", "rgba(40, 167, 69, 0.7)"),
    "Swiss - Orange": create_swiss_variant("Swiss - Orange", "#fd7e14", "rgba(253, 126, 20, 0.7)"),
}
