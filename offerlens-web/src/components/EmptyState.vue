<script setup lang="ts">
/**
 * 空状态。统一"没有数据"的视觉：图标 + 标题 + 说明 + 可选操作。
 */
withDefaults(
  defineProps<{
    icon?: string
    title: string
    description?: string
    /** 紧凑模式：用于面板内部的小块空状态 */
    compact?: boolean
  }>(),
  { icon: '·', description: '', compact: false },
)
</script>

<template>
  <div class="empty-state" :class="{ 'compact-empty': compact }">
    <div class="empty-mark" aria-hidden="true">{{ icon }}</div>
    <strong>{{ title }}</strong>
    <p v-if="description">{{ description }}</p>
    <slot />
  </div>
</template>
