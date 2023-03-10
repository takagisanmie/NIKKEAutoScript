<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>活动</h3>
      <hr>
      <div>
        活动
        <el-select @change="changeEvent" effect="dark" style="float:right;width: 210px;" v-model="event"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in events"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </div>
      <br>
      <br>
      <div>
        关卡名称
        <el-input style="width: 210px;float: right" @input="_changeEvent"
                  v-model="Settings.event_settings.event"/>
        <p>例如1-5，1-11</p>
      </div>
      <div>
        完成当前难度所有未完成的关卡
        <el-switch size="large" width="60px"
                   style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                   @change="_finishAllEvent" v-model="finishAllEvent"/>
      </div>
      <br>
      <div>
        难度
        <el-select @change="changeDifficulty" effect="dark" style="float:right;width: 210px;" v-model="difficulty"
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
      <div v-if="isLarge">
        <br>
        <br>
        Story
        <el-select @change="changeStory" effect="dark" style="float:right;width: 210px;" v-model="story"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in stories"
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
import useSettings from "@/assets/store/settingStore";
import _ from "lodash";
import taskState from "@/views/common/taskState.vue";

const difficulties = [
  {
    value: 0,
    label: '普通',
  },
  {
    value: 1,
    label: '困难',
  }
]

const stories = [
  {
    value: 1,
    label: 'Part1',
  },
  {
    value: 2,
    label: 'Part2',
  }
]

const socket = Socket.getSocket()
const Settings = useSettings()
const events = ref('')
const event = ref()
const isLarge = ref(false)
const finishAllEvent = ref(false)
const difficulty = ref(0)
const story = ref(1)
const activate = ref('Task.Event.activate')
const nextExecutionTime = ref('Task.Event.nextExecutionTime')

const changeEvent = _.debounce(() => {
  Socket.updateConfigByKey(
      [
        'Task.Event.currentEvent'
      ],
      [
        event.value
      ],
      'task',
      'update_success'
  )

  setOptions()
}, 2000)


const _changeEvent = _.debounce(() => {
  Socket.updateConfigByKey(
      [
        'Task.Event.event'
      ],
      [
        Settings.event_settings.event
      ],
      'task',
      'update_success'
  )
}, 2000)

const changeDifficulty = _.debounce(() => {
  Socket.updateConfigByKey(
      [
        'Task.Event.difficulty'
      ],
      [
        difficulty.value
      ],
      'task',
      'update_success'
  )
}, 2000)

const changeStory = _.debounce(() => {
  Socket.updateConfigByKey(
      [
        'Task.Event.part'
      ],
      [
        story.value
      ],
      'task',
      'update_success'
  )
}, 2000)

const _finishAllEvent = _.debounce(async () => {
  await Socket.updateConfigByKey(
      [
        'Task.Event.finishAllEvent'
      ],
      [
        finishAllEvent.value
      ],
      'task',
      'update_success'
  )
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.Event.currentEvent',
        'Task.Event.historyEvent',
        'Task.Event.difficulty',
        'Task.Event.finishAllEvent',
        'Task.Event.part'
      ],
      'task',
      'setEventOptions'
  )
}

socket.on('setEventOptions', async (result) => {
  await _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.Event.finishAllEvent') {
      finishAllEvent.value = option.value
    } else if (option.key === 'Task.Event.difficulty') {
      difficulty.value = option.value
    } else if (option.key === 'Task.Event.part') {
      story.value = option.value
    } else if (option.key === 'Task.Event.historyEvent') {
      events.value = option.value
    } else if (option.key === 'Task.Event.currentEvent') {
      event.value = option.value
    }
  });

  _.forEach(events.value, function (e, index) {
    if (e.value === event.value) {
      if (e.type === 1) {
        isLarge.value = true
      } else {
        isLarge.value = false
      }
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

<style lang="stylus" scoped>
*
  --el-fill-color-blank #333333
  --el-text-color-regular #c0c0c0

.el-select-dropdown__item.hover, .el-select-dropdown__item:hover
  background-color #4d4d4d

.el-select-dropdown__item
  color #c0c0c0
</style>