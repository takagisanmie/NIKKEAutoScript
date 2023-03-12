<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>收获</h3>
      <hr>
      <div>
        领取特殊竞技场点数
        <el-switch inline-prompt size="large" width="60px"
                   style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                   @change="_arena" v-model="arena"/>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import Socket from "@/assets/js/socket"
import taskState from "@/views/common/taskState.vue";
import _ from "lodash";

const socket = Socket.getSocket()
const activate = ref('Task.Reward.activate')
const nextExecutionTime = ref('Task.Reward.nextExecutionTime')

const arena = ref(false)

const _arena = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Task.Reward.arena'
      ],
      [
        arena.value
      ],
      'task',
      'update_success'
  )
  socket.emit('setRewardOption')
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.Reward.arena'
      ],
      'task',
      'setRewardOption'
  )
}

socket.on('setRewardOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.Reward.arena') {
      arena.value = option.value
    }
  });
})

onMounted(() => {
  setOptions()
})


</script>

<style lang="stylus" scoped>

</style>