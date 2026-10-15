declare module "@arco-design/web-vue/dist/arco-vue-icon"
declare module "vue-virtual-scroller"
declare module "*.vue" {
    import { DefineComponent } from "vue"
    const component: DefineComponent<{}, {}, any>
    export default component
}
// 声明tinymce的min
declare module "tinymce/tinymce.min.js"
