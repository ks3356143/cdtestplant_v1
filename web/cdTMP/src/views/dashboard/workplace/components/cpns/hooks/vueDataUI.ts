import { Ref, computed } from "vue"
import { storeToRefs } from "pinia"
import { useAppStore } from "@/store"

interface IData {
    mouth: string
    count: number
}
interface ResData {
    data: IData[]
}

function useVueDataUI(data: Ref<ResData>) {
    const appStore = useAppStore()
    const { theme } = storeToRefs(appStore)

    // 基础数据集
    const initialData = [
        {
            name: "项目数量",
            series: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            type: "line",
            color: "rgb(95,139,238)",
            scaleSteps: 10,
            suffix: "个",
            smooth: true
        }
    ]

    const chartData = computed(() => {
        if (data.value) {
            const countData = data.value.data.map((it) => it.count)
            // 注意：这里直接修改了 initialData[0].series，为避免副作用，建议每次返回新对象
            return [
                {
                    ...initialData[0],
                    series: countData
                }
            ]
        }
        return initialData
    })

    // 基础配置（不包含颜色相关部分）
    const baseConfig = {
        responsive: false,
        customPalette: [],
        downsample: { threshold: 500 },
        chart: {
            fontFamily: "inherit",
            height: 300,
            width: 1200,
            padding: { top: 36, right: 24, bottom: 48, left: 48 },
            highlighter: { opacity: 5, useLine: false, lineDasharray: 2, lineWidth: 1 },
            grid: {
                showVerticalLines: false,
                showHorizontalLines: false,
                position: "middle",
                frame: {
                    show: false,
                    strokeWidth: 2,
                    strokeLinecap: "round",
                    strokeLinejoin: "round",
                    strokeDasharray: 0
                },
                labels: {
                    show: true,
                    fontSize: 12,
                    axis: { yLabel: "", yLabelOffsetX: 0, xLabel: "", xLabelOffsetY: 14, fontSize: 12 },
                    zeroLine: { show: true },
                    xAxis: { showBaseline: true },
                    yAxis: {
                        showBaseline: true,
                        commonScaleSteps: 1,
                        useIndividualScale: false,
                        stacked: false,
                        gap: 12,
                        labelWidth: 40,
                        formatter: null,
                        scaleMin: 0,
                        scaleMax: 20
                    },
                    xAxisLabels: {
                        show: true,
                        values: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"],
                        fontSize: 12,
                        showOnlyFirstAndLast: false,
                        showOnlyAtModulo: false,
                        modulo: 12,
                        yOffset: 8,
                        rotation: 0
                    }
                }
            },
            comments: { show: true, showInTooltip: true, width: 200, offsetX: 0, offsetY: 0 },
            labels: { fontSize: 10, prefix: "", suffix: "" },
            legend: { show: false, fontSize: 16 },
            title: {
                text: "项目每月统计",
                fontSize: 18,
                bold: true,
                textAlign: "left",
                paddingLeft: 5,
                paddingRight: 0,
                subtitle: { text: "", fontSize: 16, bold: false },
                show: true
            },
            tooltip: {
                show: true,
                fontSize: 14,
                customFormat: null,
                borderRadius: 4,
                borderWidth: 1,
                backgroundOpacity: 30,
                position: "center",
                offsetY: 24,
                showValue: true,
                showPercentage: false,
                roundingValue: 0,
                roundingPercentage: 0
            },
            userOptions: {
                show: true,
                position: "right",
                buttons: {
                    tooltip: true,
                    pdf: true,
                    csv: true,
                    img: true,
                    table: false,
                    labels: false,
                    fullscreen: true,
                    sort: false,
                    stack: true,
                    animation: false,
                    annotator: false
                },
                buttonTitles: {
                    open: "打开选项",
                    close: "关闭选项",
                    tooltip: "切换提示开关",
                    pdf: "下载为PDF",
                    csv: "下载为CSV",
                    img: "下载为PNG",
                    table: "表格显示/隐藏",
                    labels: "标签显示/隐藏",
                    fullscreen: "切换全屏",
                    stack: "切换stack模式"
                }
            },
            zoom: { show: false }
        },
        showTable: false
    }

    const chartConfig = computed(() => {
        const isDark = theme.value === "dark"

        // 计算 Y 轴最大值
        let scaleMax = 10
        if (data.value) {
            const countData = data.value.data.map((it) => it.count)
            scaleMax = Math.max(...countData) || 10
        }

        // 动态生成颜色相关配置
        return {
            ...baseConfig,
            // 不设置 theme，完全自定义
            chart: {
                ...baseConfig.chart,
                // 背景色
                backgroundColor: isDark ? "#1A1A1Aff" : "#FFFFFFff",
                // 全局文字颜色
                color: isDark ? "#FFFFFFFF" : "#1A1A1Aff",
                highlighter: {
                    ...baseConfig.chart.highlighter,
                    color: isDark ? "#FFFFFFFF" : "#1A1A1Aff"
                },
                grid: {
                    ...baseConfig.chart.grid,
                    stroke: isDark ? "#444444ff" : "#e1e5e8ff",
                    frame: {
                        ...baseConfig.chart.grid.frame,
                        stroke: isDark ? "#444444ff" : "#E1E5E8ff"
                    },
                    labels: {
                        ...baseConfig.chart.grid.labels,
                        color: isDark ? "#FFFFFFFF" : "#1A1A1Aff",
                        yAxis: {
                            ...baseConfig.chart.grid.labels.yAxis,
                            scaleMax
                        },
                        xAxisLabels: {
                            ...baseConfig.chart.grid.labels.xAxisLabels,
                            color: isDark ? "#FFFFFFFF" : "#1A1A1Aff"
                        }
                    }
                },
                legend: {
                    ...baseConfig.chart.legend,
                    color: isDark ? "#FFFFFFFF" : "#1A1A1Aff"
                },
                title: {
                    ...baseConfig.chart.title,
                    color: isDark ? "#FFFFFFFF" : "#1A1A1Aff",
                    subtitle: {
                        ...baseConfig.chart.title.subtitle,
                        color: isDark ? "#AAAAAAff" : "#CCCCCCff"
                    }
                },
                tooltip: {
                    ...baseConfig.chart.tooltip,
                    color: isDark ? "#FFFFFFFF" : "#1A1A1Aff",
                    backgroundColor: isDark ? "#333333ff" : "#FFFFFFff",
                    borderColor: isDark ? "#555555ff" : "#e1e5e8"
                }
            }
        }
    })

    return { chartData, chartConfig }
}

export default useVueDataUI
