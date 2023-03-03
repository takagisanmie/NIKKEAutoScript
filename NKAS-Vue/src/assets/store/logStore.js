import {provide} from "vue";
import {defineStore} from 'pinia'
import _ from 'lodash'

const size = 50

const useNKASLog = defineStore('NKAS-Logs', {
    state: () => {
        return {
            Logs: []
        }
    },
    actions: {
        insert(item) {
            this.Logs.push(item)
            if (this.Logs.length > size) {
                this.Logs.shift()
            }
        },
        shift() {
            this.Logs.shift()
        }
    },
    //持久化
    // persist: true
})

export default useNKASLog