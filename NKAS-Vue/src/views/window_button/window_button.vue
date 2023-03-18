<template>
  <div id="header">
    <span>
      <img id="LOGO" src="../../assets/img/Helm.png" alt="">
    </span>
    <span id="LOGO-TEXT">{{ packageJson.name }}</span>
    <span :style="{color:props.isConnected?'#7dd08f':'#cc4f4f'}"
          id="LOGO-TEXT">{{ props.isConnected ? 'Socket已连接' : 'Socket未连接' }}</span>
    <div @click="ToClose" class="win-button" id="Close">
      <el-icon>
        <Close/>
      </el-icon>
    </div>
    <div @click="ToFullScreen" class="win-button" id="FullScreen">
      <el-icon>
        <FullScreen/>
      </el-icon>
    </div>
    <div @click="ToMin" class="win-button" id="Minus">
      <el-icon>
        <Minus/>
      </el-icon>
    </div>
  </div>
</template>

<script setup>
import {
  Minus, Close, FullScreen
} from '@element-plus/icons-vue'
import packageJson from '../../../package.json'
import {defineProps} from "vue";
import Socket from "@/assets/js/socket";

const socket = Socket.getSocket()

const props = defineProps(['isConnected'])

const ToMin = () => {
  window.WindowStrategyAPI.WindowToMin()
}

const ToFullScreen = () => {
  window.WindowStrategyAPI.WindowToFullScreen()
}

const ToClose = async () => {
  await socket.emit('stopNKAS')
  window.WindowStrategyAPI.WindowToClose()
}

</script>

<style lang="stylus" scoped>
#LOGO
  border-radius 40px
  width 50px

#LOGO-TEXT
  position relative
  display contents
  bottom 15px
  font-size 22px
  font-weight bold

#header
  width 100%
  height 57px
  //border 2px solid red
  background-color #333333
  -webkit-app-region drag
  -webkit-user-select none

#header > .win-button, #LOGO-TEXT
  color #c0c0c0
  display inline-block;
  margin 16px
  -webkit-app-region none


#Minus, #FullScreen, #Close
  float right
  width 25px
  height 25px
  //position absolute


  :hover
    color #727272
    cursor pointer


.el-icon
  color #c0c0c0


</style>
