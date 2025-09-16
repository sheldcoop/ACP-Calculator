# =====================================================================================
# THEME DEFINITIONS MODULE
# =====================================================================================
# This module contains the data structures and definitions for the different
# visual themes that can be applied to the application.
# =====================================================================================

from dataclasses import dataclass, field
from typing import List, Dict

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
# THEME DEFINITIONS
# =====================================================================================

THEMES = {
    "Mission Control": Theme(
        name="Mission Control",
        primaryColor="#00A9FF",
        backgroundColor="#1A202C",
        secondaryBackgroundColor="#2C3A47",
        textColor="#F0F2F6",
        font="sans serif",
        # Custom values are mostly the defaults, which were designed for this theme
    ),

    "Swiss Precision": Theme(
        name="Swiss Precision",
        primaryColor="#D22B2B", # A bold, clinical red
        backgroundColor="#FFFFFF",
        secondaryBackgroundColor="#F0F2F6",
        textColor="#31333F",
        font="sans serif",
        base_font_url="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap",
        base_font_family="'Inter', sans-serif",
        mono_font_url="https://fonts.googleapis.com/css2?family=Inter:wght@700&display=swap",
        mono_font_family="'Inter', sans-serif",
        glass_bg_color="rgba(255, 255, 255, 0.8)",
        glass_border_color="rgba(0, 0, 0, 0.05)",
        glass_blur_radius="0px", # No blur for a crisp look
        card_box_shadow="0 1px 4px rgba(0, 0, 0, 0.05)",
        gauge_good_color="#D22B2B",
        gauge_danger_color="#E0E0E0",
        gauge_target_color="#31333F",
        gauge_needle_color="rgba(210, 43, 43, 0.7)",
        alert_success_border="#28a745",
        alert_info_border="#17a2b8",
        alert_warning_border="#ffc107",
        alert_error_border="#dc3545",
    ),

    "Blueprint": Theme(
        name="Blueprint",
        primaryColor="#FFD700", # A bright yellow for contrast
        backgroundColor="#2a3f5f",
        secondaryBackgroundColor="#3c5a88",
        textColor="#E0E0E0",
        font="sans serif",
        base_font_url="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&display=swap",
        base_font_family="'Roboto Condensed', sans-serif",
        mono_font_url="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@700&display=swap",
        mono_font_family="'Roboto Condensed', sans-serif",
        glass_bg_color="rgba(0, 0, 0, 0.1)",
        glass_border_color="rgba(255, 215, 0, 0.3)",
        card_box_shadow="none",
        gauge_good_color="#FFD700",
        gauge_danger_color="#5a76a8",
        gauge_target_color="#FFFFFF",
        gauge_needle_color="rgba(255, 215, 0, 0.7)",
        alert_success_border="#FFD700",
        alert_info_border="#FFD700",
        alert_warning_border="#FFD700",
        alert_error_border="#FFD700",
        custom_css_rules={
            "div[data-testid=\"stExpander\"]": "border-style: dashed; border-width: 1px;",
            "h1, h2, h3": "font-variant: small-caps; font-weight: 700;",
        }
    ),

    "Solaris Light": Theme(
        name="Solaris Light",
        primaryColor="#d33682", # Magenta
        backgroundColor="#fdf6e3", # Base
        secondaryBackgroundColor="#eee8d5", # Base1
        textColor="#657b83", # Base00
        font="sans serif",
        base_font_url="https://fonts.googleapis.com/css2?family=Lora:wght@400;600&display=swap",
        base_font_family="'Lora', serif",
        mono_font_url="https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@500&display=swap",
        mono_font_family="'Source Code Pro', monospace",
        glass_bg_color="rgba(238, 232, 213, 0.7)", # Base1 with alpha
        glass_border_color="rgba(147, 161, 161, 0.2)", # Base0
        glass_blur_radius="0px",
        card_box_shadow="0 1px 3px rgba(0,0,0,0.05)",
        gauge_good_color="#859900", # Green
        gauge_danger_color="#dc322f", # Red
        gauge_target_color="#657b83",
        gauge_needle_color="rgba(211, 54, 130, 0.7)",
        alert_success_border="#859900",
        alert_info_border="#268bd2",
        alert_warning_border="#b58900",
        alert_error_border="#dc322f",
    ),

    "Glass & Aurora": Theme(
        name="Glass & Aurora",
        primaryColor="#FFFFFF",
        backgroundColor="#111111", # A very dark base for the aurora to pop
        secondaryBackgroundColor="rgba(255, 255, 255, 0.05)", # Will be part of glass effect
        textColor="#E0E0E0",
        font="sans serif",
        base_font_url="https://fonts.googleapis.com/css2?family=Manrope:wght@400;700&display=swap",
        base_font_family="'Manrope', sans-serif",
        mono_font_url="https://fonts.googleapis.com/css2?family=Manrope:wght@700&display=swap",
        mono_font_family="'Manrope', sans-serif",
        glass_bg_color="rgba(255, 255, 255, 0.05)",
        glass_border_color="rgba(255, 255, 255, 0.2)",
        glass_blur_radius="20px",
        card_box_shadow="0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        gauge_good_color="#FFFFFF",
        gauge_danger_color="#555555",
        gauge_target_color="#FFFFFF",
        gauge_needle_color="rgba(255, 255, 255, 0.7)",
        alert_success_border="rgba(51, 255, 153, 0.7)",
        alert_info_border="rgba(0, 169, 255, 0.7)",
        alert_warning_border="rgba(255, 195, 0, 0.7)",
        alert_error_border="rgba(255, 107, 107, 0.7)",
        use_aurora_bg=True,
    ),
}
