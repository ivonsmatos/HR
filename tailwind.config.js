/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./templates/**/*.html",
    "./apps/**/*.html",
  ],

  theme: {
    extend: {
      // ============================================
      // BRAND COLORS - Dark Innovation Palette
      // ============================================
      colors: {
        // ---- PRIMARY PALETTE (5 Core Colors)
        brand: {
          darkest: '#00080D',  // Primary app background
          dark: '#122E40',     // Cards, panels, surfaces
          mid: '#274B59',      // Primary interactive elements
          light: '#547C8C',    // Secondary, hovers, soft accents
          bright: '#D0E5F2',   // Text primary, maximum contrast
        },

        // ---- SEMANTIC SURFACE COLORS
        surface: {
          primary: '#00080D',        // Main background
          secondary: '#122E40',      // Cards, elevated surfaces
          tertiary: '#274B59',       // Hover, active states
          overlay: 'rgba(0, 8, 13, 0.8)',  // Modal overlay
        },

        // ---- TEXT HIERARCHY
        text: {
          primary: '#D0E5F2',        // Headlines, body text
          secondary: '#547C8C',      // Labels, secondary info
          tertiary: '#274B59',       // Placeholders, disabled
          disabled: '#274B59',       // Disabled text
        },

        // ---- BORDER COLORS
        border: {
          primary: '#274B59',        // Strong borders
          secondary: '#547C8C',      // Subtle borders
          light: '#122E40',          // Very subtle dividers
        },

        // ---- INTERACTIVE STATES
        interactive: {
          default: '#274B59',
          hover: '#547C8C',
          active: '#122E40',
          focus: '#547C8C',
          disabled: '#274B59',
        },

        // ---- SEMANTIC STATUS COLORS
        // Add these if you need status indicators
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6',

        // ---- TRANSPARENCY UTILITIES
        'brand-alpha': {
          5: 'rgba(212, 229, 242, 0.05)',
          10: 'rgba(212, 229, 242, 0.1)',
          20: 'rgba(212, 229, 242, 0.2)',
          30: 'rgba(212, 229, 242, 0.3)',
          50: 'rgba(212, 229, 242, 0.5)',
        },
      },

      // ============================================
      // TYPOGRAPHY
      // ============================================
      fontFamily: {
        // Modern, tech-forward sans-serif stack
        sans: [
          'Inter',
          'Roboto',
          'Manrope',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'sans-serif',
        ],
        // Monospace for code blocks
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Courier New',
          'monospace',
        ],
      },

      fontSize: {
        // ---- TYPOGRAPHY SCALE (12-step)
        'xs': ['12px', { lineHeight: '16px', letterSpacing: '0.3px' }],
        'sm': ['13px', { lineHeight: '18px', letterSpacing: '0.25px' }],
        'base': ['14px', { lineHeight: '20px', letterSpacing: '0.2px' }],
        'lg': ['16px', { lineHeight: '24px', letterSpacing: '0.15px' }],
        'xl': ['18px', { lineHeight: '28px', letterSpacing: '0.1px' }],
        '2xl': ['20px', { lineHeight: '28px', letterSpacing: '0px' }],
        '3xl': ['24px', { lineHeight: '32px', letterSpacing: '-0.5px' }],
        '4xl': ['28px', { lineHeight: '36px', letterSpacing: '-0.7px' }],
        '5xl': ['32px', { lineHeight: '40px', letterSpacing: '-0.8px' }],
        '6xl': ['36px', { lineHeight: '44px', letterSpacing: '-0.9px' }],
      },

      fontWeight: {
        thin: '100',
        extralight: '200',
        light: '300',
        normal: '400',     // Body text
        medium: '500',     // Emphasis
        semibold: '600',   // Subheadings
        bold: '700',       // Headlines
        extrabold: '800',  // Major titles
      },

      // ============================================
      // SPACING & SIZING (Generous padding = Minimalista)
      // ============================================
      spacing: {
        px: '1px',
        0: '0',
        1: '4px',      // xs
        2: '8px',      // sm
        3: '12px',     // md
        4: '16px',     // md
        5: '20px',     // lg
        6: '24px',     // lg
        8: '32px',     // xl
        10: '40px',    // 2xl
        12: '48px',    // 2xl
        16: '64px',    // 3xl
        20: '80px',    // 4xl
      },

      // ============================================
      // BORDER RADIUS (Flat, minimal rounding)
      // ============================================
      borderRadius: {
        none: '0',
        xs: '2px',      // Minimal
        sm: '4px',      // Input fields
        md: '6px',      // Cards, buttons
        lg: '8px',      // Large panels
        xl: '12px',     // Modal dialogs
        full: '9999px', // Pill-shaped
      },

      // ============================================
      // BOX SHADOWS (Minimal - flat design emphasis)
      // ============================================
      boxShadow: {
        none: 'none',
        xs: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        sm: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        md: '0 2px 4px 0 rgba(0, 0, 0, 0.15)',
        lg: '0 4px 8px 0 rgba(0, 0, 0, 0.2)',
        xl: '0 8px 16px 0 rgba(0, 0, 0, 0.25)',
        // Focus ring (light)
        'focus': '0 0 0 3px rgba(84, 124, 140, 0.1)',
      },

      // ============================================
      // TRANSITIONS & ANIMATIONS
      // ============================================
      transitionDuration: {
        0: '0ms',
        75: '75ms',
        100: '100ms',
        150: '150ms',
        200: '200ms',
        300: '300ms',
        500: '500ms',
        700: '700ms',
        1000: '1000ms',
      },

      transitionTimingFunction: {
        linear: 'linear',
        in: 'cubic-bezier(0.4, 0, 1, 1)',
        out: 'cubic-bezier(0, 0, 0.2, 1)',
        'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },

      // ============================================
      // RESPONSIVE BREAKPOINTS (Mobile-first)
      // ============================================
      screens: {
        xs: '320px',    // Small phones
        sm: '640px',    // Large phones
        md: '768px',    // Tablets
        lg: '1024px',   // Small laptops
        xl: '1280px',   // Desktops
        '2xl': '1536px', // Large screens
      },

      // ============================================
      // KEYFRAME ANIMATIONS
      // ============================================
      keyframes: {
        // Spin animation (for loaders)
        spin: {
          to: { transform: 'rotate(360deg)' },
        },
        // Pulse animation
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        // Fade in
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        // Slide in from left
        slideInLeft: {
          from: { transform: 'translateX(-100%)' },
          to: { transform: 'translateX(0)' },
        },
        // Slide in from right
        slideInRight: {
          from: { transform: 'translateX(100%)' },
          to: { transform: 'translateX(0)' },
        },
      },

      animation: {
        spin: 'spin 1s linear infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in': 'fadeIn 300ms ease-out',
        'slide-in-left': 'slideInLeft 300ms ease-out',
        'slide-in-right': 'slideInRight 300ms ease-out',
      },
    },
  },

  // ============================================
  // PLUGINS
  // ============================================
  plugins: [
    // Uncomment as needed:
    // require('@tailwindcss/forms'),
    // require('@tailwindcss/typography'),
    // require('@tailwindcss/aspect-ratio'),
  ],

  // ============================================
  // DARK MODE
  // ============================================
  darkMode: 'class',  // Class-based dark mode (manual toggle)

  // ============================================
  // OPTIMIZATION
  // ============================================
  safelist: [
    // Add utilities that might be dynamically generated
    { pattern: /^bg-brand-/ },
    { pattern: /^text-brand-/ },
    { pattern: /^border-brand-/ },
    { pattern: /^text-text-/ },
    { pattern: /^bg-surface-/ },
    { pattern: /^border-border-/ },
  ],

  // Specificity control
  important: false,
};
