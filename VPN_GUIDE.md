# VPN/代理配置指南

## 🔧 常见连接问题解决方案

### 问题1: 503错误频繁出现

**症状**: BitBrowser API连接测试时频繁出现503错误，需要多次尝试才能成功

**原因分析**:
- VPN软件的系统代理模式干扰了本地API连接
- 代理服务器不稳定或负载过高
- 防火墙或安全软件拦截连接

**解决方案**:

#### 方案1: VPN TUN模式配置 (推荐)
1. **ExpressVPN**:
   - 打开ExpressVPN客户端
   - 进入设置 → 高级 → 协议
   - 选择"Lightway - UDP"协议
   - 启用"Split Tunneling"功能
   - 在排除列表中添加BitBrowser应用

2. **NordVPN**:
   - 打开NordVPN客户端
   - 进入设置 → 高级
   - 选择"NordLynx"协议
   - 启用"Split Tunneling"
   - 排除BitBrowser和本地应用

3. **Surfshark**:
   - 打开Surfshark客户端
   - 进入设置 → 高级
   - 启用"Bypasser"功能
   - 添加BitBrowser到排除列表

#### 方案2: 系统代理排除
如果无法使用TUN模式，可以配置系统代理排除：

**Windows**:
```
1. 打开"设置" → "网络和Internet" → "代理"
2. 在"手动代理设置"中点击"高级"
3. 在"例外"中添加: 127.0.0.1;localhost;*.local
```

**macOS**:
```
1. 打开"系统偏好设置" → "网络"
2. 选择当前网络 → "高级" → "代理"
3. 在"忽略这些主机与域的代理设置"中添加: 127.0.0.1,localhost,*.local
```

### 问题2: 连接超时或不稳定

**解决步骤**:

1. **检查VPN服务器状态**:
   - 选择延迟较低的服务器（<100ms）
   - 避免使用负载过高的服务器
   - 尝试不同地区的服务器

2. **优化VPN协议**:
   - OpenVPN → WireGuard/NordLynx
   - IKEv2 → Lightway
   - 启用快速连接功能

3. **网络环境测试**:
   ```bash
   # 测试本地API连接
   curl -X POST http://127.0.0.1:54345/browser/list \
        -H "Content-Type: application/json" \
        -d '{"page":0,"pageSize":10}'
   ```

### 问题3: 双VPN环境配置

对于需要额外安全性的用户：

**配置方案**:
1. **路由器级VPN**: 配置路由器连接VPN服务器
2. **软件级VPN**: 在设备上运行第二个VPN客户端
3. **应用排除**: 确保BitBrowser通过本地网络访问

**推荐组合**:
- 路由器: ExpressVPN (Lightway)
- 软件: NordVPN (Split Tunneling开启)
- 排除: 127.0.0.1, localhost, BitBrowser

## 🛠️ 故障排除步骤

### 步骤1: 基础检查
```bash
# 检查BitBrowser进程
ps aux | grep -i bitbrowser

# 检查端口占用
netstat -an | grep 54345

# 测试本地连接
telnet 127.0.0.1 54345
```

### 步骤2: 代理环境检查
```bash
# 检查环境变量
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 临时清除代理
unset HTTP_PROXY HTTPS_PROXY
```

### 步骤3: 防火墙检查
**Windows**:
- 打开Windows Defender防火墙
- 检查是否阻止了BitBrowser或端口54345
- 添加例外规则

**macOS**:
- 系统偏好设置 → 安全性与隐私 → 防火墙
- 确保BitBrowser被允许接收连接

### 步骤4: 应急解决方案

1. **临时关闭VPN测试**:
   - 断开VPN连接
   - 测试BitBrowser API连接
   - 确认是否为VPN问题

2. **使用移动热点**:
   - 连接手机热点
   - 测试网络环境
   - 排除网络环境问题

3. **重启服务**:
   ```bash
   # 重启BitBrowser服务
   # 重启VPN客户端
   # 清除DNS缓存
   ```

## 📞 技术支持

如果以上方案都无法解决问题，请联系：

1. **VPN服务商客服**: 获取专用配置文件
2. **BitBrowser技术支持**: 报告API连接问题
3. **应用开发者**: 提供详细错误日志

## ⚠️ 注意事项

- 避免使用免费VPN，稳定性差且可能有安全风险
- 定期更新VPN客户端到最新版本
- 保持BitBrowser和系统更新到最新版本
- 不要同时运行多个VPN客户端
- 定期清理DNS缓存和网络配置
