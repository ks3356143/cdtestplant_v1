import { Message } from "@arco-design/web-vue"

export default {
    /**
     * 生成最终产品文档的进度条模块
     */
    async create_entire_doc(visible, isComplete, api, record_id, docName, fragmentList) {
        visible.value = true
        isComplete.value = false
        try {
            // 1. 调用生成接口，等待文档生成完成，获取下载令牌
            const res = await api({ id: record_id, frag: fragmentList })
            const token = res.download_token || res.data?.download_token
            if (!token) {
                throw new Error("生成文档失败：未获取到下载令牌")
            }
            // 2. 构建下载 URL（根据你的后端路由，这里假设前缀是 /create/download/{token}）
            const downloadUrl = `/api/create/download/${token}`
            // 3. 隐藏 iframe 触发浏览器原生下载（即刻弹出保存框）
            const iframe = document.createElement("iframe")
            iframe.style.display = "none"
            iframe.src = downloadUrl
            document.body.appendChild(iframe)
            // 延迟移除 iframe，确保下载已触发
            setTimeout(() => {
                if (document.body.contains(iframe)) {
                    document.body.removeChild(iframe)
                }
            }, 2000)
            isComplete.value = true
            Message.success("文档生成并下载成功，请打开问题全选->F9更新其中的域!")
        } catch (err) {
            console.error(err)
            isComplete.value = true
            visible.value = false
            Message.error(err.message || "文档下载失败")
        }
    }
}
