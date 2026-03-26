import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ink: "#08111a",
        panel: "#0f1c27",
        line: "#1d3341",
        signal: "#35d0aa",
        flare: "#f7b84b",
        warn: "#ff7a59",
        frost: "#dbe7f2",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(61, 146, 214, 0.16), 0 24px 60px rgba(2, 8, 15, 0.45)",
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(91,125,145,0.10) 1px, transparent 1px), linear-gradient(90deg, rgba(91,125,145,0.10) 1px, transparent 1px)",
      },
      fontFamily: {
        display: ["var(--font-display)"],
        body: ["var(--font-body)"],
        mono: ["var(--font-mono)"],
      },
    },
  },
  plugins: [],
};

export default config;
