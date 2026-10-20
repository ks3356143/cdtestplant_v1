// 本地存储的下载前缀：优先用 VITE_APP_STORAGE_URL，未配置时从接口基址推导（去掉 /api 后缀）
const apiBase = import.meta.env.VITE_APP_BASE_URL || "";
const derivedOrigin = apiBase.replace(/\/api\/?$/, "");

export default {
    storage: {
        LOCAL: import.meta.env.VITE_APP_STORAGE_URL || derivedOrigin,
        OSS: "",
        COS: "",
        QINIU: ""
    },

    storageMode: {
        1: "LOCAL",
        2: "OSS",
        3: "QINIU",
        4: "COS"
    }
}
