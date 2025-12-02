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


def _get_config_for_locale(locale="en"):
    """Get configuration for a specific locale"""
    config = _load_event_names_config()
    
    if locale in config:
        return config[locale]
    
    # Fallback to English
    if 'en' in config:
        return config['en']
    
    # Last resort: use hardcoded defaults
    return {
        'adjectives': ADJECTIVES_EN,
        'nouns': NOUNS_EN,
        'activities': ACTIVITIES_EN,
        'themes': THEMES_EN
    }

def generate_event_name(style="default", locale="en"):
    """
    Generate a meaningful Secret Santa event name based on language configuration
    
    Args:
        style: Type of name to generate
            - "default": Adjective + Noun + Activity
            - "theme": Theme-based name
            - "year": Name with year
            - "funny": Extra adjective + noun combination
        locale: Language code (e.g., "en", "es_MX", "es_CR", "es_CO", "es_AR", "es_ES")
    
    Returns:
        str: Generated event name loaded from config
    """
    config = _get_config_for_locale(locale)
    
    adjectives = config.get('adjectives', [])
    nouns = config.get('nouns', [])
    activities = config.get('activities', [])
    themes = config.get('themes', [])
    
    if not adjectives or not nouns:
        return "Secret Santa 2025"  # Fallback
    
    if style == "theme" and themes:
        theme = random.choice(themes)
        return f"{theme} 2025"
    
    elif style == "year":
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        return f"{adjective} {noun} 2025"
    
    elif style == "funny":
        adj1 = random.choice(adjectives)
        noun1 = random.choice(nouns)
        noun2 = random.choice(nouns)
        return f"{adj1} {noun1} y {noun2}" if locale and locale.startswith('es') else f"{adj1} {noun1} & {noun2}"
    
    else:  # default
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        activity = random.choice(activities)
        if locale and locale.startswith('es'):
            return f"{adjective} {noun} de {activity}"
        else:
            return f"{adjective} {noun} {activity}"

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
    Generate multiple event name suggestions
    
    Args:
        count: Number of names to generate
        locale: Language code (default "en")
    
    Returns:
        list: List of event names
    """
    styles = ["default", "theme", "year", "funny"]
    names = []
    
    for _ in range(count):
        style = random.choice(styles)
        name = generate_event_name(style=style, locale=locale)
        while name in names:
            name = generate_event_name(style=style, locale=locale)
        names.append(name)
    
    return names

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
