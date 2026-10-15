/**
 * @description: js工具类
 */

/**
 * 该函数传入一个对象，判断其是否为空
 * @param {object} 对象
 * @returns {boolean} 是否为空
 */
export function isBlankObj(data: object): boolean {
    return Object.keys(data).length > 0
}
