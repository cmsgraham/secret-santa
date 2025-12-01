"""
Database models for language preferences

This file shows what needs to be added to models.py
"""

# Add to User model:
"""
class User(db.Model):
    # ... existing fields ...
    
    # New field for language preference
    preferred_language = db.Column(db.String(10), default='en', nullable=False)
    
    def set_language(self, locale):
        '''Set user's preferred language'''
        valid_locales = ['en', 'es_MX', 'es_CR', 'es_CO', 'es_AR', 'es_ES']
        if locale in valid_locales:
            self.preferred_language = locale
"""

# Add to Participant model:
"""
class Participant(db.Model):
    # ... existing fields ...
    
    # New field for language preference
    preferred_language = db.Column(db.String(10), default='en', nullable=False)
    
    def set_language(self, locale):
        '''Set participant's preferred language'''
        valid_locales = ['en', 'es_MX', 'es_CR', 'es_CO', 'es_AR', 'es_ES']
        if locale in valid_locales:
            self.preferred_language = locale
"""

# Add to Event model:
"""
class Event(db.Model):
    # ... existing fields ...
    
    # New field for default event language
    default_language = db.Column(db.String(10), default='en', nullable=False)
    
    def set_default_language(self, locale):
        '''Set event's default language'''
        valid_locales = ['en', 'es_MX', 'es_CR', 'es_CO', 'es_AR', 'es_ES']
        if locale in valid_locales:
            self.default_language = locale
"""
