import type { ArcoGlobalComponents } from "@arco-design/web-vue"

declare module "vue" {
    export interface GlobalComponents extends ArcoGlobalComponents {
        ASpace: (typeof import("@arco-design/web-vue"))["Space"]
    }
}
