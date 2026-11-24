/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070d18',
          900: '#0b1329',
          850: '#0f1c3a',
          800: '#152449',
          700: '#1e3363',
          600: '#2d4985',
        },
        brand: {
          blue: '#1d4ed8',
          cyan: '#06b6d4',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e',
        }
      }
    },
  },
  plugins: [],
}
