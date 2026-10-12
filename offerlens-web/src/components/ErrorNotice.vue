<script setup lang="ts">
/**
 * 错误提示条。统一四个页面的错误展示：图标 + 文案 + 可选重试。
 */
withDefaults(
  defineProps<{
    message: string
    /** 传了就显示"重试"按钮 */
    retryLabel?: string
  }>(),
  { retryLabel: '' },
)

defineEmits<{ retry: [] }>()
</script>

<template>
  <div class="notice notice-error" role="alert">
    <span class="notice-icon" aria-hidden="true">!</span>
    <span>{{ message }}</span>
    <button v-if="retryLabel" type="button" @click="$emit('retry')">{{ retryLabel }}</button>
  </div>
</template>
