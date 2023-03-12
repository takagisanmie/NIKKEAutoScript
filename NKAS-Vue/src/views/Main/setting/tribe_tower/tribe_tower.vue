<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>企业塔</h3>
      <hr>
      <div>
        只完成每日任务，在进入后退出
        <el-switch inline-prompt size="large" width="60px"
                   style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                   @change="_daily" v-model="daily"/>
      </div>
      <br>
      <!--      <div>-->
      <!--        尝试完成开放的企业塔-->
      <!--        <el-switch inline-prompt size="large" width="60px"-->
      <!--                   style="&#45;&#45;el-switch-on-color: #626aef; &#45;&#45;el-switch-off-color: #ff4949;float: right;"-->
      <!--                   @change="_arena" v-model="arena"/>-->
      <!--      </div>-->
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import Socket from "@/assets/js/socket"
import taskState from "@/views/common/taskState.vue";
import _ from "lodash";

const socket = Socket.getSocket()
const activate = ref('Task.TribeTower.activate')
const nextExecutionTime = ref('Task.TribeTower.nextExecutionTime')

const daily = ref(false)

const _daily = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Task.TribeTower.daily'
      ],
      [
        daily.value
      ],
      'task',
      'update_success'
  )
  socket.emit('setTribeTowerOption')
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.TribeTower.daily'
      ],
      'task',
      'setTribeTowerOption'
  )
}

socket.on('setTribeTowerOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.TribeTower.daily') {
      daily.value = option.value
    }
  });
})

onMounted(() => {
  setOptions()
})

</script>

<style lang="stylus" scoped>

</style>