"""
Internationalization (i18n) module for Secret Santa app
Supports English and Spanish variants by region
"""

import json
import os
from typing import Dict, Optional, Any
from functools import lru_cache

# Country to locale mapping
COUNTRY_TO_LOCALE = {
    'MX': 'es_MX',  # Mexico
    'CR': 'es_CR',  # Costa Rica
    'CO': 'es_CO',  # Colombia
    'AR': 'es_AR',  # Argentina
    'ES': 'es_ES',  # Spain
    'US': 'en',     # United States
    'CA': 'en',     # Canada
    'GB': 'en',     # United Kingdom
}

# Supported locales
SUPPORTED_LOCALES = [
    'en',
    'es_MX',
    'es_CR',
    'es_CO',
    'es_AR',
    'es_ES',
]

# Default locale
DEFAULT_LOCALE = 'en'


@lru_cache(maxsize=32)
def load_translations(locale: str) -> Dict[str, Any]:
    """
    Load translation file for given locale.
    Falls back to English if locale not found.
    """
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE

    translation_file = os.path.join(
        os.path.dirname(__file__),
        'translations',
        locale,
        'messages.json'
    )

    try:
        with open(translation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback to default locale
        default_file = os.path.join(
            os.path.dirname(__file__),
            'translations',
            DEFAULT_LOCALE,
            'messages.json'
        )
        with open(default_file, 'r', encoding='utf-8') as f:
            return json.load(f)


def detect_locale_from_country(country_code: Optional[str]) -> str:
    """
    Detect locale from country code.
    Returns mapped locale or default.
    """
    if not country_code:
        return DEFAULT_LOCALE

    country_code = country_code.upper()
    return COUNTRY_TO_LOCALE.get(country_code, DEFAULT_LOCALE)


def detect_locale_from_header(accept_language: Optional[str]) -> str:
    """
    Detect locale from Accept-Language header.
    Parses header and maps to supported locales.
    """
    if not accept_language:
        return DEFAULT_LOCALE

    # Parse Accept-Language header
    # Format: "es-MX,es;q=0.9,en;q=0.8"
    languages = accept_language.lower().split(',')

    for lang in languages:
        # Get language code (before semicolon if present)
        lang = lang.split(';')[0].strip()

        # Map language-country to locale
        if '-' in lang:
            language, country = lang.split('-')
            locale = COUNTRY_TO_LOCALE.get(country.upper(), f'{language}_{country.upper()}')
        else:
            locale = language

        # Check if supported
        if locale in SUPPORTED_LOCALES:
            return locale

        # Try to find Spanish variant match
        if locale == 'es':
            # Return default Spanish (Mexico)
            return 'es_MX'

    return DEFAULT_LOCALE


def get_translation(key: str, locale: str = DEFAULT_LOCALE, **kwargs) -> str:
    """
    Get translated string for key in given locale.
    Supports template variables with {{ variable }} syntax.
    """
    translations = load_translations(locale)

    # Get the translation or use key as fallback
    text = translations.get(key, key)

    # Replace template variables
    if kwargs:
        # Replace {{ variable }} with values from kwargs
        for var_name, var_value in kwargs.items():
            text = text.replace('{{ ' + var_name + ' }}', str(var_value))

    return text


def t(key: str, locale: str = DEFAULT_LOCALE, **kwargs) -> str:
    """
    Shorthand for get_translation
    """
    return get_translation(key, locale, **kwargs)


class I18nContext:
    """
    Context manager for handling i18n in request scope
    """

    def __init__(self, locale: str = DEFAULT_LOCALE):
        self.locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
        self.translations = load_translations(self.locale)

    def get(self, key: str, **kwargs) -> str:
        """Get translation in this context's locale"""
        text = self.translations.get(key, key)

        if kwargs:
            for var_name, var_value in kwargs.items():
                text = text.replace('{{ ' + var_name + ' }}', str(var_value))

        return text

    def __call__(self, key: str, **kwargs) -> str:
        """Allow calling context as function"""
        return self.get(key, **kwargs)


# Export main functions
__all__ = [
    'load_translations',
    'detect_locale_from_country',
    'detect_locale_from_header',
    'get_translation',
    't',
    'I18nContext',
    'SUPPORTED_LOCALES',
    'DEFAULT_LOCALE',
    'COUNTRY_TO_LOCALE',
]
