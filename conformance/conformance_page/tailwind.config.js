/** @type {import('tailwindcss').Config} */
export default {
    content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
    theme: {
        extend: {
            colors: {
                paper: "#f5f5f5",
            },
            borderWidth: {
                1: "1px",
            },
        },
    },
    plugins: [],
};
