"""
Jinja2 filters and globals for i18n integration
"""

from jinja2 import Environment
from flask import g
from i18n import get_translation, I18nContext, DEFAULT_LOCALE


def add_i18n_to_jinja(app, locale='en'):
    """
    Add i18n functions and filters to Jinja2 environment
    """

    # Create default translation context (for fallback only)
    default_i18n_ctx = I18nContext(locale)

    # Create request-aware translation functions
    def get_current_locale():
        """Get the current locale from Flask's request context"""
        return g.get('locale', DEFAULT_LOCALE)

    def t_func(key, **kwargs):
        """Translate using current request's locale"""
        current_locale = get_current_locale()
        return get_translation(key, current_locale, **kwargs)

    def _func(key, **kwargs):
        """Shorthand for t_func"""
        return t_func(key, **kwargs)

    # Register as global functions (these will be called at render time with current locale)
    app.jinja_env.globals['t'] = t_func
    app.jinja_env.globals['_'] = _func
    # NOTE: 'locale' and 'SUPPORTED_LOCALES' are now injected per-request via context_processor
    # Do NOT set them as static globals here, as they would override context_processor values

    # Register filters
    def translate(key, **kwargs):
        """Filter for translations - uses current request's locale"""
        return t_func(key, **kwargs)

    def language_name(locale_code):
        """Get native name of language"""
        from language_selector import LANGUAGES
        lang = LANGUAGES.get(locale_code)
        return lang['native_name'] if lang else locale_code

    def language_flag(locale_code):
        """Get flag emoji for language"""
        from language_selector import LANGUAGES
        lang = LANGUAGES.get(locale_code)
        return lang['flag'] if lang else '🌍'

    app.jinja_env.filters['t'] = translate
    app.jinja_env.filters['language_name'] = language_name
    app.jinja_env.filters['language_flag'] = language_flag

    return default_i18n_ctx


def create_language_selector_macro():
    """
    Create Jinja2 macro for language selector
    """
    return """
    {%- macro language_selector(current_locale) -%}
        <div class="language-selector">
            <span class="current-language">
                {{ current_locale|language_flag }} {{ current_locale|language_name }}
            </span>
            <div class="language-dropdown">
                {% for locale_code in SUPPORTED_LOCALES %}
                    <a href="#" data-language="{{ locale_code }}" class="language-option {% if locale_code == current_locale %}active{% endif %}">
                        {{ locale_code|language_flag }} {{ locale_code|language_name }}
                    </a>
                {% endfor %}
            </div>
        </div>
    {%- endmacro -%}
    """


__all__ = [
    'add_i18n_to_jinja',
    'create_language_selector_macro',
]
