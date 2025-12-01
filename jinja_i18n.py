"""
Jinja2 filters and globals for i18n integration
"""

from jinja2 import Environment
from i18n import get_translation, I18nContext


def add_i18n_to_jinja(app, locale='en'):
    """
    Add i18n functions and filters to Jinja2 environment
    """

    # Create translation context
    i18n_ctx = I18nContext(locale)

    # Register as global function
    app.jinja_env.globals['t'] = i18n_ctx.get
    app.jinja_env.globals['_'] = i18n_ctx.get  # Shorthand
    app.jinja_env.globals['locale'] = locale
    app.jinja_env.globals['SUPPORTED_LOCALES'] = [
        'en', 'es_MX', 'es_CR', 'es_CO', 'es_AR', 'es_ES'
    ]

    # Register filters
    def translate(key, **kwargs):
        return i18n_ctx.get(key, **kwargs)

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

    return i18n_ctx


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
