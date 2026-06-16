# 升级到永久 URL（5–10 分钟）

当前是 Cloudflare **Quick Tunnel**（临时随机 URL，PC 重启会变）。
本文档帮你升级成**永久 URL**，手机书签一次保终生。

---

## 路线 A · Cloudflare Named Tunnel（推荐 · 需自有域名）

**前提**：需要一个已托管在 Cloudflare 的域名。
- 没域名：Cloudflare 自营注册 `.com` 约 ¥1,500/年，最便宜 `.xyz` 约 ¥150/年
- 有域名（Google Domains/お名前.com 等）：免费转入 Cloudflare 或仅修改 NS 即可

### 步骤（PowerShell）

```powershell
$cf = 'C:\Users\satan\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe'

# 1. 登录（会弹浏览器，授权你的域名）
& $cf tunnel login

# 2. 创建命名隧道
& $cf tunnel create ai-radar

# 3. 绑定子域名（替换 example.com 为你的域名）
& $cf tunnel route dns ai-radar radar.example.com

# 4. 写配置文件
$config = @"
tunnel: ai-radar
credentials-file: $env:USERPROFILE\.cloudflared\<tunnel-id>.json
ingress:
  - hostname: radar.example.com
    service: http://localhost:8765
  - service: http_status:404
"@
$config | Out-File -Encoding utf8 "$env:USERPROFILE\.cloudflared\config.yml"

# 5. 装成系统服务（永久自动启动）
& $cf service install
```

### 替换 Quick Tunnel 的 Startup 项

把 `C:\Users\satan\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\AI-Radar-Tunnel.vbs` **删除**（因为 step 5 装的系统服务会自动跑）。

---

## 路线 B · Tailscale Funnel（免费 · 无需域名）

**优点**：完全免费、不用域名、PC 装好就行。
**缺点**：URL 是 `https://hostname.tailXXXX.ts.net` 这种长串，不太好记。

### 步骤

1. 下载 Tailscale Windows 客户端：https://tailscale.com/download
2. 安装并用 Google 账号登录（你已经有 Gmail）
3. PowerShell：
   ```powershell
   tailscale funnel --bg 8765
   ```
4. 它会打印类似 `https://yourpc.tailXXXX.ts.net` 的 URL，**永久有效**
5. 删除 Quick Tunnel 的 Startup 项（同上）

---

## 选哪个？

| 维度 | Cloudflare Named | Tailscale Funnel |
|---|---|---|
| 永久 URL | ✅ | ✅ |
| 自定义域名 | ✅ radar.你的域名 | ❌ 系统生成 |
| 费用 | 域名约 ¥150–1500/年 | 完全免费 |
| 配置复杂度 | 5 步 | 3 步 |
| 适合 | 想长期用 + 想要漂亮 URL | 想最快搞定 |

---

## 当前 Quick Tunnel 设定（已就绪）

- 通道脚本：`start_tunnel.ps1`
- Startup 项：`AI-Radar-Tunnel.vbs`
- 当前 URL 文件：`data\tunnel_url.txt`（重启后自动更新）
- 历史日志：`data\tunnel_url.history.log`

打开 http://192.168.2.173:8765/ 时顶部会显示当前 URL，方便随时复制更新手机书签。
