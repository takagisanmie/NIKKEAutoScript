import {defineStore} from 'pinia'

const useSettings = defineStore('Settings', {
    state: () => {
        return {
            simulator_settings:
                {
                    current_simulator: '',
                },
            event_settings:
                {
                    event: '',
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