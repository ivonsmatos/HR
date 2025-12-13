/**
 * ============================================================================
 * SyncRH - UI Components Library
 * ============================================================================
 * 
 * Biblioteca de componentes JavaScript para a interface moderna do SyncRH.
 * Foco em performance, acessibilidade e experiência mobile-first.
 * 
 * @version 2.0.0
 */

// ============================================================================
// CORE UTILITIES
// ============================================================================

const SyncRH = {
  version: '2.0.0',
  
  /**
   * Query selector simplificado
   */
  $(selector, context = document) {
    return context.querySelector(selector);
  },
  
  $$(selector, context = document) {
    return [...context.querySelectorAll(selector)];
  },
  
  /**
   * Event delegation
   */
  on(element, event, selector, handler) {
    if (typeof selector === 'function') {
      handler = selector;
      element.addEventListener(event, handler);
    } else {
      element.addEventListener(event, (e) => {
        const target = e.target.closest(selector);
        if (target && element.contains(target)) {
          handler.call(target, e, target);
        }
      });
    }
  },
  
  /**
   * Debounce function
   */
  debounce(fn, delay = 300) {
    let timeoutId;
    return function (...args) {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
  },
  
  /**
   * Throttle function
   */
  throttle(fn, limit = 100) {
    let inThrottle;
    return function (...args) {
      if (!inThrottle) {
        fn.apply(this, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },
  
  /**
   * Gera ID único
   */
  uid(prefix = 'syncrh') {
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).substr(2, 9)}`;
  },
};

// ============================================================================
// TOAST NOTIFICATIONS
// ============================================================================

class Toast {
  static container = null;
  static defaultOptions = {
    duration: 5000,
    position: 'top-right',
    closable: true,
  };
  
  static init() {
    if (!Toast.container) {
      Toast.container = document.createElement('div');
      Toast.container.className = 'toast-container';
      document.body.appendChild(Toast.container);
    }
  }
  
  static show(message, options = {}) {
    Toast.init();
    
    const config = { ...Toast.defaultOptions, ...options };
    const toast = document.createElement('div');
    toast.className = `toast ${config.type || 'info'}`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
      <span class="toast-icon">${Toast.getIcon(config.type)}</span>
      <div class="toast-content">
        ${config.title ? `<div class="toast-title">${config.title}</div>` : ''}
        <div class="toast-message">${message}</div>
      </div>
      ${config.closable ? `<button class="modal-close" aria-label="Fechar">×</button>` : ''}
    `;
    
    Toast.container.appendChild(toast);
    
    // Trigger animation
    requestAnimationFrame(() => toast.classList.add('show'));
    
    // Auto remove
    if (config.duration > 0) {
      setTimeout(() => Toast.remove(toast), config.duration);
    }
    
    // Close button
    if (config.closable) {
      toast.querySelector('.modal-close').addEventListener('click', () => {
        Toast.remove(toast);
      });
    }
    
    return toast;
  }
  
  static remove(toast) {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }
  
  static getIcon(type) {
    const icons = {
      success: '✓',
      error: '✕',
      warning: '⚠',
      info: 'ℹ',
    };
    return icons[type] || icons.info;
  }
  
  static success(message, options = {}) {
    return Toast.show(message, { ...options, type: 'success' });
  }
  
  static error(message, options = {}) {
    return Toast.show(message, { ...options, type: 'error' });
  }
  
  static warning(message, options = {}) {
    return Toast.show(message, { ...options, type: 'warning' });
  }
  
  static info(message, options = {}) {
    return Toast.show(message, { ...options, type: 'info' });
  }
}

// ============================================================================
// MODAL COMPONENT
// ============================================================================

class Modal {
  static instances = new Map();
  
  constructor(element, options = {}) {
    this.element = typeof element === 'string' 
      ? document.querySelector(element) 
      : element;
    
    this.options = {
      backdrop: true,
      keyboard: true,
      focus: true,
      ...options,
    };
    
    this.backdrop = null;
    this.isOpen = false;
    this.previouslyFocused = null;
    
    this.init();
    Modal.instances.set(this.element, this);
  }
  
  init() {
    // Create backdrop
    if (this.options.backdrop) {
      this.backdrop = document.createElement('div');
      this.backdrop.className = 'modal-backdrop';
      this.backdrop.addEventListener('click', () => this.close());
    }
    
    // Close button
    const closeBtn = this.element.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }
    
    // Keyboard events
    if (this.options.keyboard) {
      this.element.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') this.close();
      });
    }
    
    // Trap focus
    this.element.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        this.trapFocus(e);
      }
    });
  }
  
  open() {
    if (this.isOpen) return;
    
    this.previouslyFocused = document.activeElement;
    
    if (this.backdrop) {
      document.body.appendChild(this.backdrop);
      requestAnimationFrame(() => this.backdrop.classList.add('show'));
    }
    
    this.element.style.display = 'block';
    requestAnimationFrame(() => {
      this.element.classList.add('show');
    });
    
    document.body.style.overflow = 'hidden';
    this.isOpen = true;
    
    // Focus first focusable element
    if (this.options.focus) {
      const focusable = this.element.querySelector(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (focusable) focusable.focus();
    }
    
    this.element.dispatchEvent(new CustomEvent('modal:open'));
  }
  
  close() {
    if (!this.isOpen) return;
    
    this.element.classList.remove('show');
    if (this.backdrop) {
      this.backdrop.classList.remove('show');
    }
    
    setTimeout(() => {
      this.element.style.display = 'none';
      if (this.backdrop && this.backdrop.parentNode) {
        this.backdrop.remove();
      }
      document.body.style.overflow = '';
      
      if (this.previouslyFocused) {
        this.previouslyFocused.focus();
      }
    }, 200);
    
    this.isOpen = false;
    this.element.dispatchEvent(new CustomEvent('modal:close'));
  }
  
  toggle() {
    this.isOpen ? this.close() : this.open();
  }
  
  trapFocus(e) {
    const focusables = this.element.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
  
  static get(element) {
    return Modal.instances.get(
      typeof element === 'string' ? document.querySelector(element) : element
    );
  }
}

// ============================================================================
// DROPDOWN COMPONENT
// ============================================================================

class Dropdown {
  constructor(trigger, options = {}) {
    this.trigger = typeof trigger === 'string' 
      ? document.querySelector(trigger) 
      : trigger;
    
    this.menu = this.trigger.nextElementSibling;
    this.options = {
      placement: 'bottom-start',
      offset: 4,
      ...options,
    };
    
    this.isOpen = false;
    this.init();
  }
  
  init() {
    this.trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggle();
    });
    
    // Close on click outside
    document.addEventListener('click', () => {
      if (this.isOpen) this.close();
    });
    
    // Close on escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) this.close();
    });
    
    // Keyboard navigation
    this.menu.addEventListener('keydown', (e) => {
      this.handleKeyboard(e);
    });
  }
  
  open() {
    this.menu.classList.add('show');
    this.trigger.setAttribute('aria-expanded', 'true');
    this.isOpen = true;
    this.positionMenu();
  }
  
  close() {
    this.menu.classList.remove('show');
    this.trigger.setAttribute('aria-expanded', 'false');
    this.isOpen = false;
  }
  
  toggle() {
    this.isOpen ? this.close() : this.open();
  }
  
  positionMenu() {
    const triggerRect = this.trigger.getBoundingClientRect();
    const menuRect = this.menu.getBoundingClientRect();
    
    let top = triggerRect.bottom + this.options.offset;
    let left = triggerRect.left;
    
    // Adjust if overflowing viewport
    if (left + menuRect.width > window.innerWidth) {
      left = triggerRect.right - menuRect.width;
    }
    
    if (top + menuRect.height > window.innerHeight) {
      top = triggerRect.top - menuRect.height - this.options.offset;
    }
    
    this.menu.style.position = 'fixed';
    this.menu.style.top = `${top}px`;
    this.menu.style.left = `${left}px`;
  }
  
  handleKeyboard(e) {
    const items = [...this.menu.querySelectorAll('[role="menuitem"]')];
    const current = document.activeElement;
    const index = items.indexOf(current);
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      const next = items[index + 1] || items[0];
      next.focus();
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      const prev = items[index - 1] || items[items.length - 1];
      prev.focus();
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      current.click();
    }
  }
}

