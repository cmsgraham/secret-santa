"""
Language Switch API Endpoints Documentation

This file documents the API endpoints needed for language switching.
Add these to app_v2.py
"""

# API ENDPOINT: Set Language Preference
"""
@app.route('/api/language/set', methods=['POST'])
def set_language():
    '''
    Set user's language preference
    
    Request:
    {
        "language": "es_MX"
    }
    
    Response:
    {
        "success": true,
        "message": "Language preference updated",
        "language": "es_MX"
    }
    '''
    from i18n import SUPPORTED_LOCALES
    
    try:
        data = request.get_json()
        language = data.get('language', 'en')
        
        if language not in SUPPORTED_LOCALES:
            return jsonify({
                'success': False,
                'error': f'Unsupported language: {language}'
            }), 400
        
        # Store in session
        session['language'] = language
        
        # If user is logged in, update their preference in database
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user:
                user.preferred_language = language
                db.session.commit()
        
        # If participant is logged in, update their preference
        if 'participant_id' in session:
            participant = Participant.query.get(session['participant_id'])
            if participant:
                participant.preferred_language = language
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Language preference updated',
            'language': language
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# API ENDPOINT: Get Supported Languages
"""
@app.route('/api/languages', methods=['GET'])
def get_languages():
    '''
    Get list of supported languages
    
    Response:
    {
        "success": true,
        "languages": [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "flag": "🇺🇸",
                "region": "Global"
            },
            {
                "code": "es_MX",
                "name": "Spanish (Mexico)",
                "native_name": "Español (México)",
                "flag": "🇲🇽",
                "region": "Mexico"
            },
            ...
        ],
        "current": "en"
    }
    '''
    from language_selector import LANGUAGES
    
    languages = []
    for code, info in LANGUAGES.items():
        languages.append({
            'code': code,
            'name': info['name'],
            'native_name': info['native_name'],
            'flag': info['flag'],
            'region': info['region']
        })
    
    current_language = session.get('language', 'en')
    
    return jsonify({
        'success': True,
        'languages': languages,
        'current': current_language
    })
"""


# MIDDLEWARE: Language Detection
"""
Add before_request handler to detect and set language:

@app.before_request
def detect_language():
    '''Detect language from session, user preference, or Accept-Language header'''
    from i18n import detect_locale_from_header
    
    # Check session first
    if 'language' in session:
        g.locale = session['language']
        return
    
    # Check user preference
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user and user.preferred_language:
            g.locale = user.preferred_language
            session['language'] = user.preferred_language
            return
    
    # Check participant preference
    if 'participant_id' in session:
        participant = Participant.query.get(session['participant_id'])
        if participant and participant.preferred_language:
            g.locale = participant.preferred_language
            session['language'] = participant.preferred_language
            return
    
    # Detect from Accept-Language header
    g.locale = detect_locale_from_header(request.headers.get('Accept-Language', ''))
    session['language'] = g.locale
"""


# TEMPLATE USAGE:
"""
In templates, use these patterns:

<!-- Simple translation -->
{{ t('button_yes') }}
{{ _('button_no') }}

<!-- Translation with variables -->
{{ t('warning_need_participants', min_count=3, remaining=2) }}

<!-- Get language name -->
{{ current_locale|language_name }}

<!-- Get language flag -->
{{ current_locale|language_flag }}

<!-- Language selector dropdown -->
{% include 'components/language_selector.html' %}
"""
