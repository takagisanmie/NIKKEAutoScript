<template>
  <div class="common-layout">
    <el-container>
      <Aside></Aside>
      <router-view/>
    </el-container>
  </div>
</template>

<script setup>
import Aside from '@/views/Aside/Aside.vue'

</script>

<style lang="stylus" scoped>

.common-layout, .el-container
  width 100%
  height 100vh
</style>