// ============================================================================
// TABS COMPONENT
// ============================================================================

class Tabs {
  constructor(element, options = {}) {
    this.element = typeof element === 'string' 
      ? document.querySelector(element) 
      : element;
    
    this.options = {
      activeClass: 'active',
      ...options,
    };
    
    this.tabs = this.element.querySelectorAll('[role="tab"]');
    this.panels = this.element.querySelectorAll('[role="tabpanel"]');
    
    this.init();
  }
  
  init() {
    this.tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => this.activate(index));
      tab.addEventListener('keydown', (e) => this.handleKeyboard(e, index));
    });
  }
  
  activate(index) {
    // Deactivate all
    this.tabs.forEach((tab) => {
      tab.classList.remove(this.options.activeClass);
      tab.setAttribute('aria-selected', 'false');
      tab.setAttribute('tabindex', '-1');
    });
    
    this.panels.forEach((panel) => {
      panel.hidden = true;
    });
    
    // Activate selected
    this.tabs[index].classList.add(this.options.activeClass);
    this.tabs[index].setAttribute('aria-selected', 'true');
    this.tabs[index].setAttribute('tabindex', '0');
    this.panels[index].hidden = false;
    
    this.element.dispatchEvent(new CustomEvent('tabs:change', {
      detail: { index, tab: this.tabs[index], panel: this.panels[index] },
    }));
  }
  
  handleKeyboard(e, currentIndex) {
    let newIndex;
    
    if (e.key === 'ArrowRight') {
      newIndex = (currentIndex + 1) % this.tabs.length;
    } else if (e.key === 'ArrowLeft') {
      newIndex = (currentIndex - 1 + this.tabs.length) % this.tabs.length;
    } else if (e.key === 'Home') {
      newIndex = 0;
    } else if (e.key === 'End') {
      newIndex = this.tabs.length - 1;
    } else {
      return;
    }
    
    e.preventDefault();
    this.activate(newIndex);
    this.tabs[newIndex].focus();
  }
}

