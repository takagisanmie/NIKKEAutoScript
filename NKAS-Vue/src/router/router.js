import {createRouter, createWebHashHistory} from "vue-router"

import Main from '@/views/Main/Main.vue'

const router = createRouter({
    routes:
        [
            {
                path: '/',
                component: Main
            },
            {
                path: '/Main',
                name: 'Main',
                component: Main
            },
            {
                path: '/setting',
                name: 'Setting',
                redirect: '/general_setting',
                // redirect: '/conversation_setting',
                component: () => import('@/views/Main/setting/setting.vue'),
                children: [
                    {
                        path: '/general_setting',
                        name: 'general_setting',
                        component: () => import('@/views/Main/setting/general/general.vue'),

                    },
                    {
                        path: '/simulator_setting',
                        name: 'simulator_setting',
                        component: () => import('@/views/Main/setting/simulator/simulator_setting.vue'),

                    },
                    {
                        path: '/reward_setting',
                        name: 'reward_setting',
                        component: () => import('@/views/Main/setting/reward/reward.vue'),

                    },
                    {
                        path: '/destroy_setting',
                        name: 'destroy_setting',
                        component: () => import('@/views/Main/setting/destroy/destroy.vue'),

                    },
                    {
                        path: '/store_setting',
                        name: 'store_setting',
                        component: () => import('@/views/Main/setting/store/store.vue'),

                    },
                    {
                        path: '/friendship_setting',
                        name: 'friendship_setting',
                        component: () => import('@/views/Main/setting/friendship/friendship.vue'),

                    },
                    {
                        path: '/commission_setting',
                        name: 'commission_setting',
                        component: () => import('@/views/Main/setting/commission/commission.vue'),

                    },
                    {
                        path: '/conversation_setting',
                        name: 'conversation_setting',
                        component: () => import('@/views/Main/setting/conversation/conversation_setting.vue'),

                    },
                    {
                        path: '/rookie_arena',
                        name: 'rookie_arena',
                        component: () => import('@/views/Main/setting/rookiearena/rookiearena.vue'),

                    },
                    {
                        path: '/simulation_room',
                        name: 'simulation_room',
                        component: () => import('@/views/Main/setting/simulationroom/simulationroom.vue'),

                    },
                    {
                        path: '/event_setting',
                        name: 'event_setting',
                        component: () => import('@/views/Main/setting/event/event_setting.vue'),

                    }
                ]
            },
        ],
    history: createWebHashHistory()
})

export default router
