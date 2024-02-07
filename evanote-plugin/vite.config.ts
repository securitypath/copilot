import { defineConfig } from 'vite'
import dts from 'vite-plugin-dts';

export default defineConfig({
    plugins: [dts()],
    build: {
        outDir: 'dist',
        lib: {
            entry: 'src/gradio-float-chatbot.ts',
            formats: ['es'],
        },
        manifest: true
    },
})