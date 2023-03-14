<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <taskState :socket='socket' :activate="activate" :time="nextExecutionTime"/>
      <h3>通用商店</h3>
      <hr>
      <br>
      <h3>竞技场商店</h3>
      <hr>
      <div>
        启用此功能
        <el-switch inline-prompt size="large" width="60px"
                   style="--el-switch-on-color: #626aef; --el-switch-off-color: #ff4949;float: right;"
                   @change="_activate_arena_store" v-model="activate_arena_store"/>
      </div>
      <br>
      <br>
      <div style="line-height: 38px">
        优先购买
        <el-input style="width: 1000px;height: 38px;float: right;font-size: 17px"
                  @input="_arena_product_list" v-model="arena_product_list"/>
        <p>例如: ‘electric > fire > selection_box > water > wind > iron’，不填写则不购买</p>
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
const activate = ref('Task.FreeStore.activate')
const nextExecutionTime = ref('Task.FreeStore.nextExecutionTime')
const activate_arena_store = ref()
const arena_product_list = ref()

const _activate_arena_store = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.FreeStore.activate_arena_store'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 127)

const _arena_product_list = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Task.FreeStore.arena_product_list'
      ],
      [
        val
      ],
      'task',
      'update_success'
  )
}, 1270)

socket.on('setFreeStoreOption', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Task.FreeStore.activate_arena_store') {
      activate_arena_store.value = option.value
    } else if (option.key === 'Task.FreeStore.arena_product_list') {
      arena_product_list.value = option.value
    }
  })
})

function setOptions() {
  Socket.getConfigByKey(
      [
        'Task.FreeStore.activate_arena_store',
        'Task.FreeStore.arena_product_list',
      ],
      'task',
      'setFreeStoreOption'
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