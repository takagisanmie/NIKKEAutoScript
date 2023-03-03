<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>咨询列表</h3>
      <hr>
      <div>
        <p style="text-align: center; margin: 0 0 20px">
          <el-transfer @change="nikke_list_change" v-model="Nikke_List_selected" :data="Nikke_List"
                       :titles="['可选', '已选']"
          />
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, onMounted, computed} from 'vue'
import Socket from "@/assets/js/socket"
import useSettings from "@/assets/store/settingStore";
import taskState from "@/views/common/taskState.vue";
import _ from "lodash";
import dayjs from "dayjs";


const socket = Socket.getSocket()
const Settings = useSettings()

function setOptions() {
  socket.emit('getConfigByKeyInConversation',
      {
        'keys':
            [
              {
                'key': 'Task.Conversation.nikkeList'
              }
            ],
      }
  )
}

function nikke_list_change() {
  Socket.updateConfigByKey(
      [
        'Task.Conversation.nikkeList'
      ],
      [
        Nikke_List_selected.value
      ],
      'task',
      'update_success'
  )
}

socket.on('getConfigByKeyInConversation', (result) => {
  _.forEach(result.data.keys, function (option, index) {
    if (option.key === 'Task.Conversation.nikkeList') {
      Nikke_List.value = option.Nikke_list
      Nikke_List_selected.value = option.Nikke_list_selected
    }
  });
})
const activate = ref('Task.Conversation.activate')
const nextExecutionTime = ref('Task.Conversation.nextExecutionTime')
const Nikke_List = ref([])
const Nikke_List_selected = ref([])

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

.el-transfer
  //穿梭框header颜色
  --el-transfer-panel-header-bg-color #393939
  //穿梭框body颜色
  --el-bg-color-overlay #393939

*
  //header字体颜色
  --el-text-color-primary #d8d8d8
  //body字体颜色
  --el-text-color-regular #d8d8d8

</style>