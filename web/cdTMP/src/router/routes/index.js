// 导入modules文件夹所有js文件
const modules = import.meta.glob("./modules/*.js", { eager: true })
// 导入externalModules下面所有js文件
const externalMoudles = import.meta.glob("./externalModules/*.js", { eager: true })
/**
 * @description: 传入一个路由文件和一个空数组
 * @return: 返回文件路由的数组
 */
function formatModules(_modules, result) {
    Object.keys(_modules).forEach((key) => {
        const defaultModule = _modules[key].default // 取文件值需要.default
        if (!defaultModule) return
        const moduleList = Array.isArray(defaultModule) ? [...defaultModule] : [defaultModule]
        result.push(...moduleList)
    })
    return result
}

/**
 * @description: 该变量直接获取moduels文件夹下路由数组
 * @return: 返回文件路由的数组
 */
export const appRoutes = formatModules(modules, [])
export const appExternalRoutes = formatModules(externalMoudles, [])
