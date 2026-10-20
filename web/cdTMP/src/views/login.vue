<template>
    <div class="login-page">
        <div class="login-grid-bg"></div>
        <div class="login-shell">
            <!-- 品牌区：墨黑底 + 工程网格，强调“测评工具”的工业感 -->
            <aside class="login-brand">
                <div class="brand-head">
                    <div class="brand-mark">
                        <img src="@/assets/img/wxwx-logo.svg" alt="logo" />
                    </div>
                    <span class="brand-en">TestManagePlant</span>
                </div>
                <div class="brand-body">
                    <div class="brand-kicker">TEST MANAGEMENT PLATFORM</div>
                    <h1>测试管理平台</h1>
                    <p class="brand-desc">面向软件测评全流程的项目、需求、用例与问题单管理平台。</p>
                    <ul class="brand-points">
                        <li><span class="point-index">01</span><span>项目与轮次全生命周期管理</span></li>
                        <li><span class="point-index">02</span><span>需求—用例—问题单双向追踪</span></li>
                        <li><span class="point-index">03</span><span>测评文档一键生成与归档</span></li>
                    </ul>
                </div>
                <div class="brand-foot">
                    <span>v{{ $version }}</span>
                    <span>为测评服务 · 打造测评高地</span>
                </div>
            </aside>

            <!-- 表单区 -->
            <section class="login-form-panel">
                <div class="form-inner">
                    <div class="form-head">
                        <h2>登录</h2>
                        <p>使用平台账号登录，继续您的测评工作。</p>
                    </div>
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

                        <a-form-item :hide-label="true" class="login-submit">
                            <a-button html-type="submit" type="primary" long size="large" :loading="loading"> 登录 </a-button>
                        </a-form-item>

                        <div class="login-note">
                            <icon-safe class="note-icon" />
                            <span>仅限授权用户访问，登录行为将被记录。</span>
                        </div>
                    </a-form>
                </div>
                <div class="form-foot">
                    <span>© {{ new Date().getFullYear() }} 测试管理平台</span>
                    <span>v{{ $version }}</span>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup>
import { reactive, ref } from "vue"
import loginAPI from "@/api/login"
import { useUserStore } from "@/store"
import { useRouter } from "vue-router"
import userApi from "@/api/system/user"

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

<style scoped lang="less">
.login-page {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    min-height: 100vh;
    padding: 24px;
    background-color: #eef1f3;
    overflow: hidden;
}

// 背景工程网格：细线 + 渐隐，替代粒子动画
.login-grid-bg {
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(to right, rgba(15, 23, 42, 0.055) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(15, 23, 42, 0.055) 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: radial-gradient(circle at 50% 45%, #000 20%, transparent 78%);
    pointer-events: none;
}

.login-shell {
    position: relative;
    z-index: 1;
    display: flex;
    width: 100%;
    max-width: 940px;
    min-height: 540px;
    background-color: #fff;
    border: 1px solid #d8dde3;
    box-shadow: 0 24px 60px rgba(15, 23, 42, 0.14);
}

// ---------- 左侧品牌区 ----------
.login-brand {
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 46%;
    padding: 32px;
    color: #e5e9ef;
    background-color: #0f172a;
    background-image:
        linear-gradient(to right, rgba(148, 163, 184, 0.1) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(148, 163, 184, 0.1) 1px, transparent 1px);
    background-size: 36px 36px;

    &::after {
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background-color: rgb(var(--primary-6));
        content: "";
    }
}

.brand-head {
    display: flex;
    align-items: center;
    gap: 12px;
}

.brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    background-color: rgb(var(--primary-6));

    img {
        width: 26px;
        height: 26px;
        filter: brightness(0) invert(1);
    }
}

.brand-en {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #94a3b8;
}

.brand-body {
    margin-top: 8px;
}

.brand-kicker {
    margin-bottom: 14px;
    color: rgb(var(--primary-4));
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.18em;
}

.brand-body h1 {
    margin: 0;
    color: #ffffff;
    font-size: 34px;
    font-weight: 700;
    letter-spacing: 0.02em;
    line-height: 1.2;
}

.brand-desc {
    margin: 16px 0 0;
    color: #9aa7b8;
    font-size: 13px;
    line-height: 1.8;
}

.brand-points {
    margin: 28px 0 0;
    padding: 0;
    list-style: none;

    li {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0;
        border-top: 1px solid rgba(148, 163, 184, 0.16);
        color: #cbd5e1;
        font-size: 13px;

        &:last-child {
            border-bottom: 1px solid rgba(148, 163, 184, 0.16);
        }
    }
}

.point-index {
    color: rgb(var(--primary-4));
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
}

.brand-foot {
    display: flex;
    justify-content: space-between;
    color: #64748b;
    font-size: 11px;
    letter-spacing: 0.04em;
}

// ---------- 右侧表单区 ----------
.login-form-panel {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 54%;
    padding: 44px 48px 24px;
    background-color: #ffffff;
}

.form-inner {
    display: flex;
    flex: 1;
    flex-direction: column;
    justify-content: center;
}

.form-head {
    margin-bottom: 28px;

    h2 {
        margin: 0;
        color: #111827;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    p {
        margin: 8px 0 0;
        color: #6b7280;
        font-size: 13px;
    }
}

.login-submit {
    margin-top: 24px;
    margin-bottom: 16px;
}

.login-note {
    display: flex;
    align-items: center;
    gap: 6px;
    color: #8a93a0;
    font-size: 12px;
    line-height: 1.5;
}

.note-icon {
    color: rgb(var(--primary-6));
    font-size: 14px;
}

.form-foot {
    display: flex;
    justify-content: space-between;
    margin-top: 32px;
    padding-top: 14px;
    border-top: 1px solid #eceff2;
    color: #9aa3af;
    font-size: 11px;
}

:deep(.arco-form-item) {
    margin-bottom: 18px;
}

:deep(.arco-input-wrapper) {
    height: 44px;
    background-color: #fbfcfd;
}

:deep(.arco-input-wrapper:hover) {
    background-color: #ffffff;
}

:deep(.arco-input-wrapper.arco-input-focus) {
    background-color: #ffffff;
}

:deep(.arco-input-append) {
    padding: 0 !important;
    background-color: transparent;
}

.captcha-img {
    height: 42px;
    display: block;
    cursor: pointer;
    border-left: 1px solid #e4e7eb;
}

:deep(.arco-btn-size-large) {
    height: 44px;
    font-size: 15px;
    letter-spacing: 0.08em;
}

@media (max-width: 820px) {
    .login-page {
        padding: 16px;
    }

    .login-shell {
        min-height: auto;
        max-width: 460px;
    }

    .login-brand {
        display: none;
    }

    .login-form-panel {
        width: 100%;
        padding: 32px 24px 20px;
    }
}
</style>
