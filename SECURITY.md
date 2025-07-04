# 安全说明 / Security Information

## 关于杀毒软件误报 / About Antivirus False Positives

### 为什么会被误报为病毒？/ Why is it flagged as a virus?

本软件使用PyInstaller打包，包含以下功能可能触发杀毒软件警报：
This software is packaged with PyInstaller and contains features that may trigger antivirus alerts:

1. **浏览器自动化** / Browser Automation
   - 使用Selenium WebDriver控制浏览器
   - Uses Selenium WebDriver to control browsers

2. **网络请求** / Network Requests  
   - 与BitBrowser API通信
   - Communicates with BitBrowser API

3. **文件操作** / File Operations
   - 生成报告文件和日志
   - Generates report files and logs

### 安全保证 / Security Guarantee

✅ **开源代码** / Open Source Code
- 所有源代码公开在GitHub: https://github.com/Suge8/vinted-inventory-manager
- All source code is public on GitHub

✅ **无恶意行为** / No Malicious Behavior
- 不收集个人信息
- Does not collect personal information
- 不连接可疑服务器
- Does not connect to suspicious servers
- 不修改系统文件
- Does not modify system files

✅ **功能透明** / Transparent Functionality
- 仅用于Vinted库存监控
- Only used for Vinted inventory monitoring
- 所有网络请求都是合法的API调用
- All network requests are legitimate API calls

### 如何安全使用 / How to Use Safely

1. **下载来源** / Download Source
   - 仅从官方GitHub Releases下载
   - Only download from official GitHub Releases
   - 链接: https://github.com/Suge8/vinted-inventory-manager/releases

2. **杀毒软件设置** / Antivirus Settings
   - 将文件添加到信任列表
   - Add file to trusted list
   - 或临时关闭实时保护进行安装
   - Or temporarily disable real-time protection for installation

3. **验证文件** / Verify File
   - 检查文件大小是否合理（约30-40MB）
   - Check if file size is reasonable (about 30-40MB)
   - 确认下载来源是官方仓库
   - Confirm download source is official repository

### 联系我们 / Contact Us

如果您对安全性有任何疑问，请：
If you have any security concerns, please:

- 查看完整源代码
- Review the complete source code
- 在GitHub提交Issue
- Submit an Issue on GitHub
- 联系开发者进行验证
- Contact developers for verification

**我们承诺本软件100%安全，无任何恶意代码！**
**We guarantee this software is 100% safe with no malicious code!**