// ============================================================================
// SIDEBAR COMPONENT
// ============================================================================

class Sidebar {
  constructor(element) {
    this.element = typeof element === 'string' 
      ? document.querySelector(element) 
      : element;
    
    this.overlay = document.querySelector('.sidebar-overlay');
    this.toggleBtn = document.querySelector('[data-toggle="sidebar"]');
    this.collapseBtn = document.querySelector('[data-collapse="sidebar"]');
    
    this.isOpen = false;
    this.isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
    
    this.init();
  }
  
  init() {
    // Apply saved state
    if (this.isCollapsed) {
      this.element.classList.add('collapsed');
    }
    
    // Mobile toggle
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => this.toggle());
    }
    
    // Collapse toggle (desktop)
    if (this.collapseBtn) {
      this.collapseBtn.addEventListener('click', () => this.collapse());
    }
    
    // Overlay click
    if (this.overlay) {
      this.overlay.addEventListener('click', () => this.close());
    }
    
    // Handle resize
    window.addEventListener('resize', SyncRH.debounce(() => {
      if (window.innerWidth >= 1024 && this.isOpen) {
        this.close();
      }
    }, 100));
  }
  
  open() {
    this.element.classList.add('open');
    this.isOpen = true;
    document.body.style.overflow = 'hidden';
  }
  
  close() {
    this.element.classList.remove('open');
    this.isOpen = false;
    document.body.style.overflow = '';
  }
  
  toggle() {
    this.isOpen ? this.close() : this.open();
  }
  
  collapse() {
    this.element.classList.toggle('collapsed');
    this.isCollapsed = this.element.classList.contains('collapsed');
    localStorage.setItem('sidebar-collapsed', this.isCollapsed);
  }
}

// ============================================================================
// DATA TABLE COMPONENT
// ============================================================================

class DataTable {
  constructor(element, options = {}) {
    this.element = typeof element === 'string' 
      ? document.querySelector(element) 
      : element;
    
    this.options = {
      perPage: 10,
      searchable: true,
      sortable: true,
      pagination: true,
      ...options,
    };
    
    this.data = [];
    this.filteredData = [];
    this.currentPage = 1;
    this.sortColumn = null;
    this.sortDirection = 'asc';
    
    this.init();
  }
  
