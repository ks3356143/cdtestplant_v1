import axios from "axios"
import { Message } from "@arco-design/web-vue"
import tool from "@/utils/tool"
import { get, isEmpty } from "lodash-es"
import qs, { stringify } from "qs"
import { h } from "vue"
import { IconFaceFrownFill } from "@arco-design/web-vue/dist/arco-vue-icon"

// 创建axios实例，添加请求和响应拦截器，返回该axios实例
function createService() {
    // 创建axios实例
    const service = axios.create()

    // 实例的request请求拦截器
    service.interceptors.request.use(
        (config) => config,
        (error) => {
            return Promise.reject(error)
        }
    )
    // 实例的response响应拦截器
    service.interceptors.response.use(
        (res) => {
            if (
                (res.headers["content-disposition"] || !/^application\/json/.test(res.headers["content-type"])) &&
                res.status === 200
            ) {
                return res.data
                // 如果发现data中有size字段直接报错
            } else if (res.data.size) {
                res.data.code = 500
                res.data.message = "服务器内部错误"
                res.data.success = false
            } else if (res.data.code && res.data.code !== 200) {
                // 如果data里面code字段不为200
                Message.error({
                    content: res.data.message,
                    icon: () => h(IconFaceFrownFill)
                })
            }
            return res.data
        },
        (error) => {
            const err = async (text) => {
                let content = ""
                // 在设置axios为responseType: "blob"时候，data为Blob对象，需要解析Blob
                if (error.response && error.response.data instanceof Blob) {
                    try {
                        const text = await error.response.data.text()
                        content = JSON.parse(text).message && JSON.parse(text).message
                        if (!content) {
                            content = "未知Blob错误"
                        }
                    } catch (e) {
                        Message.error("解析Blob失败")
                    }
                } else {
                    // 非Blob正常错误响应
                    content =
                        error.response && error.response.data && error.response.data.message
                            ? error.response.data.message
                            : text
                }
                Message.error({
                    content,
                    icon: () => h(IconFaceFrownFill)
                })
            }
            if (error.response && error.response.data) {
                switch (error.response.status) {
                    case 404:
                        err("服务器资源不存在")
                        break
                    case 500:
                        err("服务器内部错误")
                        break
                    case 400:
                        err("服务器抛出逻辑错误")
                        break
                    case 401:
                        err("登录状态已过期，需要重新登录")
                        // 清除本地localStorage
                        tool.local.clear()
                        // 移动到网站的根目录-这里不需要因为导航守卫可以返回login页面
                        if (
                            error.response.data.data.code === 40001 ||
                            error.response.data.data.detail === "No active account found with the given credentials"
                        ) {
                        } else {
                            window.location.href = "/"
                        }
                        break
                    case 403:
                        err("没有权限访问该资源")
                        break
                    default:
                        err("未知错误！")
                        break
                }
            } else {
                err("请求超时，服务器无响应！")
            }
            return Promise.reject(error.response && error.response.data ? error.response.data : null)
        }
    )
    return service
}

/**
 * @description 创建请求方法
 * @param {Object} service axios 实例
 */
function createRequest(service) {
    return function (config) {
        const env = import.meta.env
        const token = tool.local.get(env.VITE_APP_TOKEN_PREFIX)
        const configDefault = {
            headers: {
                Authorization: "Bearer " + token,
                "Accept-Language": "zh_CN",
                "Content-Type": get(config, "headers.Content-Type", "application/json;charset=UTF-8")
            },
            timeout: 20000,
            baseURL: env.VITE_APP_OPEN_PROXY === "true" ? env.VITE_APP_PROXY_PREFIX : env.VITE_APP_BASE_URL,
            data: {}
        }
        const option = Object.assign(configDefault, config)
        if (!isEmpty(option.params)) {
            option.url = option.url + "?" + stringify(option.params)
            option.params = {}
        }
        return service(option)
    }
}

export const service = createService()
export const request = createRequest(service)
