import {provide} from "vue";
import {defineStore} from 'pinia'
import _ from 'lodash'


const useTaskListStates = defineStore('TaskListStates', {
    state: () => {
        return {
            taskList: {},
        }
    },
    actions: {
        update(list) {
            this.taskList = list
        },
    },
    //持久化
    persist: true
})

export default useTaskListStates