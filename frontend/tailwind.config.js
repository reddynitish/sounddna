/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Syne"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
        body: ['"DM Sans"', 'sans-serif'],
      },
      colors: {
        obsidian: '#080810',
        void: '#0d0d1a',
        surface: '#12121f',
        panel: '#1a1a2e',
        border: '#ffffff0f',
        acid: '#c8f53d',
        plasma: '#7b61ff',
        ember: '#ff6b35',
        ice: '#38bdf8',
        mist: '#ffffff14',
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'spin-slow': 'spin 8s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'scan': 'scan 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        glow: {
          from: { boxShadow: '0 0 20px #c8f53d33' },
          to: { boxShadow: '0 0 40px #c8f53d88, 0 0 80px #c8f53d22' },
        },
        scan: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(400%)' },
        }
      }
    },
  },
  plugins: [],
}
