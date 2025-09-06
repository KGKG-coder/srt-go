/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        // 無襯線字體系統 - 優先使用系統字體
        sans: [
          'Inter',          // 現代化無襯線字體
          '-apple-system',  // macOS 系統字體
          'BlinkMacSystemFont', // macOS Chrome
          'Segoe UI',       // Windows 系統字體
          'Roboto',         // Android 系統字體
          'Helvetica Neue', // macOS 舊版
          'Arial',          // 通用無襯線
          'Noto Sans',      // Google 字體
          'sans-serif'      // 瀏覽器默認
        ],
        // 等寬字體（用於代碼和數據）
        mono: [
          'JetBrains Mono',
          'Fira Code',
          'Consolas',
          'Monaco',
          'Courier New',
          'monospace'
        ]
      },
      colors: {
        // 極簡風格色彩系統
        primary: {
          50: '#F0F7FF',
          100: '#E0EFFF', 
          200: '#B8DDFF',
          300: '#7BC3FF',
          400: '#36A3FF',
          500: '#0066FF',  // 主色
          600: '#0052CC',  // 懸浮色
          700: '#003D99',
          800: '#002966',
          900: '#001533'
        },
        gray: {
          50: '#FAFAFA',
          100: '#F4F4F5',
          200: '#E4E4E7',
          300: '#D4D4D8',
          400: '#A1A1AA',
          500: '#71717A',
          600: '#52525B',
          700: '#3F3F46',
          800: '#27272A',
          900: '#18181B'
        },
        // 狀態色彩
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        // 背景色彩
        background: '#FFFFFF',
        surface: '#F8F9FA',
        // 文字色彩
        'text-primary': '#1A1A1A',
        'text-secondary': '#6B7280',
        'text-tertiary': '#9CA3AF'
      },
      spacing: {
        // 8pt 網格系統
        '18': '4.5rem',   // 72px
        '22': '5.5rem',   // 88px
        '26': '6.5rem',   // 104px
        '30': '7.5rem',   // 120px
      },
      borderRadius: {
        // 統一的圓角系統
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px'
      },
      boxShadow: {
        // 極簡陰影系統
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'card-focus': '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
      },
      animation: {
        // 自定義動畫
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'spin-slow': 'spin 2s linear infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' }
        }
      },
      fontSize: {
        // 排版尺寸系統
        'xs': ['0.75rem', { lineHeight: '1rem' }],     // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        'base': ['1rem', { lineHeight: '1.5rem' }],    // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }], // 18px
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],  // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],     // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
        '5xl': ['3rem', { lineHeight: '1' }],           // 48px
      }
    },
  },
  plugins: [
    // 自定義插件
    function({ addUtilities }) {
      const newUtilities = {
        // 文字選擇樣式
        '.select-none': {
          '-webkit-user-select': 'none',
          '-moz-user-select': 'none',
          '-ms-user-select': 'none',
          'user-select': 'none',
        },
        // 滾動條樣式
        '.scrollbar-thin': {
          'scrollbar-width': 'thin',
          'scrollbar-color': '#CBD5E0 #F7FAFC',
        },
        '.scrollbar-thin::-webkit-scrollbar': {
          width: '8px',
        },
        '.scrollbar-thin::-webkit-scrollbar-track': {
          background: '#F7FAFC',
          'border-radius': '4px',
        },
        '.scrollbar-thin::-webkit-scrollbar-thumb': {
          background: '#CBD5E0',
          'border-radius': '4px',
        },
        '.scrollbar-thin::-webkit-scrollbar-thumb:hover': {
          background: '#A0AEC0',
        },
        // 焦點樣式
        '.focus-ring': {
          '&:focus': {
            outline: '2px solid transparent',
            'outline-offset': '2px',
            'box-shadow': '0 0 0 2px #0066FF',
          },
        },
      }
      addUtilities(newUtilities)
    }
  ],
}