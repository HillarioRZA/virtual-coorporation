import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        cos: {
          light: "#FDE68A",
          DEFAULT: "#F59E0B",
          dark: "#B45309",
        },
        cto: {
          light: "#67E8F9",
          DEFAULT: "#06B6D4",
          dark: "#0E7490",
        },
        ceo: {
          light: "#A5B4FC",
          DEFAULT: "#6366F1",
          dark: "#4338CA",
        },
      },
    },
  },
  plugins: [],
};
export default config;
