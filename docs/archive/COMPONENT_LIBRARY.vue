<!-- 
  ============================================
  DESIGN SYSTEM - COMPONENT LIBRARY
  ============================================
  Vue 3 Composition API Components
  Compatible with Dark Innovation Design System
  
  Usage: Import and use these components in your views
-->

<!-- ============================================
     1. BUTTON COMPONENT
     ============================================ -->

<template>
  <button
    :class="[
      'btn',
      `btn-${variant}`,
      `btn-${size}`,
      {
        'btn-loading': loading,
        'btn-disabled': disabled,
      },
    ]"
    :disabled="disabled || loading"
    @click="$emit('click')"
  >
    <span v-if="loading" class="btn-spinner" />
    <slot v-else>{{ label }}</slot>
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: "primary" | "secondary" | "tertiary" | "danger";
  size?: "sm" | "md" | "lg";
  label?: string;
  loading?: boolean;
  disabled?: boolean;
}

withDefaults(defineProps<Props>(), {
  variant: "primary",
  size: "md",
  loading: false,
  disabled: false,
});

defineEmits<{
  click: [];
}>();
</script>

<style scoped>
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border-radius: var(--radius-md);
  transition: all var(--transition-normal);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
  border: none;
  outline: none;
}

/* Sizes */
.btn-sm {
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--font-size-sm);
}

.btn-md {
  padding: var(--space-lg) var(--space-xl);
  font-size: var(--font-size-base);
}

.btn-lg {
  padding: var(--space-xl) var(--space-2xl);
  font-size: var(--font-size-lg);
}

/* Variants */
.btn-primary {
  background-color: var(--color-brand-mid);
  color: var(--color-brand-bright);
}

.btn-primary:hover:not(.btn-disabled) {
  background-color: var(--color-brand-light);
}

.btn-primary:active:not(.btn-disabled) {
  background-color: var(--color-brand-dark);
}

.btn-secondary {
  background-color: transparent;
  color: var(--color-brand-light);
  border: 2px solid var(--color-brand-light);
}

.btn-secondary:hover:not(.btn-disabled) {
  background-color: var(--color-brand-light);
  color: var(--color-brand-dark);
}

.btn-tertiary {
  background-color: transparent;
  color: var(--color-brand-light);
}

.btn-tertiary:hover:not(.btn-disabled) {
  color: var(--color-brand-bright);
  background-color: var(--color-brand-dark);
}

.btn-danger {
  background-color: var(--color-error);
  color: white;
}

.btn-danger:hover:not(.btn-disabled) {
  background-color: #dc2626;
}

/* States */
.btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-loading {
  pointer-events: none;
}

.btn-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  margin-right: var(--space-sm);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.btn:focus-visible {
  outline: 2px solid var(--color-brand-light);
  outline-offset: 2px;
}
</style>

---

<!-- ============================================
     2. CARD COMPONENT
     ============================================ -->

<template>
  <div
    :class="[
      'card',
      {
        'card-clickable': clickable,
        'card-elevated': elevated,
      },
    ]"
    @click="clickable && $emit('click')"
  >
    <div v-if="$slots.header" class="card-header">
      <slot name="header" />
    </div>

    <div class="card-body">
      <slot />
    </div>

    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  clickable?: boolean;
  elevated?: boolean;
}

withDefaults(defineProps<Props>(), {
  clickable: false,
  elevated: false,
});

defineEmits<{
  click: [];
}>();
</script>

<style scoped>
.card {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  transition: all var(--transition-normal);
}

.card-clickable {
  cursor: pointer;
}

.card-clickable:hover {
  background-color: var(--color-bg-tertiary);
  border-color: var(--color-border-secondary);
}

.card-elevated {
  box-shadow: var(--shadow-lg);
}

.card-header {
  padding: var(--space-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.card-body {
  padding: var(--space-xl);
}

.card-footer {
  padding: var(--space-xl);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg-primary);
}
</style>

---

<!-- ============================================
     3. INPUT COMPONENT
     ============================================ -->

<template>
  <div class="input-wrapper">
    <label v-if="label" :for="id" class="input-label">
      {{ label }}
      <span v-if="required" class="input-required">*</span>
    </label>

    <input
      :id="id"
      :type="type"
      :placeholder="placeholder"
      :value="modelValue"
      :disabled="disabled"
      :required="required"
      class="input-field"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
    />

    <p v-if="error" class="input-error">{{ error }}</p>
    <p v-if="hint" class="input-hint">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  modelValue: string | number;
  type?: "text" | "email" | "password" | "number" | "date" | "tel" | "url";
  placeholder?: string;
  label?: string;
  hint?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
}

