<script setup lang="ts">
/**
 * 表格骨架屏。替代此前"正在读取投递记录…"一行文字，
 * 让加载态的布局与真实表格一致，避免内容跳动。
 */
withDefaults(defineProps<{ rows?: number; columns?: number }>(), {
  rows: 5,
  columns: 4,
})
</script>

<template>
  <div class="skeleton-table" aria-hidden="true">
    <div v-for="row in rows" :key="row" class="skeleton-row">
      <i v-for="col in columns" :key="col" />
    </div>
  </div>
  <span class="sr-only" role="status">正在加载数据…</span>
</template>
