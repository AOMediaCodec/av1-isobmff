import preact from "@preact/preset-vite";
import { defineConfig } from "vite";

export default defineConfig({
    base: "/av1-isobmff/conformance/",
    plugins: [preact()],
    server: {
        fs: {
            allow: [".."],
        },
    },
});
