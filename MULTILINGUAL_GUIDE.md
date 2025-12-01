# Multilingual Implementation Guide

## ✅ Completed

### Infrastructure (Commit: a24335e)
- ✅ Translation files for 6 locales (EN, ES-MX, ES-CR, ES-CO, ES-AR, ES-ES)
- ✅ i18n.py module with locale detection and translation loading
- ✅ Caching for performance

### UI & API (Commit: 2f0696d)
- ✅ Language selector dropdown component
- ✅ CSS styling (desktop & mobile responsive)
- ✅ JavaScript for interactive switching
- ✅ API endpoint documentation
- ✅ Reusable template component

### Flask Integration (Commit: 45e5bef)
- ✅ Database models updated with `preferred_language` fields
- ✅ Language detection middleware (@app.before_request)
- ✅ API endpoints implemented:
  - POST /api/language/set
  - GET /api/languages
- ✅ Jinja2 integration with t() filters

## 🚀 Next Steps to Activate

### 1. Add Language Selector to Templates

Add this line to your base template or main header:
```html
{% include 'components/language_selector.html' %}
```

Or use the comprehensive nav example:
```html
{% include 'components/nav_with_language.html' %}
```

### 2. Update Template Examples

In any template, use translations like this:
```html
<!-- Simple translation -->
<h1>{{ t('page_title_manage_event', event_name=event.name) }}</h1>

<!-- Without variables -->
<button>{{ t('button_yes') }}</button>

<!-- In JavaScript -->
<script>
    const message = "{{ t('success_message_draw', message='Draw completed!') }}";
</script>
```

### 3. Template Filters Available

```html
<!-- Get translated text -->
{{ t('key_name') }}
{{ _('key_name') }}  <!-- Shorthand -->

<!-- Get language metadata -->
{{ 'es_MX'|language_name }}     <!-- Output: Español (México) -->
{{ 'es_MX'|language_flag }}     <!-- Output: 🇲🇽 -->

<!-- Get current locale -->
<meta name="lang" content="{{ locale }}">
```

### 4. API Usage Examples

```javascript
// Get supported languages
fetch('/api/languages')
  .then(r => r.json())
  .then(data => {
    console.log(data.languages);  // All available languages
    console.log(data.current);    // Current language code
  });

// Switch language
fetch('/api/language/set', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ language: 'es_MX' })
})
.then(r => r.json())
.then(d => {
  if (d.success) {
    window.location.reload();  // Reload to apply language
  }
});
```

### 5. Backend Usage Examples

In Flask routes:
```python
from flask import g

@app.route('/example')
def example():
    # g.locale contains the current language
    print(f"Current language: {g.locale}")
    
    # Render template with i18n
    return render_template('example.html')
```

## 🔄 Language Detection Priority

The app detects language in this order:
1. Session language (user explicitly selected)
2. User's preferred_language (from database)
3. Participant's preferred_language (from database)
4. Accept-Language header (browser default)
5. English (fallback)

## 📝 Adding New Translation Keys

To add new translation keys:

1. Add to each translation file in `translations/*/messages.json`:
```json
{
  "new_feature_title": "Feature Title",
  "new_feature_description": "Feature description"
}
```

2. Use in templates:
```html
<h2>{{ t('new_feature_title') }}</h2>
<p>{{ t('new_feature_description') }}</p>
```

## 🌍 Supported Locales

```
en         - English (Global)
es_MX      - Spanish (Mexico)
es_CR      - Spanish (Costa Rica)
es_CO      - Spanish (Colombia)
es_AR      - Spanish (Argentina)
es_ES      - Spanish (Spain)
```

## 🔧 Customization

### Modifying Language Selector Placement
The language selector is a standalone component. Place it anywhere:
- Navigation bar (navbar)
- Footer
- Settings page
- Header section

### Changing Default Language
In `i18n.py`:
```python
DEFAULT_LOCALE = 'en'  # Change this
```

### Adding More Languages
1. Create new folder: `translations/es_VE/` (Venezuela example)
2. Copy messages.json from another Spanish locale
3. Update translations as needed
4. Add to SUPPORTED_LOCALES in i18n.py
5. Add to COUNTRY_TO_LOCALE mapping
6. Add to LANGUAGES in language_selector.py

## 🐛 Troubleshooting

### Language not changing
- Clear browser cache (Cmd+Shift+R or Ctrl+Shift+Del)
- Check browser console for errors
- Verify /api/language/set endpoint returns success

### Translations not showing
- Check browser console for 404 errors
- Verify translation key exists in `translations/*/messages.json`
- Ensure template uses `{{ t('key_name') }}` syntax

### Wrong language detected
- Check Accept-Language header: Right-click > Inspect > Network > Headers
- Manually switch via language selector
- Language preference saved in database for future visits

## 📦 Files Modified/Created

```
Created:
  - i18n.py                              (i18n core module)
  - language_selector.py                 (language metadata)
  - jinja_i18n.py                        (Jinja2 integration)
  - static/language-selector.css         (styles)
  - static/language-selector.js          (interactions)
  - templates/components/language_selector.html
  - templates/components/nav_with_language.html
  - translations/en/messages.json        (English)
  - translations/es_MX/messages.json     (Mexican Spanish)
  - translations/es_CR/messages.json     (Costa Rican Spanish)
  - translations/es_CO/messages.json     (Colombian Spanish)
  - translations/es_AR/messages.json     (Argentine Spanish)
  - translations/es_ES/messages.json     (Castilian Spanish)
  - LANGUAGE_API.md                      (API documentation)
  - LANGUAGE_MODELS.md                   (Database notes)

Modified:
  - models.py                            (added preferred_language fields)
  - app_v2.py                            (added middleware & API endpoints)
```

## 🎯 Features Summary

✅ **Automatic Detection**
- Detects browser language from Accept-Language header
- Maps country codes to regional Spanish variants
- Falls back to English for unknown languages

✅ **User Preferences**
- Stores language preference in database
- Persists across sessions and devices
- User can manually switch at any time

✅ **UI Components**
- Interactive dropdown with flag emojis
- Mobile-responsive design
- Smooth animations

✅ **Template Integration**
- t() function for translations
- Filter support (language_name, language_flag)
- Template variables with {{ variable }} syntax

✅ **API Support**
- Get list of supported languages
- Set user's language preference
- Manage language at runtime

## 📊 Translation Coverage

Each locale includes 100+ translation keys covering:
- Navigation & UI elements
- Event management actions
- Participant workflow
- Guessing phase
- Gift ideas & comments
- Validation messages
- API errors
- Date/time formatting
- Button labels

---

**Status**: Ready for production deployment ✅
