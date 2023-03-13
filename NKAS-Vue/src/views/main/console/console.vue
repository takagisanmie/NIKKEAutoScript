<template>
  <div id="Logs" style="padding-top: 14px;padding-left: 5px">
    <el-scrollbar ref="scrollbarRef">
      <span v-for="(log,index) in NKASLog.Logs" v-html="log"></span>
    </el-scrollbar>
  </div>
</template>

<script setup>
import {inject, onUpdated, ref, watch, nextTick} from "vue";

const NKASLog = inject('NKASLog')

const scrollbarRef = ref('')

watch(() => NKASLog.Logs.length, async (newValue, oldValue) => {
  if (newValue > oldValue) {
    //等待DOM渲染完毕，再进行滚动
    await nextTick()
    scrollbarRef.value.setScrollTop(scrollbarRef.value.wrapRef.scrollHeight)
  }
});
</script>

<style lang="stylus" scoped>
#Logs
  height: 100%;
  color #c0c0c0


</style>