  init() {
    // Parse table data
    this.parseData();
    
    // Add controls
    if (this.options.searchable) {
      this.addSearch();
    }
    
    // Make headers sortable
    if (this.options.sortable) {
      this.makeSortable();
    }
    
    // Add pagination
    if (this.options.pagination) {
      this.addPagination();
    }
    
    this.render();
  }
  
  parseData() {
    const rows = this.element.querySelectorAll('tbody tr');
    this.data = [...rows].map((row) => {
      const cells = row.querySelectorAll('td');
      return {
        element: row,
        cells: [...cells].map((cell) => cell.textContent.trim()),
      };
    });
    this.filteredData = [...this.data];
  }
  
  addSearch() {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-search mb-4';
    wrapper.innerHTML = `
      <div class="input-group" style="max-width: 300px;">
        <span class="input-group-icon">🔍</span>
        <input type="text" class="form-input" placeholder="Pesquisar...">
      </div>
    `;
    
    this.element.parentNode.insertBefore(wrapper, this.element);
    
    const input = wrapper.querySelector('input');
    input.addEventListener('input', SyncRH.debounce((e) => {
      this.search(e.target.value);
    }, 200));
  }
  
  search(query) {
    const q = query.toLowerCase();
    
    this.filteredData = this.data.filter((row) => {
      return row.cells.some((cell) => cell.toLowerCase().includes(q));
    });
    
    this.currentPage = 1;
    this.render();
  }
  
  makeSortable() {
    const headers = this.element.querySelectorAll('th');
    
    headers.forEach((header, index) => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => this.sort(index));
    });
  }
  
  sort(columnIndex) {
    if (this.sortColumn === columnIndex) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = columnIndex;
      this.sortDirection = 'asc';
    }
    
    this.filteredData.sort((a, b) => {
      const aVal = a.cells[columnIndex];
      const bVal = b.cells[columnIndex];
      
      const comparison = aVal.localeCompare(bVal, undefined, { numeric: true });
      return this.sortDirection === 'asc' ? comparison : -comparison;
    });
    
    this.render();
  }
  
  addPagination() {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-pagination flex justify-between items-center mt-4';
    
    this.element.parentNode.appendChild(wrapper);
    this.paginationWrapper = wrapper;
  }
  
  render() {
    const tbody = this.element.querySelector('tbody');
    tbody.innerHTML = '';
    
    // Calculate pagination
    const start = (this.currentPage - 1) * this.options.perPage;
    const end = start + this.options.perPage;
    const pageData = this.filteredData.slice(start, end);
    
    // Render rows
    pageData.forEach((row) => {
      tbody.appendChild(row.element.cloneNode(true));
    });
    
    // Render pagination
    if (this.options.pagination) {
      this.renderPagination();
    }
  }
  
  renderPagination() {
    const totalPages = Math.ceil(this.filteredData.length / this.options.perPage);
    const start = (this.currentPage - 1) * this.options.perPage + 1;
    const end = Math.min(start + this.options.perPage - 1, this.filteredData.length);
    
    this.paginationWrapper.innerHTML = `
      <span class="text-sm text-muted">
        Mostrando ${start}-${end} de ${this.filteredData.length} registros
      </span>
      <div class="flex gap-2">
        <button class="btn btn-secondary btn-sm" ${this.currentPage === 1 ? 'disabled' : ''} data-page="prev">
          ← Anterior
        </button>
        <button class="btn btn-secondary btn-sm" ${this.currentPage === totalPages ? 'disabled' : ''} data-page="next">
          Próximo →
        </button>
      </div>
    `;
    
    this.paginationWrapper.querySelector('[data-page="prev"]')
      .addEventListener('click', () => this.goToPage(this.currentPage - 1));
    this.paginationWrapper.querySelector('[data-page="next"]')
      .addEventListener('click', () => this.goToPage(this.currentPage + 1));
  }
  
  goToPage(page) {
    const totalPages = Math.ceil(this.filteredData.length / this.options.perPage);
    if (page < 1 || page > totalPages) return;
    
    this.currentPage = page;
    this.render();
  }
}

// ============================================================================
// FORM VALIDATION
// ============================================================================

