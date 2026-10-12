<script setup lang="ts">
/**
 * 成功提示条。用于"已保存到投递记录"这类一次性反馈。
 */
defineProps<{ message: string }>()
</script>

<template>
  <div class="notice notice-success" role="status" aria-live="polite">
    <span class="notice-icon" aria-hidden="true">✓</span>
    <span>{{ message }}</span>
  </div>
</template>
