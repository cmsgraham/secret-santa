document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('secretSantaForm');
    const assignBtn = document.getElementById('assignBtn');
    const btnText = document.getElementById('btnText');
    const spinner = document.getElementById('spinner');
    const result = document.getElementById('result');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Disable button and show spinner
        assignBtn.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'inline-block';
        result.style.display = 'none';
        
        // Get form data
        const formData = {
            emails: document.getElementById('emails').value,
            sender_email: document.getElementById('senderEmail').value,
            event_name: document.getElementById('eventName').value
        };
        
        try {
            const response = await fetch('/assign', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            // Show result
            result.style.display = 'block';
            result.className = `result ${data.success ? 'success' : 'error'}`;
            
            if (data.success) {
                result.innerHTML = `<p>${data.message}</p>`;
                form.reset();
            } else {
                result.innerHTML = `<p>${data.error}</p>`;
            }
            
        } catch (error) {
            result.style.display = 'block';
            result.className = 'result error';
            result.textContent = 'An error occurred. Please try again.';
        } finally {
            // Re-enable button and hide spinner
            assignBtn.disabled = false;
            btnText.style.display = 'inline-block';
            spinner.style.display = 'none';
        }
    });
    
    // Auto-resize textarea
    const textarea = document.getElementById('emails');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = this.scrollHeight + 'px';
    });
});