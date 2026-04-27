# Frontend Templates

All frontends live in `frontend/`. Tauri dev server URL: `http://localhost:5173`.

---

## React + TypeScript (recommended)

### `frontend/package.json`
```json
{
  "name": "<project-name>-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18",
    "react-dom": "^18",
    "@tauri-apps/api": "^2"
  },
  "devDependencies": {
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "@vitejs/plugin-react": "^4",
    "typescript": "^5",
    "vite": "^5"
  }
}
```

### `frontend/vite.config.ts`
```ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    watch: { ignored: ["**/src-tauri/**"] }
  },
  envPrefix: ["VITE_", "TAURI_"],
  build: {
    target: ["es2021", "chrome100", "safari13"],
    minify: !process.env.TAURI_DEBUG ? "esbuild" : false,
    sourcemap: !!process.env.TAURI_DEBUG,
  }
});
```

### `frontend/src/App.tsx`
```tsx
import { useState } from "react";

function App() {
  const [message, setMessage] = useState("Hello Tauri!");
  return (
    <main>
      <h1>{message}</h1>
      <button onClick={() => fetch("http://127.0.0.1:8000/api/hello")
        .then(r => r.json()).then(d => setMessage(d.message))}>
        Call Backend
      </button>
    </main>
  );
}

export default App;
```

### `frontend/src/main.tsx`
```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><App /></React.StrictMode>
);
```

### `frontend/index.html`
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title><ProjectName></title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

---

## Svelte + TypeScript

### `frontend/package.json`
```json
{
  "name": "<project-name>-frontend",
  "scripts": { "dev": "vite", "build": "vite build" },
  "dependencies": { "@tauri-apps/api": "^2" },
  "devDependencies": {
    "@sveltejs/vite-plugin-svelte": "^3",
    "svelte": "^4",
    "typescript": "^5",
    "vite": "^5"
  }
}
```

### `frontend/vite.config.ts`
```ts
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";

export default defineConfig({
  plugins: [svelte()],
  clearScreen: false,
  server: { port: 5173, strictPort: true }
});
```

### `frontend/src/App.svelte`
```svelte
<script lang="ts">
  let message = "Hello Tauri!";
  async function callBackend() {
    const r = await fetch("http://127.0.0.1:8000/api/hello");
    const d = await r.json();
    message = d.message;
  }
</script>

<main>
  <h1>{message}</h1>
  <button on:click={callBackend}>Call Backend</button>
</main>
```

---

## Vue 3 + TypeScript

### `frontend/vite.config.ts`
```ts
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  clearScreen: false,
  server: { port: 5173, strictPort: true }
});
```

### `frontend/src/App.vue`
```vue
<template>
  <main>
    <h1>{{ message }}</h1>
    <button @click="callBackend">Call Backend</button>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue";
const message = ref("Hello Tauri!");
async function callBackend() {
  const r = await fetch("http://127.0.0.1:8000/api/hello");
  const d = await r.json();
  message.value = d.message;
}
</script>
```
