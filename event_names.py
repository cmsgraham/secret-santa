"""
Event name generator for Secret Santa - loads names from config/event_names.json
Supports English and Spanish (multiple regions)
"""
import random
import string
import json
import os
from functools import lru_cache

# Path to configuration file
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config', 'event_names.json')

# Legacy naming for backward compatibility (fallback)
ADJECTIVES_EN = ["Merry", "Festive", "Magical", "Cozy", "Cheery"]
NOUNS_EN = ["Christmas Party", "Holiday Celebration", "Winter Festival"]
ACTIVITIES_EN = ["2025", "Celebration", "Party"]
YEARS_EN = ["2025"]
THEMES_EN = ["Winter Wonderland Secret Santa", "North Pole Gift Exchange"]

ADJECTIVES = ADJECTIVES_EN
NOUNS = NOUNS_EN
ACTIVITIES = ACTIVITIES_EN
YEARS = YEARS_EN
THEMES = THEMES_EN


@lru_cache(maxsize=1)
def _load_event_names_config():
    """Load event names configuration from JSON file"""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load event names config: {e}")
    
    # Return a minimal fallback if config file not found
    return {
        'en': {
            'adjectives': ADJECTIVES_EN,
            'nouns': NOUNS_EN,
            'activities': ACTIVITIES_EN,
            'themes': THEMES_EN
        }
    }


def _get_event_names_for_locale(locale="en"):
    """Get event name list for a specific locale"""
    config = _load_event_names_config()
    
    if locale in config and isinstance(config[locale], list):
        return config[locale]
    
    # Fallback to English
    if 'en' in config and isinstance(config['en'], list):
        return config['en']
    
    # Last resort: use hardcoded defaults
    return ["Holiday Celebration", "Christmas Party", "Gift Exchange"]

def generate_event_name(locale="en"):
    """
    Generate a random event name from the configured list for the given locale
    
    Args:
        locale: Language code (e.g., "en", "es_MX", "es_CR", "es_CO", "es_AR", "es_ES")
    
    Returns:
        str: Random event name from the configured list
    """
    names = _get_event_names_for_locale(locale)
    
    if names:
        return random.choice(names)
    
    return "Holiday Celebration"  # Fallback

def generate_event_code(length=8):
    """
    Generate a unique short code for event URLs
    Uses uppercase letters and numbers, avoiding ambiguous characters (0, O, 1, I, l)
    
    Args:
        length: Length of the code (default 8)
    
    Returns:
        str: Random code like "XK9M2PQ7"
    """
    # Remove ambiguous characters
    chars = string.ascii_uppercase.replace('O', '').replace('I', '')
    chars += string.digits.replace('0', '').replace('1', '')
    
    return ''.join(random.choice(chars) for _ in range(length))

def get_random_event_names(count=5, locale="en"):
    """
    Get multiple random event name suggestions
    
    Args:
        count: Number of names to generate
        locale: Language code (default "en")
    
    Returns:
        list: List of unique random event names
    """
    names_pool = _get_event_names_for_locale(locale)
    
    if not names_pool:
        return ["Holiday Celebration"] * count
    
    # Return unique names if possible
    if len(names_pool) >= count:
        return random.sample(names_pool, count)
    else:
        # If pool is smaller than count, use all names and fill with duplicates
        return names_pool + [random.choice(names_pool) for _ in range(count - len(names_pool))]

# Predefined funny names for quick selection
PREDEFINED_NAMES = [
    "Jolly Elves Gift Swap",
    "Merry Reindeer Exchange",
    "Festive Snowflakes Party",
    "Santa's Workshop Spectacular",
    "Winter Wonderland Secret Santa",
    "Cozy Cabin Gift Exchange",
    "Twinkling Town Celebration",
    "The Magnificent Snowmen Bash",
    "Sparkly Mittens Extravaganza",
    "Frosty Penguins Jamboree",
    "Epic Candy Canes Fiesta",
    "Magical Ornaments Gala",
    "North Pole Secret Santa Soiree",
    "Jingle Junction Gift Swap",
    "Holiday Haven Celebration",
    "Groovy Gingerbread Get-Together",
    "Legendary Hot Chocolate Exchange",
    "Whimsical Nutcrackers Party",
    "Dazzling Tinsel Bash",
    "Blissful Carolers Gathering"
]

def get_predefined_name():
    """Get a random predefined funny name"""
    return random.choice(PREDEFINED_NAMES)

if __name__ == "__main__":
    # Test the generator
    print("=== Secret Santa Event Name Generator ===\n")
    
    print("Default style names:")
    for _ in range(3):
        print(f"  - {generate_event_name('default')}")
    
    print("\nTheme-based names:")
    for _ in range(3):
        print(f"  - {generate_event_name('theme')}")
    
    print("\nWith year:")
    for _ in range(3):
        print(f"  - {generate_event_name('year')}")
    
    print("\nExtra funny:")
    for _ in range(3):
        print(f"  - {generate_event_name('funny')}")
    
    print("\nEvent codes:")
    for _ in range(5):
        print(f"  - {generate_event_code()}")
    
    print("\nRandom suggestions:")
    for name in get_random_event_names(5):
        print(f"  - {name}")
