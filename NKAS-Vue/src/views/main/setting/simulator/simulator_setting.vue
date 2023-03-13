<template>
  <div style="margin:10px;color: #c0c0c0;">
    <div>
      <h3>模拟器</h3>
      <hr>
      <div>
        模拟器 Serial
        <el-input style="width: 200px;float: right" @input="changeSerial"
                  v-model="Settings.simulator_settings.current_simulator"/>
      </div>
      <div>
        <br>
        模拟器默认 Serial：
        <br>
        - 雷电模拟器 emulator-5554
        <br>
        - MuMu模拟器 127.0.0.1:7555
      </div>
      <br>
      <div>
        服务器
        <el-select @change="changeServer" effect="dark" style="float:right;width: 200px;" v-model="server"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in servers"
              :key="item.value"
              :label="item.label"
              :value="item.value"
          />
        </el-select>
      </div>
      <br>
      <br>
      <div>
        加速器
        <el-select @change="changeAccelerator" effect="dark" style="float:right;width: 200px;" v-model="accelerator"
                   class="m-2" placeholder=" "
                   size="large">
          <el-option
              v-for="item in accelerators"
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
import {ref, onMounted, computed} from 'vue'
import Socket from "@/assets/js/socket"
import useSettings from "@/assets/store/settingStore";
import _ from 'lodash'
import dayjs from "dayjs";

const socket = Socket.getSocket()
const Settings = useSettings()
const accelerator = ref('')
const server = ref('')


const changeSerial = _.debounce(() => {
  Socket.updateConfigByKey(
      [
        'Simulator.Serial'
      ],
      [
        Settings.simulator_settings.current_simulator
      ],
      'config',
      'serial_update_success'
  )
}, 2000)

const changeAccelerator = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Simulator.Accelerator'
      ],
      [
        val
      ],
      'config',
      'update_success'
  )
}, 127)

const changeServer = _.debounce((val) => {
  Socket.updateConfigByKey(
      [
        'Server'
      ],
      [
        val
      ],
      'config',
      'update_success'
  )
}, 127)

function setOptions() {
  Socket.getConfigByKey(
      [
        'Accelerators',
        'Simulator.Accelerator',
        'Servers',
        'Server',
      ],
      'config',
      'setAccelerator'
  )
}

const accelerators = ref([])
const servers = ref([])

socket.on('setAccelerator', (result) => {
  _.forEach(result.result, function (option, index) {
    if (option.key === 'Accelerators') {
      accelerators.value = option.value
    }
    else if (option.key === 'Simulator.Accelerator') {
      accelerator.value = option.value
    }
    else if (option.key === 'Servers') {
      servers.value = option.value
    }
    else if (option.key === 'Server') {
      server.value = option.value
    }
  })
})


onMounted(() => {
  setOptions()
  document.querySelector('.el-input__wrapper').style.backgroundColor = "#333333";
  document.querySelector('.el-input__inner').style.color = "#c0c0c0";

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