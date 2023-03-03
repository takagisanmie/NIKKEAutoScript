<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>收获</h3>
      <hr>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import Socket from "@/assets/js/socket"
import taskState from "@/views/common/taskState.vue";

const socket = Socket.getSocket()
const activate = ref('Task.Reward.activate')
const nextExecutionTime = ref('Task.Reward.nextExecutionTime')


</script>

<style lang="stylus" scoped>

</style>