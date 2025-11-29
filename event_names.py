"""
Funny and festive event name generator for Secret Santa
"""
import random
import string

# Lists of words for generating funny event names
ADJECTIVES = [
    "Jolly", "Merry", "Festive", "Magical", "Snowy", "Frosty", "Sparkly",
    "Cozy", "Cheery", "Joyful", "Bright", "Glittery", "Twinkling", "Dazzling",
    "Enchanted", "Delightful", "Whimsical", "Gleeful", "Radiant", "Blissful",
    "Epic", "Legendary", "Spectacular", "Magnificent", "Wonderful", "Fantastic",
    "Incredible", "Amazing", "Awesome", "Splendid", "Groovy", "Funky"
]

NOUNS = [
    "Elves", "Reindeer", "Snowflakes", "Candy Canes", "Gingerbread", "Mittens",
    "Stockings", "Ornaments", "Presents", "Sleigh Bells", "Snowmen", "Angels",
    "Stars", "Carolers", "Nutcrackers", "Wreaths", "Tinsel", "Holly",
    "Mistletoe", "Penguins", "Polar Bears", "Hot Chocolate", "Cookies",
    "Fruitcake", "Eggnog", "Jingle Bells", "Santa's Helpers", "Toy Makers",
    "Gift Givers", "Snow Angels", "Ice Skaters", "Sledders", "Carolers"
]

ACTIVITIES = [
    "Exchange", "Swap", "Party", "Celebration", "Gathering", "Fiesta",
    "Bash", "Shindig", "Soiree", "Jamboree", "Extravaganza", "Festival",
    "Bonanza", "Spectacular", "Gala", "Get-Together", "Meetup", "Reunion"
]

YEARS = [
    "2025", "Twenty Twenty-Five", "MMXXV"
]

THEMES = [
    "Winter Wonderland", "North Pole", "Santa's Workshop", "Candy Land",
    "Ice Palace", "Cozy Cabin", "Festive Forest", "Holiday Haven",
    "Jingle Junction", "Merry Manor", "Yuletide Yard", "Christmas Corner",
    "Snowy Summit", "Frosty Fields", "Twinkling Town", "Gift Grove"
]

def generate_event_name(style="default"):
    """
    Generate a funny/festive Secret Santa event name
    
    Args:
        style: Type of name to generate
            - "default": Adjective + Noun + Activity
            - "theme": Theme-based name
            - "year": Name with year
            - "funny": Extra silly combination
    
    Returns:
        str: Generated event name
    """
    if style == "theme":
        theme = random.choice(THEMES)
        activity = random.choice(ACTIVITIES)
        return f"{theme} Secret Santa {activity}"
    
    elif style == "year":
        adjective = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        year = random.choice(YEARS)
        return f"{adjective} {noun} {year}"
    
    elif style == "funny":
        adj1 = random.choice(ADJECTIVES)
        adj2 = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        activity = random.choice(ACTIVITIES)
        return f"The {adj1} {adj2} {noun} {activity}"
    
    else:  # default
        adjective = random.choice(ADJECTIVES)
        noun = random.choice(NOUNS)
        activity = random.choice(ACTIVITIES)
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

def get_random_event_names(count=5):
    """
    Generate multiple event name suggestions
    
    Args:
        count: Number of names to generate
    
    Returns:
        list: List of event names
    """
    styles = ["default", "theme", "year", "funny"]
    names = []
    
    for _ in range(count):
        style = random.choice(styles)
        name = generate_event_name(style)
        # Avoid duplicates
        while name in names:
            name = generate_event_name(style)
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
