import { defineConfig, loadEnv } from "vite"
import vue from "@vitejs/plugin-vue"
import { resolve } from "path"
import vueJsx from "@vitejs/plugin-vue-jsx"
import { visualizer } from "rollup-plugin-visualizer"
import tailwindcss from "@tailwindcss/vite"

export default ({ mode }) => {
    const env = loadEnv(mode, process.cwd())
    const proxyPrefix = env.VITE_APP_PROXY_PREFIX
    return defineConfig({
        base: env.VITE_APP_BASE,
        plugins: [
            vue(),
            vueJsx(),
            // 产物分析图输出到 dist/visualizer.html，需要时自行打开（不自动弹浏览器，
            // 否则每次构建都会抢占前台）
            visualizer({
                open: false,
                filename: "./dist/visualizer.html"
            }),
            tailwindcss()
        ],
        resolve: {
            alias: {
                "@": resolve(import.meta.dirname, "src"),
                "@cps": resolve(import.meta.dirname, "src/components"),
                "vue-i18n": "vue-i18n/dist/vue-i18n.cjs.js",
                vue: "vue/dist/vue.esm-bundler.js"
            }
        },
        define: {
            __VUE_PROD_DEVTOOLS__: false,
            __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: false
        },
        build: {
            chunkSizeWarningLimit: 3000,
            rolldownOptions: {
                output: {
                    codeSplitting: {
                        groups: [
                            {
                                name: "arco-design",
                                test: /[\\/]node_modules[\\/]@arco-design[\\/]web-vue[\\/]/
                            }
                        ]
                    }
                }
            }
        },
        server: {
            host: "0.0.0.0",
            port: env.VITE_APP_PORT || process.env.port,
            proxy: {
                [proxyPrefix]: {
                    target: env.VITE_APP_BASE_URL,
                    changeOrigin: true,
                    ws: true,
                    toProxy: true,
                    rewrite: (path) => path.replace(new RegExp(`^${proxyPrefix}`), "")
                }
            }
        }
    })
}
