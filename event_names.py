"""
Funny and festive event name generator for Secret Santa
Supports English and Spanish (multiple regions)
"""
import random
import string

# English word lists
ADJECTIVES_EN = [
    "Jolly", "Merry", "Festive", "Magical", "Snowy", "Frosty", "Sparkly",
    "Cozy", "Cheery", "Joyful", "Bright", "Glittery", "Twinkling", "Dazzling",
    "Enchanted", "Delightful", "Whimsical", "Gleeful", "Radiant", "Blissful",
    "Epic", "Legendary", "Spectacular", "Magnificent", "Wonderful", "Fantastic",
    "Incredible", "Amazing", "Awesome", "Splendid", "Groovy", "Funky"
]

NOUNS_EN = [
    "Elves", "Reindeer", "Snowflakes", "Candy Canes", "Gingerbread", "Mittens",
    "Stockings", "Ornaments", "Presents", "Sleigh Bells", "Snowmen", "Angels",
    "Stars", "Carolers", "Nutcrackers", "Wreaths", "Tinsel", "Holly",
    "Mistletoe", "Penguins", "Polar Bears", "Hot Chocolate", "Cookies",
    "Fruitcake", "Eggnog", "Jingle Bells", "Santa's Helpers", "Toy Makers",
    "Gift Givers", "Snow Angels", "Ice Skaters", "Sledders", "Carolers"
]

ACTIVITIES_EN = [
    "Exchange", "Swap", "Party", "Celebration", "Gathering", "Fiesta",
    "Bash", "Shindig", "Soiree", "Jamboree", "Extravaganza", "Festival",
    "Bonanza", "Spectacular", "Gala", "Get-Together", "Meetup", "Reunion"
]

YEARS_EN = [
    "2025", "Twenty Twenty-Five", "MMXXV"
]

THEMES_EN = [
    "Winter Wonderland", "North Pole", "Santa's Workshop", "Candy Land",
    "Ice Palace", "Cozy Cabin", "Festive Forest", "Holiday Haven",
    "Jingle Junction", "Merry Manor", "Yuletide Yard", "Christmas Corner",
    "Snowy Summit", "Frosty Fields", "Twinkling Town", "Gift Grove"
]

# Spanish word lists (universal for all Spanish variants)
ADJECTIVES_ES = [
    "Alegre", "Festivo", "Mágico", "Nevado", "Helado", "Brillante",
    "Acogedor", "Jovial", "Radiante", "Reluciente", "Encantado", "Delicioso",
    "Épico", "Legendario", "Espectacular", "Magnífico", "Maravilloso", "Fantástico",
    "Increíble", "Sorprendente", "Fantástico", "Espléndido", "Groovy", "Funky"
]

NOUNS_ES = [
    "Elfos", "Renos", "Copos de Nieve", "Bastones de Caramelo", "Jengibre", "Mitones",
    "Calcetines", "Adornos", "Regalos", "Campanas", "Muñecos de Nieve", "Ángeles",
    "Estrellas", "Villancicos", "Cascanueces", "Coronas", "Oropel", "Acebo",
    "Muérdago", "Pingüinos", "Osos Polares", "Chocolate Caliente", "Galletas",
    "Turrón", "Ponche", "Campanillas", "Ayudantes de Papá Noel", "Hacedores de Juguetes",
    "Repartidores de Regalos", "Ángeles de Nieve", "Patinadores", "Trineos", "Cantores"
]

ACTIVITIES_ES = [
    "Intercambio", "Canje", "Fiesta", "Celebración", "Reunión", "Fiesta",
    "Juerga", "Sarao", "Velada", "Juerguecilla", "Extravagancia", "Festival",
    "Bonanza", "Espectáculo", "Gala", "Tertulia", "Encuentro", "Reencuentro"
]

YEARS_ES = [
    "2025", "Veinticinco", "MMXXV"
]

THEMES_ES = [
    "País de las Maravillas Invernal", "Polo Norte", "Taller de Papá Noel", "País de Dulces",
    "Palacio de Hielo", "Cabaña Acogedora", "Bosque Festivo", "Refugio Navideño",
    "Cruce de Campanillas", "Mansión Alegre", "Patio Yuletide", "Rincón Navideño",
    "Cumbre Nevada", "Campos Helados", "Pueblo Reluciente", "Bosque de Regalos"
]

# Legacy naming for backward compatibility
ADJECTIVES = ADJECTIVES_EN
NOUNS = NOUNS_EN
ACTIVITIES = ACTIVITIES_EN
YEARS = YEARS_EN
THEMES = THEMES_EN

def generate_event_name(style="default", locale="en"):
    """
    Generate a funny/festive Secret Santa event name
    
    Args:
        style: Type of name to generate
            - "default": Adjective + Noun + Activity
            - "theme": Theme-based name
            - "year": Name with year
            - "funny": Extra silly combination
        locale: Language code
            - "en": English (default)
            - "es_*": Spanish (all variants: es_MX, es_CR, es_CO, es_AR, es_ES)
    
    Returns:
        str: Generated event name
    """
    # Select word lists based on locale
    if locale and locale.startswith('es'):
        # Spanish for all variants (es_MX, es_CR, es_CO, es_AR, es_ES)
        adjectives = ADJECTIVES_ES
        nouns = NOUNS_ES
        activities = ACTIVITIES_ES
        years = YEARS_ES
        themes = THEMES_ES
        connector = "Secret Santa" if locale == "es_AR" else "Secret Santa"  # Same for all variants
    else:
        # English (default)
        adjectives = ADJECTIVES_EN
        nouns = NOUNS_EN
        activities = ACTIVITIES_EN
        years = YEARS_EN
        themes = THEMES_EN
    
    if style == "theme":
        theme = random.choice(themes)
        activity = random.choice(activities)
        return f"{theme} Secret Santa {activity}"
    
    elif style == "year":
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        year = random.choice(years)
        return f"{adjective} {noun} {year}"
    
    elif style == "funny":
        adj1 = random.choice(adjectives)
        adj2 = random.choice(adjectives)
        noun = random.choice(nouns)
        activity = random.choice(activities)
        if locale and locale.startswith('es'):
            return f"El/La {adj1} {adj2} {noun} {activity}"
        else:
            return f"The {adj1} {adj2} {noun} {activity}"
    
    else:  # default
        adjective = random.choice(adjectives)
        noun = random.choice(nouns)
        activity = random.choice(activities)
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
