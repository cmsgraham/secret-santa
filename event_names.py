"""
Funny and festive event name generator for Secret Santa
Supports English and Spanish (multiple regions)
"""
import random
import string

# English word lists - Cultural events and celebrations
ADJECTIVES_EN = [
    "Merry", "Festive", "Magical", "Cozy", "Cheery", "Joyful", "Bright",
    "Wonderful", "Fantastic", "Amazing", "Awesome", "Splendid", "Legendary"
]

NOUNS_EN = [
    "Christmas Party", "Holiday Celebration", "Winter Festival", "Gift Exchange",
    "Tree Trimming", "Caroling Night", "Ugly Sweater Party", "Cookie Exchange",
    "Gingerbread Decorating", "Ornament Swap", "White Elephant", "Secret Santa",
    "Holiday Potluck", "Eggnog Tasting", "Lights Tour", "Movie Marathon"
]

ACTIVITIES_EN = [
    "2025", "Celebration", "Party", "Gathering", "Exchange", "Bash"
]

YEARS_EN = [
    "2025"
]

THEMES_EN = [
    "Winter Wonderland Secret Santa",
    "North Pole Gift Exchange",
    "Festive Holiday Celebration",
    "Cozy Christmas Gathering",
    "Magical Winter Party",
    "Joyful Holiday Exchange",
    "Merry Christmas Bash",
    "Bright Holiday Festival"
]

# Spanish word lists - Cultural events and celebrations
# Using names that make sense: festivals, TV shows, parties, cultural events

# Mexico: Día de Muertos, Posadas, Carnaval, Las Mañanitas
ADJECTIVES_ES_MX = [
    "Festivo", "Navideño", "Colorido", "Alegre", "Tradicional", "Mágico", "Especial"
]

NOUNS_ES_MX = [
    "Posadas", "Navidad", "Intercambio Navideño", "Fiesta Familiar",
    "Cena Navideña", "Reunión Festiva", "Celebración Decembrina",
    "Piñata Party", "Convivio", "Festejo Navideño", "Compartir Regalos"
]

ACTIVITIES_ES_MX = [
    "2025", "Celebración", "Fiesta", "Reunión", "Intercambio", "Festejo"
]

THEMES_ES_MX = [
    "Posadas Navideñas",
    "Navidad Mexicana",
    "Fiesta de Intercambio",
    "Celebración Decembrina",
    "Reunión Festiva"
]

# Costa Rica: Luces de Navidad, Las Festividades, Típicos
ADJECTIVES_ES_CR = [
    "Festivo", "Navideño", "Tico", "Alegre", "Especial", "Mágico", "Cálido"
]

NOUNS_ES_CR = [
    "Luces de Navidad", "Navidad Tica", "Intercambio Festivo",
    "Cena Navideña", "Fiesta Familiar", "Convivio Navideño",
    "Típicos Navideños", "Posada Tica", "Reunión Decembrina", "Celebración Costarricense"
]

ACTIVITIES_ES_CR = [
    "2025", "Celebración", "Fiesta", "Reunión", "Intercambio", "Convivio"
]

THEMES_ES_CR = [
    "Luces de Navidad Costa Rica",
    "Navidad Tica",
    "Fiesta Costarricense",
    "Celebración Tica",
    "Reunión Festiva"
]

# Colombia: Festival de Luces, Navidad, Cumbia
ADJECTIVES_ES_CO = [
    "Festivo", "Navideño", "Colorido", "Alegre", "Tradicional", "Mágico", "Caluroso"
]

NOUNS_ES_CO = [
    "Festival de Luces", "Navidad Colombiana", "Intercambio Navideño",
    "Fiesta Familiar", "Cena Navideña", "Celebración Decembrina",
    "Convivio Navideño", "Reunión Festiva", "Cumbia Navideña", "Compartir Regalos"
]

ACTIVITIES_ES_CO = [
    "2025", "Celebración", "Fiesta", "Reunión", "Intercambio", "Festival"
]

THEMES_ES_CO = [
    "Festival de Luces",
    "Navidad Colombiana",
    "Fiesta de Intercambio",
    "Celebración Navideña",
    "Reunión Festiva"
]

