<template>
  <h3>任务设置</h3>
  <hr>
  <div>
    启用该功能
    <el-switch size="large" width="60px"
               style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
               @change="changeState" v-model="activate"/>
  </div>
  <br>
  <div>
    下次运行时间
    <el-input style="width: auto;float: right;font-size: 17px;"
              @input="changeTime" v-model="time"/>
  </div>
</template>

<script setup>
import {ref, defineProps, onMounted} from "vue";
import Socket from "@/assets/js/socket";
import _ from "lodash";
import dayjs from 'dayjs'
import {ElNotification} from "element-plus";

const props = defineProps(['socket', 'activate', 'time'])
const socket = props.socket

function setOptions() {
  Socket.getConfigByKey(
      [
        props.activate,
        props.time,
      ],
      'task',
      'setTaskState'
  )
}

const changeState = _.debounce(() => {
  Socket.updateConfigByKey(
      [
        props.activate
      ],
      [
        activate.value
      ],
      'task',
      'update_success'
  )
}, 127)

const changeTime = _.debounce(() => {
  if (dayjs(time.value).isValid()) {
    Socket.updateConfigByKey(
        [
          props.time
        ],
        [
          dayjs(time.value).unix()
        ],
        'task',
        'update_success'
    )
  } else {
    ElNotification({
      title: '时间格式不正确',
      type: 'warning',
    })
  }
}, 1227)

const activate = ref(false)
const time = ref('')

socket.on('setTaskState', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === props.time) {
      time.value = dayjs.unix(option.value).format('YYYY-MM-DD HH:mm:ss')
    } else if (option.key === props.activate) {
      activate.value = option.value
    }
  });
})

onMounted(() => {
  setOptions()
  let x = document.querySelectorAll('.el-input__wrapper')
  _.forEach(x, function (input, index) {
    input.style.backgroundColor = "#333333";
  });
  x = document.querySelectorAll('.el-input__inner')
  _.forEach(x, function (input, index) {
    input.style.color = "#c0c0c0";
  });
})

</script>

<style scoped>

</style>