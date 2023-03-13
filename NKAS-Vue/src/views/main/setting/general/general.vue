<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <h3>通用</h3>
      <hr>
      <div>
        控制台窗口显示
        <el-switch inline-prompt active-text="隐藏" inactive-text="显示" size="large" width="60px"
                   style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                   @change="_hideWindow" v-model="hideWindow"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue'
import Socket from "@/assets/js/socket"
import _ from 'lodash'

const hideWindow = ref(false)
const socket = Socket.getSocket()

const _hideWindow = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Socket.HideWindow'
      ],
      [
        hideWindow.value
      ],
      'config',
      'update_success'
  )
  socket.emit('hideWindow')
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'Socket.HideWindow'
      ],
      'config',
      'hideWindow'
  )
}

socket.on('hideWindow', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Socket.HideWindow') {
      hideWindow.value = option.value
    }
  });
})

onMounted(() => {
  setOptions()
})

onBeforeUnmount(() => {
  // socket.disconnect()
})

</script>

<style lang="stylus" scoped>


</style>