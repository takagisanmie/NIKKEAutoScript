<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>模拟室</h3>
      <hr>
      <div style="height: 80px">
        难度
        <el-select @change="changeDifficulty" effect="dark" style="display:block;float:right;"
                   v-model="difficulty"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in difficulties"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </div>
      <div style="">
        地区
        <el-select @change="changeArea" effect="dark" style="float:right;" v-model="area"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in areas"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
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
const activate = ref('Task.SimulationRoom.activate')
const nextExecutionTime = ref('Task.SimulationRoom.nextExecutionTime')
const difficulty = ref('')
const area = ref('')


const difficulties = [
  {
    value: '1',
    label: 'Level-1',
  },
  {
    value: '2',
    label: 'Level-2',
  },
  {
    value: '3',
    label: 'Level-3',
  },
  {
    value: '4',
    label: 'Level-4',
  },
  {
    value: '5',
    label: 'Level-5',
  },
]

const areas = [
  {
    value: '1',
    label: 'A',
  },
  {
    value: '2',
    label: 'B',
  },
  {
    value: '3',
    label: 'C',
  }
]

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.SimulationRoom.difficulty',
        'Task.SimulationRoom.area',
      ],
      'task',
      'setSimulationOption'
  )
}

socket.on('setSimulationOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.SimulationRoom.difficulty') {
      console.log(option.value)
      difficulty.value = String(option.value)
    }
    if (option.key === 'Task.SimulationRoom.area') {
      console.log(option.value)
      area.value = String(option.value)
    }
  })
})

const changeDifficulty = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.SimulationRoom.difficulty'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 127)

const changeArea = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.SimulationRoom.area'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 127)

onMounted(() => {
  setOptions()
})

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