class FormValidator {
  constructor(form, options = {}) {
    this.form = typeof form === 'string' 
      ? document.querySelector(form) 
      : form;
    
    this.options = {
      validateOnBlur: true,
      validateOnInput: true,
      showErrors: true,
      ...options,
    };
    
    this.validators = {
      required: (value) => value.trim() !== '' || 'Este campo é obrigatório',
      email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) || 'Email inválido',
      minLength: (value, length) => value.length >= length || `Mínimo ${length} caracteres`,
      maxLength: (value, length) => value.length <= length || `Máximo ${length} caracteres`,
      pattern: (value, pattern) => new RegExp(pattern).test(value) || 'Formato inválido',
      cpf: (value) => this.validateCPF(value) || 'CPF inválido',
      cnpj: (value) => this.validateCNPJ(value) || 'CNPJ inválido',
    };
    
    this.init();
  }
  
  init() {
    this.form.setAttribute('novalidate', '');
    
    const inputs = this.form.querySelectorAll('input, select, textarea');
    
    inputs.forEach((input) => {
      if (this.options.validateOnBlur) {
        input.addEventListener('blur', () => this.validateField(input));
      }
      
      if (this.options.validateOnInput) {
        input.addEventListener('input', SyncRH.debounce(() => {
          this.validateField(input);
        }, 300));
      }
    });
    
    this.form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (this.validateAll()) {
        this.form.dispatchEvent(new CustomEvent('form:valid', {
          detail: { data: new FormData(this.form) },
        }));
      }
    });
  }
  
  validateField(field) {
    const rules = field.dataset.validate?.split('|') || [];
    const value = field.value;
    
    // Check required
    if (field.required || field.hasAttribute('required')) {
      rules.unshift('required');
    }
    
    for (const rule of rules) {
      const [validatorName, param] = rule.split(':');
      const validator = this.validators[validatorName];
      
      if (validator) {
        const result = validator(value, param);
        if (result !== true) {
          this.showError(field, result);
          return false;
        }
      }
    }
    
    this.clearError(field);
    return true;
  }
  
  validateAll() {
    const inputs = this.form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach((input) => {
      if (!this.validateField(input)) {
        isValid = false;
      }
    });
    
    return isValid;
  }
  
  showError(field, message) {
    field.classList.add('error');
    
    let errorEl = field.parentNode.querySelector('.form-error');
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.className = 'form-error';
      field.parentNode.appendChild(errorEl);
    }
    errorEl.textContent = message;
  }
  
  clearError(field) {
    field.classList.remove('error');
    const errorEl = field.parentNode.querySelector('.form-error');
    if (errorEl) errorEl.remove();
  }
  
  validateCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf.length !== 11) return false;
    if (/^(\d)\1+$/.test(cpf)) return false;
    
    let sum = 0;
    for (let i = 0; i < 9; i++) sum += parseInt(cpf[i]) * (10 - i);
    let check = 11 - (sum % 11);
    if (check >= 10) check = 0;
    if (check !== parseInt(cpf[9])) return false;
    
    sum = 0;
    for (let i = 0; i < 10; i++) sum += parseInt(cpf[i]) * (11 - i);
    check = 11 - (sum % 11);
    if (check >= 10) check = 0;
    return check === parseInt(cpf[10]);
  }
  
  validateCNPJ(cnpj) {
    cnpj = cnpj.replace(/\D/g, '');
    if (cnpj.length !== 14) return false;
    
    let size = cnpj.length - 2;
    let numbers = cnpj.substring(0, size);
    const digits = cnpj.substring(size);
    let sum = 0;
    let pos = size - 7;
    
    for (let i = size; i >= 1; i--) {
      sum += parseInt(numbers[size - i]) * pos--;
      if (pos < 2) pos = 9;
    }
    
    let result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    if (result !== parseInt(digits[0])) return false;
    
    size++;
    numbers = cnpj.substring(0, size);
    sum = 0;
    pos = size - 7;
    
    for (let i = size; i >= 1; i--) {
      sum += parseInt(numbers[size - i]) * pos--;
      if (pos < 2) pos = 9;
    }
    
    result = sum % 11 < 2 ? 0 : 11 - (sum % 11);
    return result === parseInt(digits[1]);
  }
}

// ============================================================================
// THEME TOGGLE
// ============================================================================

class ThemeToggle {
  constructor() {
    this.theme = localStorage.getItem('theme') || 'light';
    this.init();
  }
  
