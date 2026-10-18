import { isString, isFunction } from "lodash-es"
export const maEvent = {
    handleCommonEvent: (component, evName) => {
        if (component[evName]) {
            if (isFunction(component[evName])) {
                return component[evName]()
            }
            if (isString(component[evName])) {
                let customFn = new Function("value", component[evName])
                return customFn.call(component[evName])
            }
        }
    }
}
