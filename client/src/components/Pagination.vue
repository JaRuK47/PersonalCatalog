<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentPage: { type: Number, required: true },
  totalPages: { type: Number, required: true }
});

const emit = defineEmits(['update:currentPage']);

const visiblePages = computed(() => {
  const total = props.totalPages;
  const current = props.currentPage;
  const delta = 3;
  const range = [];
  const rangeWithDots = [];
  let l;

  if (total <= 9) {
    for (let i = 1; i <= total; i++) range.push(i);
    return range;
  }

  for (let i = 1; i <= total; i++) {
    if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
      range.push(i);
    }
  }

  for (let i of range) {
    if (l) {
      if (i - l === 2) {
        rangeWithDots.push(l + 1);
      } else if (i - l !== 1) {
        rangeWithDots.push('...');
      }
    }
    rangeWithDots.push(i);
    l = i;
  }

  return rangeWithDots;
});

function changePage(page) {
  if (page >= 1 && page <= props.totalPages) {
    emit('update:currentPage', page);
  }
}
</script>

<template>
  <nav v-if="totalPages > 1" class="mt-4">
    <ul class="pagination justify-content-center">
      <li class="page-item" :class="{ disabled: currentPage === 1 }">
        <button class="page-link" @click="changePage(currentPage - 1)">Предыдущая</button>
      </li>

      <li
        class="page-item"
        v-for="(page, index) in visiblePages"
        :key="`page-${page}-${index}`"
        :class="{ active: currentPage === page, disabled: page === '...' }"
      >
        <span v-if="page === '...'" class="page-link">...</span>
        <button v-else class="page-link" @click="changePage(page)">{{ page }}</button>
      </li>

      <li class="page-item" :class="{ disabled: currentPage === totalPages }">
        <button class="page-link" @click="changePage(currentPage + 1)">Следующая</button>
      </li>
    </ul>
  </nav>
</template>