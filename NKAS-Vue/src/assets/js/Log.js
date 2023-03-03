import dayjs from 'dayjs'
import {inject} from "vue";

export default class Log {
    static INFO(message, NKASLog) {
        let date = dayjs().format('HH:mm:ss:SSS')
        let info = `<span style='width: auto;position:relative;top:0px;left:10px;display:block;font-size: 19px;'>
                      <span style="color:#54bac0;">INFO&nbsp&nbsp&nbsp&nbsp</span>
                      <span style="color:#61a06b;">&nbsp&nbsp&nbsp${date}&nbsp</span>
                      ${message}
                    </span>`
        NKASLog.insert(info)
    }

    static ERROR(message, NKASLog) {
        let date = dayjs().format('HH:mm:ss:SSS')
        let info = `<span style='width: auto;position:relative;top:0px;left:10px;display:block;font-size: 19px;color: #cc4f4f'>
                      <span style="color:#cc4f4f;">ERROR&nbsp&nbsp&nbsp&nbsp</span>
                      <span style="color:#61a06b;">${date}&nbsp</span>
                      ${message}
                    </span>`
        NKASLog.insert(info)
    }

    static LINE(message, NKASLog) {
        let info = `<span style='width: auto;position:relative;top:0px;left:10px;display:block;font-size: 19px;text-align: center;'>
                      <hr style="height 1px;background-color: #00ff4d;border none;">
                         ${message}
                      <hr style="height 1px;background-color: #00ff4d;border none;">
                    </span>`
        NKASLog.insert(info)
    }
}
