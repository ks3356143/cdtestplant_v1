<template>
    <div id="background" class="fixed"></div>
    <div class="bg-backdrop-layout">
        <ParticlesBg class="h-full" :quantity="200" :ease="100" :color="'#000'" :staticity="10" refresh></ParticlesBg>
    </div>
    <div class="login-container">
        <div class="login-width md:w-10/12 mx-auto flex justify-between h-full items-center">
            <div class="w-6/12 mx-auto left-panel rounded-l pl-5 pr-5 hidden md:block">
                <div class="logo">
                    <img src="@/assets/img/wxwx-logo.svg" width="45" /><span>{{ $title }}</span>
                </div>
                <div class="slogan flex justify-end">
                    <span class="font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-500 to-purple-600">---- 为测评服务，打造测评高地</span>
                </div>
            </div>

            <div class="md:w-6/12 w-11/12 md:rounded-r mx-auto pl-5 pr-5 pb-10">
                <h2 class="mt-10 text-3xl pb-0 mb-10">登录</h2>
                <a-form :model="form" @submit="handleSubmit">
                    <a-form-item
                        field="username"
                        :hide-label="true"
                        :rules="[
                            { required: true, message: '用户名不能为空' },
                            { maxLength: 30, message: '用户名不能超过30个字符' }
                        ]"
                    >
                        <a-input v-model="form.username" class="w-full" size="large" placeholder="用户名" allow-clear :max-length="30">
                            <template #prefix><icon-user /></template>
                        </a-input>
                    </a-form-item>

                    <a-form-item
                        field="password"
                        :hide-label="true"
                        :rules="[
                            { required: true, message: '密码不能为空' },
                            { maxLength: 30, message: '密码不超过30字符' }
                        ]"
                    >
                        <a-input-password v-model="form.password" placeholder="请输入密码" size="large" allow-clear :max-length="30">
                            <template #prefix><icon-lock /></template>
                        </a-input-password>
                    </a-form-item>

                    <!-- 图形验证码：仅特权账号（管理员/安全员/审计员）登录时按需出现 -->
                    <a-form-item
                        v-if="needCaptcha"
                        field="code"
                        :hide-label="true"
                        :rules="[
                            {
                                required: true,
                                match: /^[a-zA-Z0-9]{4}$/,
                                message: '验证码不符合要求'
                            }
                        ]"
                    >
                        <a-input v-model="form.code" placeholder="请输入验证码" size="large" allow-clear :max-length="4">
                            <template #prefix><icon-safe /></template>
                            <template #append>
                                <img v-if="captchaImage" :src="captchaImage" class="captcha-img" title="看不清？点击刷新" @click="refreshCaptcha" />
                            </template>
                        </a-input>
                    </a-form-item>

                    <a-form-item :hide-label="true" class="mt-5">
                        <a-button html-type="submit" type="primary" long size="large" :loading="loading"> 登录 </a-button>
                    </a-form-item>

                    <a-divider orientation="center">未来登录方式</a-divider>
                    <div class="flex w-3/4 pt-2 mx-auto items-stretch justify-around">
                        <a-avatar class="other-login wechat"><icon-wechat /></a-avatar>
                        <a-avatar class="other-login alipay"><icon-alipay-circle /></a-avatar>
                        <a-avatar class="other-login qq"><icon-qq /></a-avatar>
                        <a-avatar class="other-login weibo"><icon-weibo /></a-avatar>
                    </div>
                </a-form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import loginAPI from "@/api/login"
