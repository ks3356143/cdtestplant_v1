# 本地 HTTPS 反向代理（GB/T 28452-2012 第三级 7.1.1 鉴别信息传输加密 / 7.1.8 b)e) 用户数据传输保密性）

用部署包自带的 nginx-1.28.0 + 自签名证书，在本机 8443 端口提供 HTTPS：

```
浏览器 --TLS--> nginx:8443 --HTTP(仅本机回环)--> Django:8000
```

登录口令、token 等鉴别信息，以及用户一般/重要数据（如个人联系信息）在浏览器到服务器之间
全程 TLS 加密传输，满足 7.1.8 b) 一般数据传输保护与 e) 重要数据传输保护；
应用层不对外提供明文 HTTP 入口。

## 使用步骤

1. 构建前端并复制产物：
   ```bash
   cd web/cdTMP && npm run build:dev
   cp -r dist/* ../../packagesInitialize/nginx-1.28.0/html/dist/
   ```
2. 确认后端已启动（8000）、MySQL/Redis 已启动
3. 双击 `nginx_https_start.bat`（或命令行运行）
4. 浏览器访问 **https://localhost:8443**（自签名证书，浏览器提示不安全时选择"继续前往"）
5. 停止：`nginx_https_stop.bat`

## 文件说明

| 文件 | 说明 |
|---|---|
| localhost.crt / localhost.key | 自签名证书（SAN: localhost, 127.0.0.1，有效期 10 年，2026-10-15 生成） |
| nginx_https.conf | nginx HTTPS 配置（8443，TLSv1.2/1.3，独立 pid 不与 8181 冲突） |
| nginx_https_start.bat / _stop.bat | 启停脚本 |

## 证书信任（可选）

自签名证书浏览器会有"不安全"提示。如需消除，可将 `localhost.crt` 安装到
"受信任的根证书颁发机构"（双击 crt → 安装证书 → 本地计算机 → 受信任的根证书颁发机构），
或生产环境改用 CA 签发证书。
