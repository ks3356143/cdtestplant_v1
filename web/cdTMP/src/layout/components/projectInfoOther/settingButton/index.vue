<template>
    <button class="button">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" viewBox="0 0 20 20" height="20" fill="none" class="svg-icon">
            <g stroke-width="1.5" stroke-linecap="round" stroke="currentColor">
                <circle r="2.5" cy="10" cx="10"></circle>
                <path
                    fill-rule="evenodd"
                    d="m8.39079 2.80235c.53842-1.51424 2.67991-1.51424 3.21831-.00001.3392.95358 1.4284 1.40477 2.3425.97027 1.4514-.68995 2.9657.82427 2.2758 2.27575-.4345.91407.0166 2.00334.9702 2.34248 1.5143.53842 1.5143 2.67996 0 3.21836-.9536.3391-1.4047 1.4284-.9702 2.3425.6899 1.4514-.8244 2.9656-2.2758 2.2757-.9141-.4345-2.0033.0167-2.3425.9703-.5384 1.5142-2.67989 1.5142-3.21831 0-.33914-.9536-1.4284-1.4048-2.34247-.9703-1.45148.6899-2.96571-.8243-2.27575-2.2757.43449-.9141-.01669-2.0034-.97028-2.3425-1.51422-.5384-1.51422-2.67994.00001-3.21836.95358-.33914 1.40476-1.42841.97027-2.34248-.68996-1.45148.82427-2.9657 2.27575-2.27575.91407.4345 2.00333-.01669 2.34247-.97026z"
                    clip-rule="evenodd"
                ></path>
            </g>
        </svg>
        <span class="lable">{{ label }}</span>
        <slot></slot>
    </button>
</template>

<script setup lang="ts">
const { label } = defineProps<{
    label: string
}>()

defineOptions({
    name: "SettingButton"
})
</script>

<style scoped>
/* 直角风格：深墨底 + 青绿描边，和顶栏/侧边栏保持同一套视觉语言 */
.button {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 0 14px;
    gap: 8px;
    height: 34px;
    min-width: 148px;
    border: 1px solid #263145;
    background: #0f172a;
    border-radius: 0;
    color: #c7d0dd;
    cursor: pointer;
    transition:
        background-color 0.15s ease,
        border-color 0.15s ease,
        color 0.15s ease;
}

.lable {
    line-height: 1.2;
    font-size: 14px;
    color: inherit;
    font-family: inherit;
    letter-spacing: 0.06em;
}

.svg-icon {
    display: block;
    width: 17px;
    height: 17px;
    color: rgb(var(--primary-4));
}

.button:hover {
    background: rgb(var(--primary-6));
    border-color: rgb(var(--primary-6));
    color: #ffffff;
}

.button:hover .svg-icon {
    color: #ffffff;
}

@media (max-width: 1280px) {
    .button {
        min-width: 130px;
        height: 32px;
        padding: 0 10px;
        gap: 6px;
    }

    .lable {
        font-size: 13px;
    }

    .svg-icon {
        width: 16px;
        height: 16px;
    }
}

@media (max-width: 1024px) {
    .button {
        min-width: 118px;
        height: 30px;
        padding: 0 8px;
        gap: 5px;
    }

    .lable {
        font-size: 12px;
        letter-spacing: 0.04em;
    }

    .svg-icon {
        width: 15px;
        height: 15px;
    }
}
</style>
