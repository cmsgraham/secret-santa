"""
Fun nickname generator for Secret Santa participants
"""
import random

# Adjectives for nicknames
ADJECTIVES = [
    "Jolly", "Merry", "Festive", "Cheerful", "Snowy", "Frosty",
    "Sparkly", "Gleeful", "Magical", "Twinkling", "Cozy", "Warm",
    "Bright", "Happy", "Joyful", "Radiant", "Shiny", "Glittering",
    "Bouncy", "Giggly", "Peppy", "Chipper", "Perky", "Zippy",
    "Dashing", "Prancing", "Dancing", "Singing", "Whistling", "Humming"
]

# Nouns for nicknames
NOUNS = [
    "Snowflake", "Reindeer", "Elf", "Gingerbread", "Candy Cane",
    "Snowman", "Angel", "Star", "Bell", "Cookie", "Ornament",
    "Tinsel", "Wreath", "Stocking", "Mittens", "Scarf", "Sleigh",
    "Present", "Gift", "Ribbon", "Bow", "Penguin", "Polar Bear",
    "Hot Cocoa", "Marshmallow", "Sugarplum", "Nutcracker", "Drummer",
    "Caroler", "Shepherd", "Wise One", "Holly", "Ivy", "Pine Tree"
]

def generate_nickname():
    """Generate a fun random nickname"""
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    return f"{adjective} {noun}"

def get_random_nicknames(count=5):
    """Get multiple random nicknames"""
    nicknames = set()
    while len(nicknames) < count:
        nicknames.add(generate_nickname())
    return list(nicknames)
