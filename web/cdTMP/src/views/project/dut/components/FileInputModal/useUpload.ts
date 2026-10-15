import { ref } from "vue"
import { Message, Notification } from "@arco-design/web-vue"

const templateDemandObj = {
    chapter: "",
    title: "",
    ident: "",
    demandType: "",
    content: ""
}
// 判断是否为{"__type__": "image","format": "base64","data": "base64数据"}
function isImageObject(obj: any) {
    return (
        obj !== null &&
        typeof obj === "object" &&
        !Array.isArray(obj) &&
        Object.hasOwn(obj, "__type__") &&
        Object.hasOwn(obj, "format") &&
        Object.hasOwn(obj, "data")
    )
}

export default function useUpload(htmlData: any) {
    const parseChapter = ref("") // 定义用户想解析的章节名称
    const selectValue = ref("1") // 定义选择框
    const handleUploadSuccess = (fileItem: any) => {
        const data = fileItem.response.data
        if (!data.children) {
            Notification.error({
                content: "解析失败：请确认上传文件目录级别包含6以上；章节名称正确",
                duration: 3000,
                closable: true
            })
            parseChapter.value = ""
            return
        }
        // 这里就是解析出东西了
        const parsedData = getObjFromChapter(data)
        if (parsedData) {
            enterDemand(parsedData)
        }
        // 上传成功后清空解析章节名称
        parseChapter.value = ""
    }
    const handleUploadError = (fileItem: any) => {
        console.log(fileItem.response)
    }
    const getObjFromChapter = (parseObj: any) => {
        if (parseObj.title === parseChapter.value) return parseObj
        if (Array.isArray(parseObj.children) && parseObj.children.length > 0) {
            for (const child of parseObj.children) {
                const found = getObjFromChapter(child)
                if (found) return found // 递归返回obj或null
            }
        }
        return null // 如果都没找到返回null
    }
    // 辅助函数：（递归）将parseObj转为templateDemandObj录入，递归录入
    const enterDemand = (parseObj: any) => {
        // 下面是录入
        const demandObj = JSON.parse(JSON.stringify(templateDemandObj))
        demandObj.chapter = parseObj.number
        demandObj.title = parseObj.title
        demandObj.ident = parseObj.ordinal ? parseObj.ordinal : "" // 设计需求标识如果没有则为空
        demandObj.demandType = selectValue.value
        // 解析数组，然后添加到内容中
        const content = formatContentForTinyMCE(JSON.parse(parseObj.content))
        demandObj.content = content
        htmlData.value.push(demandObj)
        // 如果有子对象，则再运行一次即可
        if (Array.isArray(parseObj.children) && parseObj.children.length > 0) {
            for (const childObj of parseObj.children) {
                enterDemand(childObj)
            }
        }
    }
    // 上面函数的辅助函数：将数组变为HTML给tinymce使用
    function formatContentForTinyMCE(data: any) {
        let htmlContent = ""
        // 处理普通文本行
        for (const item of data) {
            // 如果是普通文本
            if (typeof item === "string") {
                // 处理表头标记
                if (item.includes("见表") || item.includes("如表") || item.includes("如下表")) {
                    htmlContent += `<p>${item.replace(/见表\d+/, "见下表").replace(/见图\d+/, "见下图")}</p>`
                } else if (item.includes("见图") || item.includes("如图") || item.includes("如下图")) {
                    htmlContent += `<p>${item.replace(/见图\d+/, "见下图").replace(/见表\d+/, "见下表")}</p>`
                } else if (/表\d+/.test(item)) {
                    htmlContent += ``
                } else if (/图\d+/.test(item)) {
                    htmlContent += `${item.replace(/图\d+/, "下图")}`
                } else {
                    htmlContent += `<p>${item}</p>`
                }
            }
            // 如果是对象（根据后端逻辑是图片）
            else if (isImageObject(item)) {
                // item现在是对象，其data是base64字符串
                htmlContent += `<p><img src="data:image/png;base64,${item.data}" style="max-width:100%; height:auto; margin: 0 auto; display: block;"></img></p>`
            }
            // 处理表格数据
            else if (Array.isArray(item)) {
                htmlContent += '<table border="1" style="margin: 0 auto;max-width:70%; border-collapse:collapse;">'
                // 处理表头
                const headers = item[0].split("\t")
                htmlContent += "<thead><tr>"
                for (const header of headers) {
                    htmlContent += `<th style="padding:8px; border:1px solid #ddd;">${header}</th>`
                }
                htmlContent += "</tr></thead>"
                // 处理表格内容
                htmlContent += "<tbody>"
                for (let i = 1; i < item.length; i++) {
                    const cells = item[i].split("\t")
                    htmlContent += "<tr>"
                    for (const cell of cells) {
                        // 处理单元格内的换行符
                        const formattedCell = cell.replace(/\n/g, "<br>")
                        htmlContent += `<td style="padding:8px; border:1px solid #ddd;">${formattedCell}</td>`
                    }
                    htmlContent += "</tr>"
                }
                htmlContent += "</tbody></table>"
            }
        }
        return htmlContent
    }
    return { handleUploadSuccess, handleUploadError, parseChapter, selectValue }
}
