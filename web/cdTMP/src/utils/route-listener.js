/**
 * 功能：
 * 单独监听路由会浪费渲染性能,所以这里使用发布订阅模式(mitt)去进行分发管理。
 */
import mitt from "mitt"

const emitter = mitt()

const key = Symbol("ROUTE_CHANGE")

let latestRoute
// 传入一个到达路由to，发出一个事件，然后把到达路由to传入latestRoute
export function setRouteEmitter(to) {
    emitter.emit(key, to)
    latestRoute = to
}
// handler为路由变化后的处理函数，返回取消监听的函数（只移除自己）
export function listenerRouteChange(handler, immediate = true) {
    emitter.on(key, handler)
    if (immediate && latestRoute) {
        handler(latestRoute)
    }
    return () => emitter.off(key, handler)
}

export function removeRouteListener(handler) {
    if (handler) {
        emitter.off(key, handler)
    } else {
        emitter.off(key)
    }
}
