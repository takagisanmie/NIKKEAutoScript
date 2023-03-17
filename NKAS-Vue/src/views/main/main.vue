<template>
  <el-main>
    <el-space style="float: left" direction="vertical" wrap>
      <el-card id="card1" class="box-card" style="width: 250px">
        <template #header>
          <div class="card-header">
            <span> {{ schedulerState ? '运行中' : '等待中' }}</span>
            <el-button @click="schedulerState ?  stopScheduler() : startScheduler()" id="start" color="#626aef">
              {{ schedulerState ? '停止' : '运行' }}
            </el-button>
          </div>
        </template>
        <div v-for="task in TaskListStates.taskList" class="text item">
          <span v-if="task.nextExecutionTime <= now && task.activate == true"
                style="font-size: 19px;display:block;"> {{ task.displayName }}</span>
          <span v-if="task.nextExecutionTime <= now && task.activate == true"
                style="margin-top: 8px;display:block;margin-bottom: 8px">{{
              task.displayDate
            }}</span>
        </div>
      </el-card>
      <el-card id="card2" class="box-card" style="width: 250px">
        <template #header>
          <div class="card-header">
            <span>队列中</span>
          </div>
        </template>
        <div v-for="task in TaskListStates.taskList" class="text item">
          <span v-if="task.nextExecutionTime >= now && task.activate == true"
                style="font-size: 19px;display:block;"> {{ task.displayName }}</span>
          <span v-if="task.nextExecutionTime >= now && task.activate == true"
                style="margin-top: 8px;display:block;margin-bottom: 8px">{{
              task.displayDate
            }}</span>
        </div>
      </el-card>
    </el-space>
    <div id="console">
      <Console></Console>
    </div>
  </el-main>
</template>

<script setup>
import Console from "@/views/main/console/console.vue";
import {inject, ref, onMounted, computed} from "vue";
import Socket from "@/assets/js/socket"
import Log from "@/assets/js/Log";
import _ from 'lodash'
import dayjs from 'dayjs'
import useTaskListStates from "@/assets/store/task/taskStatesStore";

const TaskListStates = useTaskListStates()
const schedulerState = ref(false)
const socket = Socket.getSocket()
const NKASLog = inject('NKASLog')
const now = dayjs().unix()

const startScheduler = () => {
  if (socket.connected) {
    Log.INFO('运行调度器', NKASLog)
    socket.emit('startScheduler')
    schedulerState.value = true
  } else {
    Log.ERROR('Socket还未连接', NKASLog)
  }
}

const stopScheduler = () => {
  Log.INFO('停止调度器', NKASLog)
  socket.emit('stopScheduler')
  schedulerState.value = false
}

socket.on('checkSchedulerState', (result) => {
  schedulerState.value = result.state
})

socket.on('checkAllTaskStates', (result) => {
  _.forEach(result.data.Task, function (value) {
    value.displayDate = dayjs.unix(value.nextExecutionTime).format('YYYY-MM-DD HH:mm:ss')
  });
  TaskListStates.update(result.data.Task)
})

//加载所有任务信息
// const task_list_states = ref({})
// task_list_states = computed(() => {
//   _.forEach(task_list_states.value.Task, function (value, task) {
//     value.displayDate = dayjs.unix(value.nextExecutionTime).format('YYYY-MM-DD HH:mm:ss')
//     console.log(value)
//   });
//   return _.sortBy(task_list_states.value.Task, ['nextExecutionTime']);
// })

onMounted(() => {
  socket.emit('checkSchedulerState')
  socket.emit('checkAllTaskStates')
})

</script>

<style lang="stylus" scoped>
.el-main
  width 100%
  //Main背景色
  --el-main-padding 10px
  background-color #4f4f4f

.el-card
  --el-card-border-color #c0c0c0
  border-radius 8px

#card1, #card2
  color #c0c0c0
  border none
  background-color #333333
  height calc(99% - 57px)


#console
  position: relative
  border-radius 8px
  display inline-block
  left 10px
  width calc(99% - 248px)
  height calc(99% - 57px)
  background-color #353535
  float left
  overflow hidden

#start
  width 80px
  position relative
  left 80px


</style>