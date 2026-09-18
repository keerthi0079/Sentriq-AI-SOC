/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#0B1120",
          card: "#131C2E",
          panel: "#1E293B",
          border: "#334155",
          accent: "#38BDF8",
          teal: "#14B8A6",
          low: "#22C55E",
          medium: "#F59E0B",
          high: "#F97316",
          critical: "#EF4444",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}

