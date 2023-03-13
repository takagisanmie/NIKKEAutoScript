<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>每日任务</h3>
      <hr>
      <!--      <div>-->
      <!--        升级NIKKE-->
      <!--        <el-switch inline-prompt size="large" width="60px"-->
      <!--                   style="&#45;&#45;el-switch-on-color: #626aef; &#45;&#45;el-switch-off-color: #ff4949;float: right;"-->
      <!--                   @change="_nikke_upgrade" v-model="nikke_upgrade"/>-->
      <!--      </div>-->
      <div>
        升级装备
        <el-switch inline-prompt size="large" width="60px"
                   style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                   @change="_equipment_upgrade" v-model="equipment_upgrade"/>
        <p>会使用一个模组高级增强器或模组推进器，升级背包中的任意一个装备</p>
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
const activate = ref('Task.Daily.activate')
const nextExecutionTime = ref('Task.Daily.nextExecutionTime')

const nikke_upgrade = ref(false)
const equipment_upgrade = ref(false)

const _nikke_upgrade = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Task.Daily.nikkeUpgrade'
      ],
      [
        nikke_upgrade.value
      ],
      'task',
      'update_success'
  )
  socket.emit('setRewardOption')
}, 127)

const _equipment_upgrade = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Task.Daily.equipmentUpgrade'
      ],
      [
        equipment_upgrade.value
      ],
      'task',
      'update_success'
  )
  socket.emit('setRewardOption')
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.Daily.nikkeUpgrade',
        'Task.Daily.equipmentUpgrade'
      ],
      'task',
      'setDailyOption'
  )
}

socket.on('setDailyOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.Daily.nikkeUpgrade') {
      nikke_upgrade.value = option.value
    } else if (option.key === 'Task.Daily.equipmentUpgrade') {
      equipment_upgrade.value = option.value
    }
  });
})

onMounted(() => {
  setOptions()
})

</script>

<style lang="stylus" scoped>

</style>