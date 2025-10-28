/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#ff5640',
          light: '#ff7d69',
          dark: '#e24732'
        }
      }
    },
  },
  plugins: [],
};
