"""
Configuration file for College Maintenance and Request System
"""

import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_config.json")

DEFAULT_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "database": "college_maintenance_db"
}

def load_db_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return {**DEFAULT_CONFIG, **cfg}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_db_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

# UI Theme Colors
COLORS = {
    "primary": "#1E3A8A",       # Navy Blue
    "primary_dark": "#172554",
    "secondary": "#0284C7",     # Sky Blue
    "accent": "#F59E0B",        # Amber
    "success": "#10B981",       # Emerald Green
    "danger": "#EF4444",        # Red
    "warning": "#F97316",       # Orange
    "bg_dark": "#0F172A",       # Slate 900
    "bg_light": "#F8FAFC",      # Slate 50
    "card_bg": "#FFFFFF",
    "text_dark": "#1E293B",
    "text_light": "#64748B",
    "border": "#CBD5E1"
}