# Argentina: Asado Navideño, Tango, Fiesta
ADJECTIVES_ES_AR = [
    "Festivo", "Navideño", "Argentino", "Alegre", "Especial", "Mágico", "Caluroso"
]

NOUNS_ES_AR = [
    "Asado Navideño", "Navidad Argentina", "Intercambio de Regalos",
    "Fiesta Familiar", "Cena Navideña", "Reunión Festiva",
    "Convivio Navideño", "Abrazo Navideño", "Celebración Decembrina", "Compartir en Familia"
]

ACTIVITIES_ES_AR = [
    "2025", "Celebración", "Fiesta", "Reunión", "Intercambio", "Abrazo"
]

THEMES_ES_AR = [
    "Asado Navideño",
    "Navidad Argentina",
    "Fiesta de Intercambio",
    "Celebración Navideña",
    "Reunión Familiar"
]

# Spain: Nochebuena, Roscón de Reyes, Cena Navideña
ADJECTIVES_ES_ES = [
    "Festivo", "Navideño", "Español", "Alegre", "Tradicional", "Mágico", "Especial"
]

NOUNS_ES_ES = [
    "Nochebuena", "Roscón de Reyes", "Cena Navideña",
    "Intercambio Navideño", "Fiesta Familiar", "Reunión Festiva",
    "Celebración Española", "Convivio Navideño", "Turrón Party", "Champagne y Uvas"
]

ACTIVITIES_ES_ES = [
    "2025", "Celebración", "Fiesta", "Reunión", "Intercambio", "Cena"
]

THEMES_ES_ES = [
    "Nochebuena Española",
    "Navidad Española",
    "Roscón de Reyes",
    "Celebración Navideña",
    "Reunión Festiva"
]

# Legacy naming for backward compatibility
ADJECTIVES = ADJECTIVES_EN
NOUNS = NOUNS_EN
ACTIVITIES = ACTIVITIES_EN
YEARS = YEARS_EN
THEMES = THEMES_EN

def generate_event_name(style="default", locale="en"):
    """
    Generate a meaningful Secret Santa event name based on cultural references
    
    Args:
        style: Type of name to generate
            - "default": Adjective + Noun + Activity
            - "theme": Theme-based name
            - "year": Name with year
            - "funny": Extra adjective + noun combination
        locale: Language code
            - "en": English (default)
            - "es_MX": Spanish (Mexico)
            - "es_CR": Spanish (Costa Rica)
            - "es_CO": Spanish (Colombia)
            - "es_AR": Spanish (Argentina)
            - "es_ES": Spanish (Spain)
    
    Returns:
        str: Generated event name
    """
    # Select word lists based on locale
    if locale == 'es_MX':
        adjectives = ADJECTIVES_ES_MX
        nouns = NOUNS_ES_MX
        activities = ACTIVITIES_ES_MX
        years = ACTIVITIES_ES_MX  # Just year format
        themes = THEMES_ES_MX
    elif locale == 'es_CR':
        adjectives = ADJECTIVES_ES_CR
        nouns = NOUNS_ES_CR
        activities = ACTIVITIES_ES_CR
        years = ACTIVITIES_ES_CR
        themes = THEMES_ES_CR
    elif locale == 'es_CO':
        adjectives = ADJECTIVES_ES_CO
        nouns = NOUNS_ES_CO
        activities = ACTIVITIES_ES_CO
        years = ACTIVITIES_ES_CO
        themes = THEMES_ES_CO
    elif locale == 'es_AR':
        adjectives = ADJECTIVES_ES_AR
        nouns = NOUNS_ES_AR
        activities = ACTIVITIES_ES_AR
        years = ACTIVITIES_ES_AR
        themes = THEMES_ES_AR
    elif locale == 'es_ES':
        adjectives = ADJECTIVES_ES_ES
        nouns = NOUNS_ES_ES
        activities = ACTIVITIES_ES_ES
        years = ACTIVITIES_ES_ES
        themes = THEMES_ES_ES
    else:
        # English (default)
        adjectives = ADJECTIVES_EN
        nouns = NOUNS_EN
        activities = ACTIVITIES_EN
        years = YEARS_EN
        themes = THEMES_EN
    
    if style == "theme":
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