withDefaults(defineProps<Props>(), {
  type: "text",
  disabled: false,
  required: false,
});

defineEmits<{
  "update:modelValue": [value: string | number];
  blur: [];
  focus: [];
}>();

const id = computed(() => `input-${Math.random().toString(36).substr(2, 9)}`);
</script>

<style scoped>
.input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.input-label {
  font-weight: 500;
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
}

.input-required {
  color: var(--color-error);
}

.input-field {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  font-size: var(--font-size-base);
  transition: all var(--transition-normal);
}

.input-field::placeholder {
  color: var(--color-text-tertiary);
}

.input-field:focus {
  border-color: var(--color-border-secondary);
  box-shadow: var(--shadow-focus);
}

.input-field:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--color-bg-primary);
}

.input-error {
  font-size: var(--font-size-xs);
  color: var(--color-error);
  margin: 0;
}

.input-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin: 0;
}
</style>

---

<!-- ============================================
     4. BADGE COMPONENT
     ============================================ -->

<template>
  <span :class="['badge', `badge-${variant}`, `badge-${size}`]">
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup lang="ts">
interface Props {
  variant?: "default" | "success" | "error" | "warning" | "info";
  size?: "sm" | "md" | "lg";
  label?: string;
}

withDefaults(defineProps<Props>(), {
  variant: "default",
  size: "md",
});
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

/* Sizes */
.badge-sm {
  padding: var(--space-xs) var(--space-md);
  font-size: var(--font-size-xs);
}

.badge-md {
  padding: var(--space-sm) var(--space-lg);
  font-size: var(--font-size-sm);
}

.badge-lg {
  padding: var(--space-md) var(--space-xl);
  font-size: var(--font-size-base);
}

/* Variants */
.badge-default {
  background-color: var(--color-brand-mid);
  color: var(--color-brand-bright);
}

.badge-success {
  background-color: rgba(16, 185, 129, 0.2);
  color: var(--color-success);
}

.badge-error {
  background-color: rgba(239, 68, 68, 0.2);
  color: var(--color-error);
}

.badge-warning {
  background-color: rgba(245, 158, 11, 0.2);
  color: var(--color-warning);
}

.badge-info {
  background-color: rgba(59, 130, 246, 0.2);
  color: var(--color-info);
}
</style>

---

<!-- ============================================
     5. MODAL COMPONENT
     ============================================ -->

<template>
  <Transition name="fade">
    <div v-if="modelValue" class="modal-backdrop" @click="close">
      <Transition name="scale">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">{{ title }}</h2>
            <button class="modal-close" @click="close" aria-label="Close modal">
              ✕
            </button>
          </div>

          <div class="modal-body">
            <slot />
          </div>

          <div v-if="$slots.footer" class="modal-footer">
            <slot name="footer" />
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean;
  title?: string;
}

defineProps<Props>();

const emit = defineEmits<{
  "update:modelValue": [value: boolean];
}>();

const close = () => emit("update:modelValue", false);
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background-color: var(--color-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
  backdrop-filter: blur(4px);
}

.modal-content {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-xl);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  z-index: var(--z-modal);
  box-shadow: var(--shadow-xl);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.modal-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
  cursor: pointer;
  transition: color var(--transition-normal);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  color: var(--color-text-primary);
}

.modal-body {
  padding: var(--space-xl);
}

.modal-footer {
  padding: var(--space-xl);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  gap: var(--space-lg);
  justify-content: flex-end;
}

/* Animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-normal);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all var(--transition-normal);
}

.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>

---

<!-- ============================================
     USAGE EXAMPLES IN VUE COMPONENTS
     ============================================ -->

<!--
BUTTON:
<Button 
  variant="primary" 
  size="md" 
  label="Click me"
  @click="handleClick"
/>

CARD:
<Card clickable @click="openDetails">
  <template #header>
    <h3>Card Title</h3>
  </template>
  <p>Card content here</p>
  <template #footer>
    <Button variant="secondary" label="Action" />
  </template>
</Card>

INPUT:
<Input 
  v-model="email"
  type="email"
  label="Email Address"
  placeholder="you@example.com"
  hint="We'll never share your email"
  @blur="validateEmail"
/>

BADGE:
<Badge variant="success" label="Active" />
<Badge variant="error" label="Error" />

MODAL:
<Modal 
  v-model="isOpen" 
  title="Confirm Action"
>
  Are you sure?
  <template #footer>
    <Button @click="cancel">Cancel</Button>
    <Button variant="danger" @click="confirm">Delete</Button>
  </template>
</Modal>
-->
