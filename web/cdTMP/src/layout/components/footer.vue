<template>
    <a-layout-footer class="footer">
        <span class="footer-brand">测试管理平台</span>
        <span class="footer-divider"></span>
        <span class="footer-meta">v{{ $version }}</span>
        <span class="footer-divider"></span>
        <span class="footer-meta">为测评服务 · 打造测评高地</span>
    </a-layout-footer>
</template>

<script setup></script>

<style lang="less" scoped>
.footer {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    height: 36px;
    padding: 0 16px;
    border-top: 1px solid var(--app-line, #e4e7eb);
    background-color: var(--app-surface, #fff);
    color: var(--app-muted, #6b7280);
    font-size: 12px;
}

.footer-brand {
    color: var(--app-ink-2, #374151);
    font-weight: 600;
}

.footer-divider {
    width: 1px;
    height: 12px;
    background-color: var(--app-line, #e4e7eb);
}

.footer-meta {
    color: var(--app-muted, #6b7280);
}
</style>
