<template>
  <WindowButton :isConnected="isConnected"></WindowButton>
  <General></General>
</template>

<script setup>
import Socket from "@/assets/js/socket"
import Log from '@/assets/js/Log'
import {inject, onMounted, provide, ref} from "vue";
import {useRouter} from 'vue-router'
import WindowButton from '@/views/WindowButton/WindowButton.vue'
import General from '@/views/General.vue'
import useNKASLog from "@/assets/store/logStore";

const NKASLog = useNKASLog()
const router = useRouter()
const socket = Socket.getSocket()
const isConnected = ref(false)

provide('Log', Log)
provide('NKASLog', NKASLog)

onMounted(() => {
  Log.INFO('等待Socket连接', NKASLog)
  //解决打包后router失效
  router.push('/')
  socket.connect()
})

socket.on('connect', () => {
  Log.INFO('Socket已连接', NKASLog)
  isConnected.value = true
})

socket.on('disconnect', () => {
  Log.INFO('Socket断开连接', NKASLog)
  isConnected.value = false
  location.reload()
  // socket.connect()

})

</script>
<style lang="stylus" scoped>


</style>