  init() {
    document.documentElement.setAttribute('data-theme', this.theme);
    
    const toggles = document.querySelectorAll('[data-toggle="theme"]');
    toggles.forEach((toggle) => {
      toggle.addEventListener('click', () => this.toggle());
    });
    
    // Respect system preference
    if (!localStorage.getItem('theme')) {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) this.setTheme('dark');
    }
  }
  
  toggle() {
    this.setTheme(this.theme === 'light' ? 'dark' : 'light');
  }
  
  setTheme(theme) {
    this.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    document.dispatchEvent(new CustomEvent('theme:change', {
      detail: { theme },
    }));
  }
}

// ============================================================================
// PWA HELPERS
// ============================================================================

class PWAHelper {
  static deferredPrompt = null;
  
  static init() {
    // Capture install prompt
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      PWAHelper.deferredPrompt = e;
      PWAHelper.showInstallPromotion();
    });
    
    // Track installation
    window.addEventListener('appinstalled', () => {
      PWAHelper.hideInstallPromotion();
      Toast.success('App instalado com sucesso!');
    });
    
    // Detect standalone mode
    if (window.matchMedia('(display-mode: standalone)').matches) {
      document.body.classList.add('pwa-standalone');
    }
    
    // Handle offline/online
    window.addEventListener('online', () => {
      document.body.classList.remove('offline');
      Toast.success('Conexão restaurada');
    });
    
    window.addEventListener('offline', () => {
      document.body.classList.add('offline');
      Toast.warning('Você está offline');
    });
  }
  
  static showInstallPromotion() {
    const prompt = document.createElement('div');
    prompt.className = 'pwa-install-prompt';
    prompt.innerHTML = `
      <img src="/static/images/icons/icon-64x64.png" alt="SyncRH" width="48" height="48">
      <div>
        <strong>Instalar SyncRH</strong>
        <p class="text-sm text-muted">Acesse rapidamente pelo seu dispositivo</p>
      </div>
      <button class="btn btn-primary btn-sm" id="pwa-install-btn">Instalar</button>
      <button class="btn btn-ghost btn-sm" id="pwa-dismiss-btn">×</button>
    `;
    
    document.body.appendChild(prompt);
    
    document.getElementById('pwa-install-btn').addEventListener('click', () => {
      PWAHelper.install();
    });
    
    document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
      PWAHelper.hideInstallPromotion();
    });
  }
  
  static hideInstallPromotion() {
    const prompt = document.querySelector('.pwa-install-prompt');
    if (prompt) prompt.remove();
  }
  
  static async install() {
    if (!PWAHelper.deferredPrompt) return;
    
    PWAHelper.deferredPrompt.prompt();
    const { outcome } = await PWAHelper.deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('PWA installed');
    }
    
    PWAHelper.deferredPrompt = null;
    PWAHelper.hideInstallPromotion();
  }
}

// ============================================================================
// AUTO-INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  // Initialize theme
  new ThemeToggle();
  
  // Initialize PWA helpers
  PWAHelper.init();
  
  // Auto-init modals
  document.querySelectorAll('[data-modal]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const modal = document.querySelector(trigger.dataset.modal);
      if (modal) {
        const instance = Modal.get(modal) || new Modal(modal);
        instance.open();
      }
    });
  });
  
  // Auto-init sidebar
  const sidebar = document.querySelector('.sidebar');
  if (sidebar) new Sidebar(sidebar);
  
  // Auto-init tables
  document.querySelectorAll('[data-table]').forEach((table) => {
    new DataTable(table);
  });
  
  // Auto-init form validation
  document.querySelectorAll('[data-validate]').forEach((form) => {
    new FormValidator(form);
  });
  
  // Auto-init tabs
  document.querySelectorAll('[role="tablist"]').forEach((tabs) => {
    new Tabs(tabs.closest('.tabs'));
  });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SyncRH, Toast, Modal, Dropdown, Tabs, Sidebar, DataTable, FormValidator, ThemeToggle, PWAHelper };
}

// Make available globally
window.SyncRH = SyncRH;
window.Toast = Toast;
window.Modal = Modal;
window.Dropdown = Dropdown;
window.Tabs = Tabs;
window.Sidebar = Sidebar;
window.DataTable = DataTable;
window.FormValidator = FormValidator;
window.ThemeToggle = ThemeToggle;
window.PWAHelper = PWAHelper;
