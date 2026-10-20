import axios from "axios"
import { Message } from "@arco-design/web-vue"
import tool from "@/utils/tool"
import { get, isEmpty } from "lodash-es"
import qs from "qs"
import { h } from "vue"
import { IconFaceFrownFill } from "@arco-design/web-vue/dist/arco-vue-icon"

/**
 * 统一的 axios 实例与请求工厂（api/request 与 utils/request 共用）。
 * 两处历史差异（超时时间、参数序列化）通过 options 保留，避免行为变化。
 */
export function createService() {
    const service = axios.create()

    service.interceptors.request.use(
        (config) => config,
        (error) => Promise.reject(error)
    )

    service.interceptors.response.use(
        (response) => {
            if (
                (response.headers["content-disposition"] ||
                    !/^application\/json/.test(response.headers["content-type"])) &&
                response.status === 200
            ) {
                return response.data
            } else if (response.data.size) {
                response.data.code = 500
                response.data.message = "服务器内部错误"
                response.data.success = false
            } else if (response.data.code && response.data.code !== 200) {
                Message.error({
                    content: response.data.message,
                    icon: () => h(IconFaceFrownFill)
                })
            }
            return response.data
        },
        (error) => {
            const err = async (text) => {
                let content = ""
                // responseType: "blob" 时 data 是 Blob，需要先读出文本再解析 message
                if (error.response && error.response.data instanceof Blob) {
                    try {
                        const raw = await error.response.data.text()
                        content = JSON.parse(raw).message || "未知Blob错误"
                    } catch {
                        content = "解析Blob失败"
                    }
                } else {
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
                        tool.local.clear()
                        // 登录接口自身返回 401（账号口令错误）时留在登录页，其余 401 跳回登录
                        if (
                            error.response.data?.data?.code === 40001 ||
                            error.response.data?.data?.detail ===
                                "No active account found with the given credentials"
                        ) {
                            // 账号或口令错误，不跳转
                        } else {
                            window.location.href = "/"
                        }
                        break
                    case 403:
                        err("没有权限访问该资源")
                        break
                    default:
                        err("未知错误！")
                }
            } else {
                err("请求超时，服务器无响应！")
            }
            return Promise.reject(error.response && error.response.data ? error.response.data : null)
        }
    )
    return service
}

export function createRequest(service, options = {}) {
    const { timeout = 20000, stringify } = options
    const stringifyParams = stringify || ((params) => qs.stringify(params))

    return function (config) {
        const env = import.meta.env
        const token = tool.local.get(env.VITE_APP_TOKEN_PREFIX)
        const headers = {
            "Accept-Language": "zh_CN",
            "Content-Type": get(config, "headers.Content-Type", "application/json;charset=UTF-8")
        }
        // 登录页等未登录场景不发 "Bearer undefined"，避免后端把无效头当成凭证处理
        if (token) headers.Authorization = "Bearer " + token
        const configDefault = {
            headers,
            timeout,
            baseURL: env.VITE_APP_OPEN_PROXY === "true" ? env.VITE_APP_PROXY_PREFIX : env.VITE_APP_BASE_URL,
            data: {}
        }
        const option = Object.assign(configDefault, config)
        if (!isEmpty(option.params)) {
            option.url = option.url + "?" + stringifyParams(option.params)
            option.params = {}
        }
        return service(option)
    }
}
