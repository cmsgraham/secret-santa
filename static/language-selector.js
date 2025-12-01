/**
 * Language Selector JavaScript
 * Handles language switching UI and API calls
 */

(function() {
    'use strict';

    // Initialize language selector
    document.addEventListener('DOMContentLoaded', function() {
        initLanguageSelector();
    });

    function initLanguageSelector() {
        const selector = document.querySelector('.language-selector');
        if (!selector) return;

        const currentLanguage = selector.querySelector('.current-language');
        const languageOptions = selector.querySelectorAll('.language-option');

        // Toggle dropdown on click
        if (currentLanguage) {
            currentLanguage.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                selector.classList.toggle('active');
            });
        }

        // Handle language selection
        languageOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const languageCode = this.dataset.language;
                switchLanguage(languageCode);
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!selector.contains(e.target)) {
                selector.classList.remove('active');
            }
        });
    }

    function switchLanguage(languageCode) {
        // Show loading state
        const selector = document.querySelector('.language-selector');
        if (selector) {
            selector.style.opacity = '0.6';
            selector.style.pointerEvents = 'none';
        }

        // Send request to backend
        fetch('/api/language/set', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                language: languageCode
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload page to apply new language
                window.location.reload();
            } else {
                showError('Failed to change language: ' + (data.error || 'Unknown error'));
                resetSelector();
            }
        })
        .catch(error => {
            console.error('Language switch error:', error);
            showError('Error changing language. Please try again.');
            resetSelector();
        });
    }

    function resetSelector() {
        const selector = document.querySelector('.language-selector');
        if (selector) {
            selector.style.opacity = '1';
            selector.style.pointerEvents = 'auto';
            selector.classList.remove('active');
        }
    }

    function showError(message) {
        // Use alert for now, can be replaced with toast notification
        console.error(message);
    }

    // Expose functions globally if needed
    window.languageSelector = {
        switchLanguage: switchLanguage,
        initLanguageSelector: initLanguageSelector
    };
})();
