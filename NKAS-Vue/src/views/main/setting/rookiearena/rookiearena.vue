<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>新人竞技场</h3>
      <hr>
      <div style="">
        目标
        <el-select @change="changeTarget" effect="dark" style="float:right;" v-model="target"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in targets"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </div>
      <br>
      <br>
      <div>
        战力X
        <el-input style="width: auto;float: right;font-size: 17px;height: 43px"
                  @input="_under" v-model="under"/>
        <p>选择的目标战力 &lt; 自身战斗力 - 战力X，填0，则选择目标对象</p>
      </div>
      <div>
        刷新次数
        <el-input style="width: auto;float: right;font-size: 17px;height: 43px"
                  @input="_refresh_chance" v-model="refresh_chance"/>
        <p>在刷新完后，没有符合条件的目标，则选择目标对象</p>

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
const activate = ref('Task.RookieArena.activate')
const nextExecutionTime = ref('Task.RookieArena.nextExecutionTime')
const target = ref()
const refresh_chance = ref(0)
const under = ref(0)


const targets = [
  {
    value: 1,
    label: '一号位',
  },
  {
    value: 2,
    label: '二号位',
  },
  {
    value: 3,
    label: '三号位',
  }
]

const changeTarget = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.RookieArena.target'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 127)

const _under = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.RookieArena.under'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 1270)

const _refresh_chance = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.RookieArena.refresh_chance'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 1270)

socket.on('setRookieArenaOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.RookieArena.target') {
      console.log(option.value)
      target.value = option.value
    } else if (option.key === 'Task.RookieArena.under') {
      console.log(option.value)
      under.value = option.value
    } else if (option.key === 'Task.RookieArena.refresh_chance') {
      console.log(option.value)
      refresh_chance.value = option.value
    }
  })
})

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.RookieArena.target',
        'Task.RookieArena.under',
        'Task.RookieArena.refresh_chance',
      ],
      'task',
      'setRookieArenaOption'
  )
}

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