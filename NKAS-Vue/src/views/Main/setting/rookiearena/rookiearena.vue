<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>新人竞技场</h3>
      <hr>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import Socket from "@/assets/js/socket"
import taskState from "@/views/common/taskState.vue";

const socket = Socket.getSocket()
const activate = ref('Task.RookieArena.activate')
const nextExecutionTime = ref('Task.RookieArena.nextExecutionTime')


</script>

<style lang="stylus" scoped>

</style>