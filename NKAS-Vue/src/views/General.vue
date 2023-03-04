<template>
  <div class="common-layout">
    <el-container
        v-loading.fullscreen.lock="updating"
        element-loading-text="更新中"
        element-loading-background="rgba(1, 1, 1, 0.6)"
    >
      <el-dialog
          v-model="updateDialogVisible"
          title="发现新版本"
          width="30%"
      >
        <div style="text-align: center">
          <el-button @click="update" size="large" style="width: 80px;margin: 20px" type="success">更新</el-button>
          <el-button @click="updateDialogVisible = false" size="large" style="width: 80px;margin: 20px" type="info">
            取消
          </el-button>
        </div>
      </el-dialog>

      <Aside></Aside>
      <router-view/>
    </el-container>
  </div>
</template>

<script setup>
import {ref, nextTick} from 'vue'
import Aside from '@/views/Aside/Aside.vue'
import {ElMessage, ElNotification, ElLoading} from "element-plus";
import Socket from "@/assets/js/socket";

const socket = Socket.getSocket()
const updateDialogVisible = ref(false)

socket.on('new_version_available', async (result) => {
  ElNotification({
    title: '检查到NKAS的最新版本',
    message: `最新版本为: ${result.data}`,
    type: 'warning',
  })
  await nextTick()
  updateDialogVisible.value = true

})

socket.on('new_nkas_version_available', async (result) => {
  ElNotification({
    title: '检查到NKAS的最新版本',
    duration: '10000',
    message: `最新版本为: ${result.data}，并且需要手动更新NKAS的Vue端。`,
    type: 'warning',
  })
})

socket.on('is_current_version', () => {
  ElNotification({
    title: '当前NKAS已是最新版',
    type: 'success',
  })
})

socket.on('check_version_failed', () => {
  updating.value = false
  updateDialogVisible.value = false
  ElNotification({
    title: '检查更新失败，无法连接到Github',
    type: 'warning',
  })
})

const updating = ref(false)

const update = () => {
  updating.value = true
  socket.emit('updateNKAS')
}

socket.on('update_NKAS_success', () => {
  updating.value = false
  updateDialogVisible.value = false
  ElNotification({
    title: '请重启NKAS以应用更改',
    type: 'success',
  })
})


</script>

<style lang="stylus" scoped>

.common-layout > *
  --el-bg-color #333333
  --el-text-color-primary #7dd08f
  --el-text-color-regular #c0c0c0


.common-layout, .el-container
  width 100%
  height 100vh
</style>