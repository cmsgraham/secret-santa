"""
Language switcher utilities for Secret Santa app
"""

from typing import Optional, Dict, List, Tuple

# Language display names and metadata
LANGUAGES = {
    'en': {
        'name': 'English',
        'native_name': 'English',
        'flag': '🇺🇸',
        'region': 'Global',
    },
    'es_MX': {
        'name': 'Spanish (Mexico)',
        'native_name': 'Español (México)',
        'flag': '🇲🇽',
        'region': 'Mexico',
    },
    'es_CR': {
        'name': 'Spanish (Costa Rica)',
        'native_name': 'Español (Costa Rica)',
        'flag': '🇨🇷',
        'region': 'Costa Rica',
    },
    'es_CO': {
        'name': 'Spanish (Colombia)',
        'native_name': 'Español (Colombia)',
        'flag': '🇨🇴',
        'region': 'Colombia',
    },
    'es_AR': {
        'name': 'Spanish (Argentina)',
        'native_name': 'Español (Argentina)',
        'flag': '🇦🇷',
        'region': 'Argentina',
    },
    'es_ES': {
        'name': 'Spanish (Spain)',
        'native_name': 'Español (España)',
        'flag': '🇪🇸',
        'region': 'Spain',
    },
}


def get_language_list() -> List[Tuple[str, str, str]]:
    """
    Get list of available languages as (code, display_name, flag) tuples
    """
    return [
        (code, info['native_name'], info['flag'])
        for code, info in LANGUAGES.items()
    ]


def get_language_info(locale: str) -> Optional[Dict]:
    """Get metadata for a language"""
    return LANGUAGES.get(locale)


def format_language_selector(current_locale: str) -> str:
    """
    Generate HTML for language selector dropdown
    """
    html_parts = ['<div class="language-selector">']
    html_parts.append(f'  <span class="current-language">{LANGUAGES[current_locale]["flag"]} {LANGUAGES[current_locale]["native_name"]}</span>')
    html_parts.append('  <div class="language-dropdown">')

    for code, name, flag in get_language_list():
        is_current = 'active' if code == current_locale else ''
        html_parts.append(f'    <a href="#" data-language="{code}" class="language-option {is_current}">')
        html_parts.append(f'      {flag} {name}')
        html_parts.append('    </a>')

    html_parts.append('  </div>')
    html_parts.append('</div>')

    return '\n'.join(html_parts)


__all__ = [
    'LANGUAGES',
    'get_language_list',
    'get_language_info',
    'format_language_selector',
]
