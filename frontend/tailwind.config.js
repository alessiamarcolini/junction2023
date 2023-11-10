/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        secondary: {
          '100': '#fff',
          '200': '#009ee8',
          '300': '#555'
        }
      }
    },
  },
  plugins: [],
}
