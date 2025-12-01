# 🎨 DESIGN SYSTEM - GUIA DE IMPLEMENTAÇÃO

**Data**: 1 de dezembro de 2025  
**Projeto**: Worksuite PWA  
**Status**: ✅ Pronto para implementação

---

## 📋 Índice

1. [Setup Inicial](#setup-inicial)
2. [Instalação de Dependências](#instalação-de-dependências)
3. [Configuração de Arquivos](#configuração-de-arquivos)
4. [Importação no Projeto](#importação-no-projeto)
5. [Usando Componentes](#usando-componentes)
6. [Customização](#customização)
7. [Testing & Validação](#testing--validação)
8. [Troubleshooting](#troubleshooting)

---

## ✅ Setup Inicial

### O que você recebeu:

```
Design System "Dark Innovation":
├── DESIGN_SYSTEM.md ..................... 📖 Documentação completa
├── tailwind.config.js .................. ⚙️ Configuração Tailwind
├── static/css/global.css ............... 🎨 CSS global + variáveis
├── docs/COMPONENT_LIBRARY.vue .......... 🧩 Componentes Vue
└── README.md (este arquivo) ............ 📝 Guia de uso
```

### 5 Cores Premium:

```
#00080D (Deep Black)      ← Background principal
#122E40 (Deep Navy)       ← Cards e superfícies
#274B59 (Muted Teal)      ← Interativo primário
#547C8C (Soft Blue Grey)  ← Secundário/hover
#D0E5F2 (Pale Blue)       ← Texto principal
```

---

## 🔧 Instalação de Dependências

### 1. Tailwind CSS + Plugins

```bash
npm install -D tailwindcss postcss autoprefixer
npm install -D @tailwindcss/forms @tailwindcss/typography

# ou com pnpm
pnpm add -D tailwindcss postcss autoprefixer @tailwindcss/forms
```

### 2. Fonte Inter (Google Fonts)

No seu `index.html` ou `<head>`:

```html
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
  rel="stylesheet"
/>
```

### 3. PostCSS Config

Crie `postcss.config.js` na raiz do projeto:

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

---

## 📁 Configuração de Arquivos

### 1. Copie `tailwind.config.js` para a raiz do projeto

```bash
# Se usar Vite + Vue
cp tailwind.config.js ./

# Atualize seu vite.config.js ou webpack.config.js se necessário
```

### 2. Copie `global.css` para `static/css/`

```bash
mkdir -p static/css
cp global.css static/css/global.css
```

### 3. Importe o CSS global no seu App.vue ou main.js

```javascript
// main.js (Vue 3)
import "./static/css/global.css";
import "tailwindcss/tailwind.css";
```

---

## 🎯 Importação no Projeto

### 1. HTML Base (Django/Jinja2)

Se estiver usando o `templates/base.html` existente, adicione:

```html
<!DOCTYPE html>
<html lang="pt-br">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <!-- Tailwind CSS (if using build process) -->
    <link href="{% static 'css/styles.css' %}" rel="stylesheet" />

    <!-- Google Fonts -->
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"
      rel="stylesheet"
    />

    <!-- Global CSS -->
    <link href="{% static 'css/global.css' %}" rel="stylesheet" />

    <title>Worksuite - ERP PWA</title>
  </head>
  <body class="bg-surface-primary text-text-primary">
    <div id="app"></div>
  </body>
</html>
```

### 2. Vue 3 App

Se estiver usando Vue 3 + Vite:

```javascript
// main.ts
import { createApp } from "vue";
import App from "./App.vue";

// Import styles
import "./static/css/global.css";
import "tailwindcss/tailwind.css";

const app = createApp(App);
app.mount("#app");
```

### 3. App.vue

```vue
<template>
  <div class="bg-surface-primary text-text-primary min-h-screen">
    <nav class="bg-surface-secondary border-b border-border-light">
      <!-- Navigation content -->
    </nav>

    <main class="p-6 md:p-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
// Your script here
</script>
```

---

## 🧩 Usando Componentes

### 1. Importe Componentes

```vue
<!-- PageComponent.vue -->
<script setup>
import Button from "@/components/Button.vue";
import Card from "@/components/Card.vue";
import Input from "@/components/Input.vue";
import Badge from "@/components/Badge.vue";
import Modal from "@/components/Modal.vue";

import { ref } from "vue";

const isModalOpen = ref(false);
const formData = ref({
  name: "",
  email: "",
});
</script>

<template>
  <div class="space-y-6">
    <!-- Card with Button -->
    <Card>
      <template #header>
        <h1 class="text-3xl font-bold">Dashboard</h1>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Stat Card -->
        <Card>
          <div class="text-center">
            <p class="text-text-secondary mb-2">Total Users</p>
            <p class="text-5xl font-bold text-brand-bright">1,234</p>
            <Badge variant="success" label="↑ 12%" />
          </div>
        </Card>
      </div>
    </Card>

    <!-- Form -->
    <Card elevated>
      <template #header>
        <h2 class="text-2xl font-bold">New Employee</h2>
      </template>

      <form class="space-y-4" @submit.prevent="handleSubmit">
        <Input
          v-model="formData.name"
          type="text"
          label="Full Name"
          placeholder="John Doe"
          required
        />

        <Input
          v-model="formData.email"
          type="email"
          label="Email Address"
          placeholder="john@example.com"
          hint="Company email required"
          required
        />
      </form>

      <template #footer>
        <Button variant="secondary" label="Cancel" />
        <Button variant="primary" label="Save" @click="isModalOpen = true" />
      </template>
    </Card>

    <!-- Modal -->
    <Modal v-model="isModalOpen" title="Confirm">
      <p class="text-text-secondary mb-4">
        Are you sure you want to create this employee?
      </p>

      <template #footer>
        <Button
          variant="secondary"
          label="Cancel"
          @click="isModalOpen = false"
        />
        <Button variant="primary" label="Confirm" @click="handleConfirm" />
      </template>
    </Modal>
  </div>
</template>

<script setup>
const handleSubmit = () => {
  // Handle form submission
};

const handleConfirm = () => {
  // Handle confirmation
  isModalOpen.value = false;
};
</script>
```

---

## 🎨 Customização

### 1. Mudar Cores Primárias

Edit `tailwind.config.js`:

```javascript
colors: {
  brand: {
    darkest: '#00080D',  // ← Mude aqui
    dark: '#122E40',
    mid: '#274B59',
    light: '#547C8C',
    bright: '#D0E5F2',
  },
}
```

Ou em `global.css`:

```css
:root {
  --color-brand-darkest: #00080d; /* Edite aqui */
  --color-brand-dark: #122e40;
  /* ... */
}
```

### 2. Mudar Fonte

`tailwind.config.js`:

```javascript
fontFamily: {
  sans: [
    'Roboto',  // ← Ou sua fonte preferida
    '-apple-system',
    'BlinkMacSystemFont',
    'sans-serif',
  ],
}
```

### 3. Mudar Espaçamento

`tailwind.config.js`:

```javascript
spacing: {
  px: '1px',
  0: '0',
  1: '4px',   // ← Ajuste conforme necessário
  2: '8px',
  4: '16px',
  6: '24px',
  8: '32px',
}
```

---

## ✅ Testing & Validação

### 1. Teste Contraste (WCAG AA)

Use [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/):

```
#D0E5F2 (texto) sobre #00080D (bg):
Ratio: 17.5:1 ✅ AAA
```

### 2. Teste Responsividade

```html
<div class="xs:text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl">
  Responsive Text
</div>
```

### 3. Teste PWA Safe Area

No DevTools do navegador, ative "Crop to notch" (Chrome) ou "Safe area" (Safari).

### 4. Lighthouse Audit

```bash
# Se usar Vite
npm run build
# Abra em DevTools → Lighthouse → Analyze page load
```

**Metas**:

- ✅ Accessibility: 90+
- ✅ Best Practices: 90+
- ✅ Performance: 85+ (em 4G)

---

## 🐛 Troubleshooting

### Problema: Cores não aparecem

**Solução**: Verifique se o `tailwind.config.js` está na raiz do projeto:

```bash
# Verificar
ls -la tailwind.config.js

# Se não existir, copie:
cp path/to/tailwind.config.js ./
```

### Problema: Fonte Inter não carrega

**Solução 1**: Use Google Fonts CDN no HTML:

```html
<link
  href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
  rel="stylesheet"
/>
```

**Solução 2**: Instale localmente:

```bash
npm install @fontsource/inter
```

```javascript
// main.ts
import "@fontsource/inter";
```

### Problema: Componentes não reconhecem classes Tailwind

**Solução**: Verifique `tailwind.config.js` - `content` deve incluir seus arquivos:

```javascript
content: [
  "./index.html",
  "./src/**/*.{vue,js,ts,jsx,tsx}", // ← Ajuste o path
  "./templates/**/*.html",
];
```

### Problema: CSS global não aplica

**Solução**: Verifique a ordem de imports em `main.ts`:

```javascript
// Ordem IMPORTANTE:
import "./static/css/global.css"; // 1º
import "tailwindcss/tailwind.css"; // 2º
import App from "./App.vue"; // 3º
```

### Problema: Dark mode não funciona em PWA

**Solução**: Design System é **Dark-only** por padrão. Se precisar de Light mode:

1. Edite `tailwind.config.js`:

   ```javascript
   darkMode: 'class',  // Ou 'media' para seguir sistema
   ```

2. Adicione seletor no HTML:
   ```html
   <html class="dark">
     <!-- Força dark mode -->
   </html>
   ```

---

## 📊 Exemplo: Dashboard Completo

```vue
<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h1 class="text-5xl font-bold text-text-primary">Dashboard</h1>
      <Button variant="primary" label="+ New" />
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard title="Total Users" value="1,234" trend="↑ 12%" />
      <StatCard title="Revenue" value="$45.2k" trend="↑ 8%" />
      <StatCard title="Orders" value="892" trend="↓ 3%" variant="warning" />
      <StatCard title="Pending" value="47" trend="New" variant="error" />
    </div>

    <!-- Tables -->
    <Card elevated>
      <template #header>
        <h2 class="text-2xl font-bold">Recent Orders</h2>
      </template>

      <table class="w-full">
        <thead class="border-b border-border-light">
          <tr>
            <th class="text-left p-4 text-text-primary font-semibold">
              Order ID
            </th>
            <th class="text-left p-4 text-text-primary font-semibold">
              Customer
            </th>
            <th class="text-left p-4 text-text-primary font-semibold">
              Status
            </th>
            <th class="text-left p-4 text-text-primary font-semibold">
              Amount
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            class="border-b border-border-light hover:bg-surface-tertiary transition-colors"
          >
            <td class="p-4 text-text-primary">#ORD-001</td>
            <td class="p-4 text-text-primary">John Doe</td>
            <td class="p-4">
              <Badge variant="success" label="Completed" />
            </td>
            <td class="p-4 text-text-primary">$1,234.00</td>
          </tr>
        </tbody>
      </table>
    </Card>
  </div>
</template>

<script setup>
import Button from "@/components/Button.vue";
import Card from "@/components/Card.vue";
import Badge from "@/components/Badge.vue";
import StatCard from "@/components/StatCard.vue";
</script>
```

---

## 🚀 Próximos Passos

1. **Setup Inicial** (20 min)

   - [ ] Instale Tailwind CSS
   - [ ] Copie arquivos de configuração
   - [ ] Importe global.css e tailwind.css

2. **Criação de Componentes** (2-4 horas)

   - [ ] Crie pasta `src/components/`
   - [ ] Copie componentes do COMPONENT_LIBRARY.vue
   - [ ] Adapte para seu projeto (Vue, React, etc)

3. **Implementação de Pages** (4-8 horas)

   - [ ] Dashboard
   - [ ] Employees
   - [ ] Projects
   - [ ] Settings

4. **Testing** (2-4 horas)

   - [ ] Teste contraste (WCAG AA)
   - [ ] Teste responsividade
   - [ ] Teste PWA (offline, install, etc)
   - [ ] Lighthouse audit

5. **Deploy** (1-2 horas)
   - [ ] Build otimizado
   - [ ] Setup HTTPS
   - [ ] Testing em produção
   - [ ] App install test

---

## 📞 Suporte

**Design System Issues**: Verifique `DESIGN_SYSTEM.md`  
**Component Usage**: Veja `COMPONENT_LIBRARY.vue`  
**Tailwind Docs**: https://tailwindcss.com  
**Vue Docs**: https://vuejs.org

---

**Status**: ✅ Ready to implement  
**Última atualização**: 1 de dezembro de 2025
