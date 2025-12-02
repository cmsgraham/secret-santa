"""
Fun nickname generator for Secret Santa participants
Uses famous characters and personalities from each country
"""
import random

# English - Famous characters and personalities
ADJECTIVES_EN = [
    "Super", "Magical", "Lucky", "Jolly", "Happy", "Brilliant", "Clever"
]

NOUNS_EN = [
    "Santa", "Rudolph", "Buddy", "Krampus", "Mrs. Claus", "Elf", "Scrooge",
    "Jack Frost", "Frosty", "Grinch", "Mariah Carey", "Kevin McCallister",
    "Clark Griswold", "Ralphie", "George Bailey", "Ebenezer"
]

# Legacy naming for backward compatibility
ADJECTIVES_EN_LEGACY = [
    "Jolly", "Merry", "Festive", "Cheerful", "Snowy", "Frosty",
    "Sparkly", "Gleeful", "Magical", "Twinkling", "Cozy", "Warm",
    "Bright", "Happy", "Joyful", "Radiant", "Shiny", "Glittering",
    "Bouncy", "Giggly", "Peppy", "Chipper", "Perky", "Zippy",
    "Dashing", "Prancing", "Dancing", "Singing", "Whistling", "Humming"
]

NOUNS_EN_LEGACY = [
    "Snowflake", "Reindeer", "Elf", "Gingerbread", "Candy Cane",
    "Snowman", "Angel", "Star", "Bell", "Cookie", "Ornament",
    "Tinsel", "Wreath", "Stocking", "Mittens", "Scarf", "Sleigh",
    "Present", "Gift", "Ribbon", "Bow", "Penguin", "Polar Bear",
    "Hot Cocoa", "Marshmallow", "Sugarplum", "Nutcracker", "Drummer",
    "Caroler", "Shepherd", "Wise One", "Holly", "Ivy", "Pine Tree"
]

# Mexico - Famous characters from Mexican culture
ADJECTIVES_ES_MX = [
    "Super", "Mágico", "Alegre", "Travieso", "Ingenioso", "Astuto", "Valiente"
]

NOUNS_ES_MX = [
    "Cantinflas", "Chespirito", "El Chavo", "Quico", "Doña Florinda",
    "Don Ramón", "Kalimba", "Speedy González", "Pancho Villa", "La Catrina",
    "Frida Kahlo", "Diego Rivera", "Mariachi", "Lucha Libre", "Godzilla",
    "El Santo", "Pelé", "Guillermo del Toro", "Salma Hayek", "Emiliano Zapata"
]

# Costa Rica - Famous Costa Rican characters and personalities
ADJECTIVES_ES_CR = [
    "Super", "Mágico", "Tico", "Alegre", "Travieso", "Ingenioso", "Valiente"
]

NOUNS_ES_CR = [
    "Pura Vida", "Tico", "Caballero de la Noche", "Oscar Arias", "Presidente",
    "Don Pepe", "Manuel de Jesús", "Arenal", "Tarzan", "Sloth",
    "Howler Monkey", "Quetzal", "Papagayo", "Eco-Warrior", "Ecoturista",
    "Campesino", "Carero", "Bribri", "Cabécar", "Boruca"
]

# Colombia - Famous Colombian characters and personalities
ADJECTIVES_ES_CO = [
    "Super", "Mágico", "Alegre", "Travieso", "Ingenioso", "Picante", "Valiente"
]

NOUNS_ES_CO = [
    "Gabriel García Márquez", "Fernando Botero", "Shakira", "Juanes",
    "Juan Pablo Montoya", "Colombiana", "Vallenato", "Cumbiambero",
    "Paciencia", "Narino", "Bolívar", "José Martí", "Che Guevara",
    "Gaitero", "Zapatista", "Cafe Juan", "Cartagenero", "Medellín",
    "Cali Salsa", "Picaro"
]

# Argentina - Famous Argentine characters and personalities
ADJECTIVES_ES_AR = [
    "Super", "Mágico", "Boludo", "Astuto", "Ingenioso", "Picante", "Valiente"
]

NOUNS_ES_AR = [
    "Maradona", "Messi", "Evita", "Juan Perón", "Jorge Luis Borges",
    "Carlos Gardel", "Tanguero", "Gauchos", "Borracho", "Diego",
    "Che Guevara", "Alfonsina", "Cortázar", "Piazzolla", "Tango",
    "Bonaerense", "Porteño", "Cocoliche", "Lunfardo", "Fierro"
]

# Spain - Famous Spanish characters and personalities
ADJECTIVES_ES_ES = [
    "Super", "Mágico", "Español", "Alegre", "Travieso", "Ingenioso", "Valiente"
]

NOUNS_ES_ES = [
    "Don Quijote", "Sancho Panza", "El Cid", "Zorro", "Cervantes",
    "Dalí", "Picasso", "Gaudí", "Lorca", "Goya",
    "Pablo Casals", "Almodóvar", "Iglesias", "Antonio Banderas",
    "Carmen", "Don Aníbal", "Flamenco", "Matador", "Bullfighter",
    "Manchego", "Toledano"
]

# Legacy naming for backward compatibility
ADJECTIVES = ADJECTIVES_EN
NOUNS = NOUNS_EN

def generate_nickname(locale="en"):
    """
    Generate a fun random nickname using famous characters and personalities
    
    Args:
        locale: Language code
            - "en": English (default) - Famous Christmas/movie characters
            - "es_MX": Spanish (Mexico) - Famous Mexican characters
            - "es_CR": Spanish (Costa Rica) - Costa Rican personalities
            - "es_CO": Spanish (Colombia) - Colombian personalities
            - "es_AR": Spanish (Argentina) - Argentine personalities
            - "es_ES": Spanish (Spain) - Spanish personalities
    
    Returns:
        str: Generated nickname using a famous character name
    """
    if locale == 'es_MX':
        adjective = random.choice(ADJECTIVES_ES_MX)
        noun = random.choice(NOUNS_ES_MX)
    elif locale == 'es_CR':
        adjective = random.choice(ADJECTIVES_ES_CR)
        noun = random.choice(NOUNS_ES_CR)
    elif locale == 'es_CO':
        adjective = random.choice(ADJECTIVES_ES_CO)
        noun = random.choice(NOUNS_ES_CO)
    elif locale == 'es_AR':
        adjective = random.choice(ADJECTIVES_ES_AR)
        noun = random.choice(NOUNS_ES_AR)
    elif locale == 'es_ES':
        adjective = random.choice(ADJECTIVES_ES_ES)
        noun = random.choice(NOUNS_ES_ES)
    else:
        # English (default)
        adjective = random.choice(ADJECTIVES_EN)
        noun = random.choice(NOUNS_EN)
    
    return f"{adjective} {noun}"

def get_random_nicknames(count=5, locale="en"):
    """
    Get multiple random nicknames using famous characters
    
    Args:
        count: Number of nicknames to generate
        locale: Language code (default "en")
    
    Returns:
        list: List of generated nicknames
    """
    nicknames = set()
    attempts = 0
    max_attempts = count * 10  # Prevent infinite loop
    
    while len(nicknames) < count and attempts < max_attempts:
        nickname = generate_nickname(locale=locale)
        nicknames.add(nickname)
        attempts += 1
    
    return list(nicknames)[:count]
