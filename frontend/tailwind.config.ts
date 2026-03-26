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
        gigw: {
          navy: "#152A38",
          saffron: "#FF9933",
          green: "#138808",
          blue: "#003366",
          cerulean: {
            600: "#0056B3",
            700: "#004494"
          },
          charcoal: "#212529",
          slate: "#F4F6F9",
          success: "#28A745",
          warning: "#FFC107",
          error: "#DC3545"
        }
      },
    },
  },
  plugins: [],
};

export default config;
