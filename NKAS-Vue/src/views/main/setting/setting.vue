<template>
  <el-main>
    <el-space style="float: left" direction="vertical" wrap>
      <el-card id="card1" class="box-card" style="width: 250px;height: 100%;">
        <el-menu
            class="el-menu-vertical-demo"
            :router="true"
            default-active="1-1"
        >
          <el-sub-menu index="1">
            <template #title>
              <span>设置</span>
            </template>
            <el-menu-item-group>
              <el-menu-item route="general_setting" index="1-1">NKAS设置</el-menu-item>
              <el-menu-item route="simulator_setting" index="1-2">模拟器设置</el-menu-item>
              <el-menu-item route="reward_setting" index="1-3">收获</el-menu-item>
              <el-menu-item route="destroy_setting" index="1-4">歼灭</el-menu-item>
              <el-menu-item route="store_setting" index="1-5">商店</el-menu-item>
              <el-menu-item route="commission_setting" index="1-6">委托</el-menu-item>
              <el-menu-item route="conversation_setting" index="1-7">咨询</el-menu-item>
              <el-menu-item route="rookie_arena" index="1-8">新人竞技场</el-menu-item>
              <el-menu-item route="simulation_room" index="1-9">模拟室</el-menu-item>
              <el-menu-item route="tribe_tower" index="1-10">企业塔</el-menu-item>
              <el-menu-item route="daily" index="1-11">每日任务</el-menu-item>
              <el-menu-item route="event_setting" index="1-12">活动</el-menu-item>
            </el-menu-item-group>
          </el-sub-menu>
        </el-menu>
      </el-card>
      <!--      <el-card id="card2" class="box-card" style="width: 250px;height: 435px;">-->
      <!--        <template #header>-->
      <!--          <div class="card-header">-->
      <!--            <span>Card name2</span>-->
      <!--          </div>-->
      <!--        </template>-->
      <!--        <div v-for="o in 4" :key="o" class="text item">-->
      <!--          {{ 'List item ' + o }}-->
      <!--        </div>-->
      <!--      </el-card>-->
    </el-space>
    <div id="Setting">
      <router-view/>
    </div>
  </el-main>
</template>

<script setup>
import Socket from "@/assets/js/socket";

const socket = Socket.getSocket()


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

.el-aside, .el-menu, .el-menu > *
  //侧边栏背景色
  background-color #333333
  border none
  //菜单悬浮时颜色
  --el-menu-hover-bg-color #5f5f5f
  //图标选中时颜色
  --el-menu-active-color #b5dbff
  //图标未选中时颜色
  --el-menu-text-color #c0c0c0

*
  font-size 19px

#Setting
  position: relative
  border-radius 8px
  display inline-block
  left 10px
  width calc(99% - 248px)
  height calc(99% - 57px)
  background-color #353535
  float left
</style>