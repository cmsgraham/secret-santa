# Quick Update Examples

## How to Add New Event Names

### Example 1: Add a new Spanish Mexico event name

**File**: `config/event_names.json`

Find the `es_MX` section and add to the `nouns` array:

```json
"es_MX": {
  "adjectives": ["Festivo", "Navideño", ...],
  "nouns": [
    "Posadas",
    "Navidad",
    "Intercambio Navideño",
    "Tu Nuevo Nombre Aquí"  // ← Add here
  ],
  ...
}
```

**Result**: Next time an event name is generated in Spanish (Mexico), it might create:
- "Mágico Tu Nuevo Nombre Aquí 2025"
- "Colorido Tu Nuevo Nombre Aquí de Celebración"

### Example 2: Add an English theme

**File**: `config/event_names.json`

Find the `en` section and add to the `themes` array:

```json
"en": {
  "adjectives": [...],
  "nouns": [...],
  "activities": [...],
  "themes": [
    "Winter Wonderland Secret Santa",
    "My Awesome New Theme 2025"  // ← Add here
  ]
}
```

## How to Add New Nicknames

### Example 1: Add Colombian nickname

**File**: `config/nicknames.json`

Find the `es_CO` array and add a new entry:

```json
"es_CO": [
  "Super Gabriel García Márquez",
  "Mágico Fernando Botero",
  "Nuevo Nombre Aquí",  // ← Add here
  ...
]
```

### Example 2: Add English Christmas character

**File**: `config/nicknames.json`

Find the `en` array:

```json
"en": [
  "Super Santa",
  "Magical Rudolph",
  "My New Character Here",  // ← Add here
  ...
]
```

## Adding Multiple Names at Once

Edit the configuration files in your text editor, then commit:

```bash
git add config/event_names.json config/nicknames.json
git commit -m "config: add spring festival themes and new character names"
git push origin main
```

The production server will automatically pull and use the new names on the next deployment.

## Testing Your Changes (Optional)

Before committing, test locally:

```bash
python3 << 'EOF'
from event_names import get_random_event_names
from nickname_generator import get_random_nicknames

# Test your changes
print("Event names:", get_random_event_names(5, locale="es_MX"))
print("Nicknames:", get_random_nicknames(5, locale="es_MX"))
EOF
```

## Important Notes

⚠️ **Keep JSON Valid**
- All strings must be in double quotes
- Arrays end with commas between items (but not after the last item)
- No trailing commas after the last item in arrays
- All braces `{}` and brackets `[]` must match

✅ **Good**:
```json
{
  "en": ["Name1", "Name2", "Name3"]
}
```

❌ **Bad**:
```json
{
  "en": ["Name1", "Name2", "Name3",]  // Trailing comma!
}
```

## How Changes Appear

Changes you make to the JSON files will:
1. **Immediately affect** event name and nickname generation when you create new events
2. **Not affect** already-created events (they keep their original generated names)
3. **Apply globally** to all users creating events in that language

## Rolling Back

If you make a mistake, you can revert to the previous version:

```bash
git revert HEAD  # Undo last change
git push origin main  # Deploy the revert
```

Or manually edit the file and commit again with corrections.

