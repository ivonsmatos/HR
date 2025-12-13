/**
 * Accessibility Enhancements for SyncRH
 * ====================================
 * Keyboard navigation, focus management, and screen reader support
 */

document.addEventListener('DOMContentLoaded', function() {
  // Enhanced keyboard navigation
  initKeyboardNavigation();

  // Focus management for dynamic content
  initFocusManagement();

  // Screen reader announcements
  initScreenReaderSupport();

  // Skip links functionality
  initSkipLinks();
});

/**
 * Initialize keyboard navigation enhancements
 */
function initKeyboardNavigation() {
  // Handle Escape key for modal-like elements
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
      // Close chat widget if open
      const chatWidget = document.getElementById('helix-chat-widget');
      if (chatWidget && !chatWidget.classList.contains('hidden')) {
        chatWidget.classList.add('hidden');
        // Return focus to trigger element
        const triggerButton = document.querySelector('[aria-controls="helix-chat-widget"]');
        if (triggerButton) triggerButton.focus();
      }
    }
  });

  // Enhanced Tab navigation for chat interface
  const chatInterface = document.querySelector('[role="main"]');
  if (chatInterface) {
    // Ensure proper tab order
    const focusableElements = chatInterface.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );

    // Add visual focus indicators
    focusableElements.forEach(element => {
      element.addEventListener('focus', function() {
        this.setAttribute('data-focused', 'true');
      });
      element.addEventListener('blur', function() {
        this.removeAttribute('data-focused');
      });
    });
  }
}

/**
 * Initialize focus management for dynamic content
 */
function initFocusManagement() {
  // Focus management for HTMX updates
  document.addEventListener('htmx:afterSwap', function(event) {
    const target = event.detail.target;

    // If chat messages were updated, manage focus appropriately
    if (target.id === 'chat-messages' || target.id === 'chat-window') {
      // Focus the input field after message update
      const inputField = document.getElementById('message-input') || document.getElementById('chat-input');
      if (inputField) {
        setTimeout(() => inputField.focus(), 100);
      }
    }

    // Announce dynamic content updates to screen readers
    announceContentUpdate(target);
  });

  // Focus trap for modal elements
  const modalElements = document.querySelectorAll('[role="dialog"]');
  modalElements.forEach(modal => {
    modal.addEventListener('keydown', function(event) {
      if (event.key === 'Tab') {
        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            event.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            event.preventDefault();
            firstElement.focus();
          }
        }
      }
    });
  });
}

/**
 * Initialize screen reader support
 */
function initScreenReaderSupport() {
  // Create live region for announcements
  const liveRegion = document.createElement('div');
  liveRegion.setAttribute('aria-live', 'polite');
  liveRegion.setAttribute('aria-atomic', 'true');
  liveRegion.setAttribute('id', 'sr-live-region');
  liveRegion.className = 'sr-only';
  document.body.appendChild(liveRegion);

  // Announce page load
  announceToScreenReader('Página carregada: SyncRH - Sistema de Gestão Empresarial');

  // Monitor online/offline status
  window.addEventListener('online', () => {
    announceToScreenReader('Conexão restaurada');
  });

  window.addEventListener('offline', () => {
    announceToScreenReader('Conexão perdida. Funcionalidades offline disponíveis');
  });
}

/**
 * Initialize skip links functionality
 */
function initSkipLinks() {
  const skipLinks = document.querySelectorAll('.skip-link, a[href^="#"]');

  skipLinks.forEach(link => {
    link.addEventListener('click', function(event) {
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        event.preventDefault();
        targetElement.focus();
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

/**
 * Announce content updates to screen readers
 */
function announceContentUpdate(target) {
  let announcement = '';

  if (target.id === 'chat-messages') {
    announcement = 'Nova mensagem recebida no chat';
  } else if (target.id === 'conversations-list') {
    announcement = 'Lista de conversas atualizada';
  } else if (target.classList.contains('htmx-indicator')) {
    announcement = 'Carregando...';
  }

  if (announcement) {
    announceToScreenReader(announcement);
  }
}

/**
 * Utility function to announce messages to screen readers
 */
function announceToScreenReader(message) {
  const liveRegion = document.getElementById('sr-live-region');
  if (liveRegion) {
    liveRegion.textContent = message;
    // Clear after announcement
    setTimeout(() => {
      liveRegion.textContent = '';
    }, 1000);
  }
}

/**
 * Enhanced error handling with accessibility
 */
function handleError(error, context = '') {
  console.error(`Error in ${context}:`, error);

  // Announce error to screen readers
  announceToScreenReader(`Erro: ${error.message || 'Ocorreu um erro inesperado'}`);

  // Show visual error indicator if possible
  const errorIndicator = document.createElement('div');
  errorIndicator.setAttribute('role', 'alert');
  errorIndicator.setAttribute('aria-live', 'assertive');
  errorIndicator.className = 'sr-only';
  errorIndicator.textContent = `Erro: ${error.message || 'Ocorreu um erro inesperado'}`;
  document.body.appendChild(errorIndicator);

  setTimeout(() => {
    document.body.removeChild(errorIndicator);
  }, 5000);
}

// Export for global use
window.AccessibilityUtils = {
  announceToScreenReader,
  handleError
};