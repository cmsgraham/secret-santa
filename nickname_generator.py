"""
Fun nickname generator for Secret Santa participants
Supports English and Spanish (multiple regions)
"""
import random

# English adjectives for nicknames
ADJECTIVES_EN = [
    "Jolly", "Merry", "Festive", "Cheerful", "Snowy", "Frosty",
    "Sparkly", "Gleeful", "Magical", "Twinkling", "Cozy", "Warm",
    "Bright", "Happy", "Joyful", "Radiant", "Shiny", "Glittering",
    "Bouncy", "Giggly", "Peppy", "Chipper", "Perky", "Zippy",
    "Dashing", "Prancing", "Dancing", "Singing", "Whistling", "Humming"
]

# English nouns for nicknames
NOUNS_EN = [
    "Snowflake", "Reindeer", "Elf", "Gingerbread", "Candy Cane",
    "Snowman", "Angel", "Star", "Bell", "Cookie", "Ornament",
    "Tinsel", "Wreath", "Stocking", "Mittens", "Scarf", "Sleigh",
    "Present", "Gift", "Ribbon", "Bow", "Penguin", "Polar Bear",
    "Hot Cocoa", "Marshmallow", "Sugarplum", "Nutcracker", "Drummer",
    "Caroler", "Shepherd", "Wise One", "Holly", "Ivy", "Pine Tree"
]

# Spanish adjectives for nicknames
ADJECTIVES_ES = [
    "Alegre", "Festivo", "Dichoso", "Nevado", "Helado",
    "Brillante", "Jovial", "Mágico", "Reluciente", "Acogedor", "Cálido",
    "Radiante", "Brillante", "Feliz", "Gozoso", "Resplandeciente", "Centelleante",
    "Saltarín", "Risueño", "Animado", "Vivaz", "Juguetón", "Ágil",
    "Galante", "Danzarín", "Bailarín", "Cantarín", "Silbador", "Tararearín"
]

# Spanish nouns for nicknames
NOUNS_ES = [
    "Copo de Nieve", "Reno", "Elfo", "Jengibre", "Bastón de Caramelo",
    "Muñeco de Nieve", "Ángel", "Estrella", "Campana", "Galleta", "Adorno",
    "Oropel", "Corona", "Calcetín", "Mitones", "Bufanda", "Trineo",
    "Regalo", "Don", "Lazo", "Moño", "Pingüino", "Oso Polar",
    "Chocolate Caliente", "Malvavisco", "Golosina", "Cascanueces", "Tambor",
    "Cantador", "Pastor", "Sabio", "Acebo", "Hiedra", "Árbol de Pino"
]

# Legacy naming for backward compatibility
ADJECTIVES = ADJECTIVES_EN
NOUNS = NOUNS_EN

def generate_nickname(locale="en"):
    """
    Generate a fun random nickname
    
    Args:
        locale: Language code
            - "en": English (default)
            - "es_*": Spanish (all variants: es_MX, es_CR, es_CO, es_AR, es_ES)
    
    Returns:
        str: Generated nickname
    """
    if locale and locale.startswith('es'):
        # Spanish for all variants (es_MX, es_CR, es_CO, es_AR, es_ES)
        adjective = random.choice(ADJECTIVES_ES)
        noun = random.choice(NOUNS_ES)
    else:
        # English (default)
        adjective = random.choice(ADJECTIVES_EN)
        noun = random.choice(NOUNS_EN)
    
    return f"{adjective} {noun}"

def get_random_nicknames(count=5, locale="en"):
    """
    Get multiple random nicknames
    
    Args:
        count: Number of nicknames to generate
        locale: Language code (default "en")
    
    Returns:
        list: List of generated nicknames
    """
    nicknames = set()
    while len(nicknames) < count:
        nicknames.add(generate_nickname(locale=locale))
    return list(nicknames)
