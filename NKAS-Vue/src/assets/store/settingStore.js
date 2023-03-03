import {defineStore} from 'pinia'
import _ from 'lodash'

const useSettings = defineStore('Settings', {
    state: () => {
        return {
            simulator_settings:
                {
                    current_simulator: '',
                },
            event_settings:
                {
                    step: '',
                },
        }
    },
    actions: {
        update(option) {

        },
    },
    //持久化
    persist: true
})
export default useSettings