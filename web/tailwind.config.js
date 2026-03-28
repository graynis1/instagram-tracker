/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          purple: '#A78BFA',
          pink:   '#F472B6',
        },
        bg: {
          page: '#F7F8FC',
          card: '#FFFFFF',
          purple: '#FAF5FF',
          pink:   '#FDF2F8',
        },
        txt: {
          primary:   '#1C1C1E',
          secondary: '#8E8E93',
          tertiary:  '#C7C7CC',
        },
        status: {
          green:    '#15803D',
          bgGreen:  '#F0FDF4',
          red:      '#BE123C',
          bgRed:    '#FFF1F2',
        },
      },
      backgroundImage: {
        brand: 'linear-gradient(135deg, #A78BFA 0%, #F472B6 100%)',
      },
      boxShadow: {
        card: '0 2px 8px rgba(0,0,0,0.06)',
      },
      borderRadius: {
        card: '20px',
      },
    },
  },
  plugins: [],
}
