<template>
    <div class="page max-7xl mx-auto text-center">
        <div class="bg mx-auto">
            <img src="@/assets/404.svg" />
            <div class="mt-2">页面未找到，请返回</div>
        </div>
        <div class="mt-5">
            <a-button type="primary" @click="$router.push({ name: 'workplace' })">返回第一个有权限页面</a-button>
        </div>
    </div>
</template>

<style scoped lang="less">
.page {
    position: absolute;
    top: 50%;
    left: 50%;
    margin-top: -200px;
    margin-left: -195px;
}
.bg,
.bg img {
    width: 390px;
}
</style>
