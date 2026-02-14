// Calculator JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const display = document.getElementById('display');
    const historyDisplay = document.getElementById('historyDisplay');
    
    // Calculator State
    let expression = '';
    let lastResult = '';
    let isCalculated = false; // Track if we just calculated a result
    
    // Update display
    function updateDisplay() {
        display.value = expression || '0';
    }
    
    // Append value to display
    window.appendToDisplay = function(value) {
        // If we just calculated a result and user starts typing a number, clear everything
        if (isCalculated && value.match(/[0-9.]/)) {
            expression = '';
            isCalculated = false;
        }
        
        // If display is showing "0" or empty and user types a number, replace it
        if ((expression === '0' || expression === '') && value.match(/[0-9.]/)) {
            expression = value;
        } else {
            expression += value;
        }
        
        updateDisplay();
    };
    
    // Clear display
    window.clearDisplay = function() {
        expression = '';
        lastResult = '';
        isCalculated = false;
        updateDisplay();
        updateHistoryDisplay('');
    };
    
    // Delete last character
    window.backspace = function() {
        expression = expression.slice(0, -1);
        isCalculated = false;
        updateDisplay();
    };
    
    // Toggle positive/negative
    window.toggleSign = function() {
        if (expression) {
            if (expression.startsWith('-')) {
                expression = expression.slice(1);
            } else {
                expression = '-' + expression;
            }
            isCalculated = false;
            updateDisplay();
        }
    };
    
    // Update history display
    function updateHistoryDisplay(text) {
        if (historyDisplay) {
            historyDisplay.textContent = text;
        }
    }
    
    // Calculate result
    window.calculateResult = async function() {
        if (!expression.trim() || expression === '0') return;
        
        try {
            // Show loading state
            const originalValue = display.value;
            display.value = 'Calculating...';
            
            // Send calculation to server
            const response = await fetch('/calculate/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    expression: expression
                })
            });
            
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Update display with result
            lastResult = data.result;
            expression = data.result;
            isCalculated = true; // Mark that we just calculated
            updateDisplay();
            
            // Update history display
            updateHistoryDisplay(data.expression + ' = ' + data.result);
            
            // Show success message
            showToast('Calculation successful!', 'success');
            
        } catch (error) {
            display.value = 'Error';
            updateHistoryDisplay(error.message);
            console.error('Calculation error:', error);
            showToast('Error: ' + error.message, 'error');
            
            // Reset after error
            setTimeout(() => {
                expression = '';
                isCalculated = false;
                updateDisplay();
                updateHistoryDisplay('');
            }, 2000);
        }
    };
    
    // Copy result to clipboard
    window.copyToClipboard = function() {
        if (lastResult) {
            navigator.clipboard.writeText(lastResult)
                .then(() => {
                    showToast('Result copied to clipboard!');
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                    showToast('Failed to copy result', 'error');
                });
        } else {
            showToast('No result to copy', 'error');
        }
    };
    
    // Keyboard support - FIXED to prevent duplication
    document.addEventListener('keydown', function(event) {
        // Only process if target is not another input field (like search, username input, etc.)
        if (event.target !== display && event.target.tagName === 'INPUT') {
            return;
        }
        
        const key = event.key;
        
        // Prevent default behavior for calculator keys
        if (['0','1','2','3','4','5','6','7','8','9','+','-','*','/','.','Enter','Escape','Backspace'].includes(key)) {
            event.preventDefault();
            
            // Numbers
            if (key >= '0' && key <= '9') {
                appendToDisplay(key);
            }
            // Operators
            else if (['+', '-', '*', '/', '.'].includes(key)) {
                appendToDisplay(key);
            }
            // Enter for equals
            else if (key === 'Enter') {
                calculateResult();
            }
            // Escape for clear
            else if (key === 'Escape') {
                clearDisplay();
            }
            // Backspace
            else if (key === 'Backspace') {
                backspace();
            }
        }
    });
    
    // Prevent any editing of display input
    if (display) {
        display.addEventListener('keydown', function(event) {
            event.preventDefault();
        });
        display.addEventListener('input', function(event) {
            event.preventDefault();
            this.value = expression || '0';
        });
        display.addEventListener('paste', function(event) {
            event.preventDefault();
        });
    }
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Toast notification function
    function showToast(message, type = 'success') {
        // Remove existing toasts
        document.querySelectorAll('.toast').forEach(toast => {
            if (toast.parentNode) {
                document.body.removeChild(toast);
            }
        });
        
        // Create toast element
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background-color: ${type === 'error' ? '#ef233c' : '#4cc9f0'};
            color: white;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 3000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    document.body.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
    
    // Add CSS for toast animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .toast {
            font-family: 'Roboto', sans-serif;
            font-weight: 500;
        }
    `;
    document.head.appendChild(style);
});