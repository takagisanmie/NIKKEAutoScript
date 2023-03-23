<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <h3>通用</h3>
      <hr>
      <div>
        <div>
          启动时检查更新
          <el-switch inline-prompt active-text="检查" size="large" width="60px"
                     style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                     @change="_check_version_when_startup" v-model="check_version_when_startup"/>
        </div>
        <br>
        <br>
        <div>
          控制台窗口显示
          <el-switch inline-prompt active-text="隐藏" inactive-text="显示" size="large" width="60px"
                     style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                     @change="_hideWindow" v-model="hideWindow"/>
        </div>
        <br>
        <br>
        <div>
          所有任务完成时
          <el-select @change="_idle" effect="dark" style="float:right;width: 210px;" v-model="idle"
                     class="m-2" placeholder=" "
                     size="large">
            <el-option
                v-for="item in when_all_task_finished"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
          </el-select>
        </div>
        <br>
        <br>
        <div>
          每日任务完成时，进行通知
          <el-select @change="_notification" effect="dark" style="float:right;width: 210px;" v-model="notification"
                     class="m-2" placeholder=" "
                     size="large">
            <el-option
                v-for="item in when_daily_task_finished"
                :key="item.value"
                :label="item.label"
                :value="item.value"
            />
          </el-select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, onBeforeUnmount} from 'vue'
import Socket from "@/assets/js/socket"
import _ from 'lodash'

const check_version_when_startup = ref(false)
const hideWindow = ref(false)
const idle = ref()
const notification = ref()
const socket = Socket.getSocket()

const _check_version_when_startup = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'check_version_when_startup'
      ],
      [
        check_version_when_startup.value
      ],
      'config',
      'update_success'
  )
}, 127)

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

const _notification = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Notification'
      ],
      [
        notification.value
      ],
      'config',
      'update_success'
  )
  socket.emit('notification_test')
}, 127)

const _idle = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Idle'
      ],
      [
        idle.value
      ],
      'config',
      'update_success'
  )
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'check_version_when_startup',
        'Socket.HideWindow',
        'Idle',
        'Notification'
      ],
      'config',
      'setGeneralOption'
  )
}

socket.on('setGeneralOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Socket.HideWindow') {
      hideWindow.value = option.value
    } else if (option.key === 'Idle') {
      idle.value = option.value
    } else if (option.key === 'Notification') {
      notification.value = option.value
    } else if (option.key === 'check_version_when_startup') {
      check_version_when_startup.value = option.value
    }
  });
})

onMounted(() => {
  setOptions()
})

onBeforeUnmount(() => {
  // socket.disconnect()
})

const when_all_task_finished = [
  {
    value: 0,
    label: '回到主菜单',
  },
  {
    value: 1,
    label: '关闭游戏',
  }
]

const when_daily_task_finished = [
  {
    value: 0,
    label: '不通知',
  },
  {
    value: 1,
    label: '样式一',
  },
  {
    value: 2,
    label: '样式二',
  }
]


</script>

<style lang="stylus" scoped>
*
  --el-fill-color-blank #333333
  --el-text-color-regular #c0c0c0

.el-select-dropdown__item.hover, .el-select-dropdown__item:hover
  background-color #4d4d4d

.el-select-dropdown__item
  color #c0c0c0

</style>