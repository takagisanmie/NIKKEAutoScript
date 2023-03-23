<template>
  <el-aside style="width: auto;">
    <el-menu
        default-active="1"
        :collapse="true"
        style="height:100%;"
        :router="true"
    >
      <el-menu-item route="Main" index="1">
        <el-icon>
          <IconMenu/>
        </el-icon>
      </el-menu-item>
      <el-menu-item route="Setting" index="2">
        <el-icon>
          <Setting/>
        </el-icon>
      </el-menu-item>
      <el-menu-item @click="checkVersion" route="main" index="3">
        <el-icon>
          <Link/>
        </el-icon>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script setup>
import {ref, inject, onMounted} from 'vue'
import {
  Menu as IconMenu,
  Setting, Link
} from '@element-plus/icons-vue'
import {ElNotification, ElMessage} from 'element-plus'
import Socket from "@/assets/js/socket";
import _ from "lodash";
import dayjs from "dayjs";

const socket = Socket.getSocket()
const isCollapse = ref(true)

const translateMenu = () => {
  isCollapse.value = !isCollapse.value
}

const Log = inject('Log')
const NKASLog = inject('NKASLog')

const test = () => {
  Log.INFO('11111111111111111111111', NKASLog)
  Log.WARNING('11111111111111111111111', NKASLog)
  Log.ERROR('11111111111111111111111', NKASLog)

}

const checkVersion = () => {
  socket.emit('checkVersion')
}

socket.on('update_success', () => {

  ElNotification({
    title: '选项修改成功',
    // message: '',
    type: 'success',
    // duration: 0
  })

  socket.emit('checkSchedulerState')
  socket.emit('checkAllTaskStates')
})

socket.on('serial_update_success', () => {
  ElNotification({
    title: 'Serial修改成功',
    // message: '请重启Python端以应用更改',
    type: 'success',
  })
  socket.emit('changeSerial')
})

socket.on('insertLog', (result) => {
  if (result.type === 'INFO') {
    Log.INFO(result.text, NKASLog)
  } else if (result.type === 'WARNING') {
    Log.WARNING(result.text, NKASLog)
  } else if (result.type === 'ERROR') {
    Log.ERROR(result.text, NKASLog)
  } else if (result.type === 'LINE') {
    Log.LINE(result.text, NKASLog)
  }
})

socket.on('checkSimulator', (result) => {
  const width = result.info.displayWidth
  const height = result.info.displayHeight
  Log.INFO('当前模拟器width为' + width, NKASLog)
  Log.INFO('当前模拟器height为' + height, NKASLog)
})

socket.on('checkVersion', (result) => {
  let check_version_when_startup = false
  let already_check_version = false

  _.forEach(result.result, function (option, index) {
    if (option.key === 'already_check_version') {
      already_check_version = option.value
    } else if (option.key === 'check_version_when_startup') {
      check_version_when_startup = option.value
    }
  });
  if (check_version_when_startup && !already_check_version) {
    socket.emit('checkVersion')
    Socket.updateConfigByKey(
        [
          'already_check_version'
        ],
        [
          true
        ],
        'config',
        'None'
    )
  }
})

onMounted(() => {
  Socket.getConfigByKey(
      [
        'check_version_when_startup',
        'already_check_version'
      ],
      'config',
      'checkVersion'
  )
})

</script>

<style lang="stylus" scoped>

.el-aside, .el-menu, .el-menu > *
  //侧边栏背景色
  background-color #333333
  //菜单悬浮时颜色
  //--el-menu-hover-bg-color #5f5f5f
  //图标选中时颜色
  --el-menu-active-color #b5dbff
  //图标未选中时颜色
  --el-menu-text-color #c0c0c0

.el-menu
  left 1px

</style>