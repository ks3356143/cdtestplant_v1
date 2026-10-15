import colors from "tailwindcss/colors"
export const content = ["./src/**/*.{js,ts,jsx,tsx,vue}"]
export const darkMode = "media"
export const theme = {
    fontFamily: {
        sans: ["Graphik", "sans-serif"],
        serif: ["Merriweather", "serif"]
    },
    extend: {
        spacing: {
            128: "32rem",
            144: "36rem"
        },
        borderRadius: {
            "4xl": "2rem"
        }
    }
}
export const variants = {
    extend: {
        borderColor: ["focus-visible"],
        opacity: ["disabled"]
    }
}
export const plugins = []
