"""
Fun nickname generator for Secret Santa participants
Loads names from config/nicknames.json instead of hardcoding
"""
import random
import json
import os
from functools import lru_cache

# Path to configuration file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'nicknames.json')

# Legacy naming for backward compatibility (fallback)
ADJECTIVES_EN = [
    "Super", "Magical", "Lucky", "Jolly", "Happy", "Brilliant", "Clever"
]

NOUNS_EN = [
    "Santa", "Rudolph", "Buddy", "Krampus", "Mrs. Claus", "Elf", "Scrooge"
]

ADJECTIVES = ADJECTIVES_EN
NOUNS = NOUNS_EN


@lru_cache(maxsize=1)
def _load_nicknames_config():
    """Load nicknames configuration from JSON file"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load nicknames config: {e}")
    
    # Return a minimal fallback if config file not found
    return {
        'en': [
            "Super Santa", "Magical Rudolph", "Lucky Buddy", "Jolly Krampus", 
            "Happy Mrs. Claus", "Brilliant Elf", "Clever Scrooge"
        ]
    }


def _get_nicknames_for_locale(locale="en"):
    """Get nickname list for a specific locale"""
    config = _load_nicknames_config()
    
    if locale in config and isinstance(config[locale], list):
        return config[locale]
    
    # Fallback to English
    if 'en' in config and isinstance(config['en'], list):
        return config['en']
    
    # Last resort: use hardcoded defaults
    return [f"{adj} {noun}" for adj in ADJECTIVES_EN for noun in NOUNS_EN][:20]

def generate_nickname(locale="en"):
    """
    Generate a fun random nickname from language-specific configuration
    
    Args:
        locale: Language code (e.g., "en", "es_MX", "es_CR", "es_CO", "es_AR", "es_ES")
    
    Returns:
        str: Random nickname from the configured list
    """
    nicknames = _get_nicknames_for_locale(locale)
    
    if nicknames:
        return random.choice(nicknames)
    
    return "Secret Santa"  # Fallback

def get_random_nicknames(count=5, locale="en"):
    """
    Get multiple random nicknames from the configured list
    
    Args:
        count: Number of nicknames to generate
        locale: Language code (default "en")
    
    Returns:
        list: List of random nicknames
    """
    nicknames_pool = _get_nicknames_for_locale(locale)
    
    if not nicknames_pool:
        return ["Secret Santa"] * count
    
    # Ensure we have enough unique nicknames
    if len(nicknames_pool) >= count:
        return random.sample(nicknames_pool, count)
    else:
        # If pool is smaller than count, use random.choices with replacement
        return [random.choice(nicknames_pool) for _ in range(count)]