import { useUserStore } from "@/store"
import { useRouter } from "vue-router"
import userApi from "@/api/system/user"
// 导入背景ui组件
import ParticlesBg from "@/components/ui/particles-bg/ParticlesBg.vue"
const router = useRouter()
const userStore = useUserStore()
// 绑定登录form的数据
const form = reactive({ username: "", password: "", code: "", captcha_key: "" })
// 后端图形验证码（三权分立：特权角色登录双因子）
// needCaptcha 默认 false：普通用户看不到验证码框；特权账号登录时由后端业务码触发显示，
// 因此登录页不需要任何"查该账号是否特权"的探测接口，特权账号名单不可被枚举
const needCaptcha = ref(false)
const captchaImage = ref("")
const refreshCaptcha = async () => {
    try {
        const res = await loginAPI.getCaptch()
        captchaImage.value = res.data.image
        form.captcha_key = res.data.captcha_key
        form.code = ""
    } catch (e) {
        captchaImage.value = ""
    }
}
// arco表单loading
const loading = ref(null)
// 点击登录按钮
const handleSubmit = async ({ values, errors }) => {
    if (loading.value) {
        return
    }
    loading.value = true
    if (errors) {
        loading.value = false
        return
    }
    // 登录逻辑需要用到userStore
    try {
        const login_res = await userStore.login(form)
        if (login_res && login_res.ok) {
            const { redirect, ...otherQuery } = router.currentRoute.value.query
            router.push({
                name: redirect || "workplace",
                query: {
                    ...otherQuery // 将退出时的查询参数放入，这样就不会错误
                }
            })
            // 加载LDAP数据：仅系统管理员有同步权限，内网不可用时静默忽略
            try {
                await userStore.info()
                if (userStore.role === "admin") {
                    await userApi.loadLDAPUsers()
                }
            } catch {
                // 非内网环境或非管理员：不影响正常登录
            }
            return
        }
        // 特权账号首次登录：后端要求图形验证码，此时才显示输入框并拉取图片
        if (login_res && login_res.needCaptcha) {
            needCaptcha.value = true
            await refreshCaptcha()
        } else if (needCaptcha.value) {
            // 验证码一次性使用，已显示时失败需刷新
            refreshCaptcha()
        }
    } catch {
        // 登录失败原因由接口层统一提示
    } finally {
        loading.value = false
    }
}
</script>

<style lang="less" scoped>
#background {
    top: 0;
    left: 0;
    z-index: 1;
    width: 100%;
    height: 100%;
    background-size: cover;
}
.bg-backdrop-layout {
    top: 0;
    left: 0;
    position: fixed;
    width: 100%;
    height: 100%;
    z-index: 2;
    backdrop-filter: blur(0.01px); // 给背景图模糊
}
.login-container {
    width: 100%;
    height: 100%;
    position: absolute;
    background-size: cover;
    z-index: 3;
    .login-width {
        max-width: 950px;
        padding: 10px;
        height: 500px;
        position: relative;
        top: 50%;
        margin-top: -255px;
        border-radius: var(--border-radius-small);
        box-shadow:
            rgba(0, 0, 0, 0.25) 0px 14px 28px,
            rgba(0, 0, 0, 0.22) 0px 10px 10px;
        backdrop-filter: blur(3px);
    }

    .left-panel {
        height: 491px;
        background-image: url(@/assets/login_picture.svg);
        background-repeat: no-repeat;
        background-position: center 140px;
        background-size: contain;
    }

    .logo {
        display: flex;
        align-items: center;
        margin-top: 20px;
        color: #333;
        perspective: 100px;
        span {
            font-size: 28px;
            margin-left: 15px;
            color: rgb(var(--primary-6));
        }
    }
    .slogan {
        font-size: 16px;
        line-height: 50px;
    }

    :deep(.arco-input-append) {
        padding: 0 !important;
    }

    .captcha-img {
        height: 36px;
        display: block;
        cursor: pointer;
    }

    .other-login {
        cursor: pointer;
    }

    .qq:hover,
    .alipay:hover {
        background: #165dff;
    }
    .wechat:hover {
        background: #0f9c02;
    }

    .weibo:hover {
        background: #f3ce2b;
    }
}

:deep(.arco-form-item) {
    margin-bottom: 20px; /* 覆盖默认样式 */
}
</style>
