let routeTitle = ""
let siteTitle = "测试管理平台"

function setTitle() {
    if (routeTitle) {
        document.title = routeTitle + " - " + siteTitle
        return
    } else {
        document.title = siteTitle
    }
}

export function setRouteTitle(title) {
    routeTitle = title
    setTitle()
}
