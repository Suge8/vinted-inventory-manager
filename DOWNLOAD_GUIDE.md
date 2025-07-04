# 📦 下载指南

## 🚀 如何获取应用程序

### 方法1: GitHub Actions Artifacts (推荐)

1. **访问Actions页面**: https://github.com/Suge8/vinted-inventory-manager/actions
2. **点击最新的成功构建** (绿色✅标记)
3. **在页面底部找到"Artifacts"部分**
4. **下载对应的文件**:
   - **Windows用户**: 下载 `vinted-inventory-manager-windows`
   - **macOS用户**: 下载 `vinted-inventory-manager-macos`

### 方法2: 本地构建

#### macOS用户
```bash
git clone https://github.com/Suge8/vinted-inventory-manager.git
cd vinted-inventory-manager
pip install -r requirements.txt
pip install pyinstaller
python build.py
```
生成文件: `dist/VintedInventoryManager.app`

#### Windows用户
```cmd
git clone https://github.com/Suge8/vinted-inventory-manager.git
cd vinted-inventory-manager
pip install -r requirements.txt
pip install pyinstaller
python build_windows_simple.py
```
生成文件: `dist/VintedInventoryManager.exe`

## 📋 文件说明

### Windows版本
- **文件名**: `VintedInventoryManager.exe`
- **大小**: 约40-50MB
- **系统要求**: Windows 10/11 64位
- **使用方法**: 直接双击运行

### macOS版本
- **文件名**: `VintedInventoryManager-macOS.zip`
- **压缩大小**: 约45MB
- **解压后大小**: 约110MB
- **系统要求**: macOS 10.14+
- **使用方法**: 
  1. 下载zip文件
  2. 解压得到 `VintedInventoryManager.app`
  3. 双击运行

## ⚠️ 重要说明

### 文件大小差异
- **压缩包小，解压后大**: 这是正常现象
- **原因**: zip压缩对重复的库文件效果很好
- **实际占用**: 解压后的大小才是真实占用空间

### 安全提示
- **macOS**: 首次运行可能提示"无法验证开发者"
  - 解决: 右键点击应用 → 打开 → 确认打开
- **Windows**: 可能提示"Windows已保护你的电脑"
  - 解决: 点击"更多信息" → "仍要运行"

## 🔧 系统要求

### 共同要求
- **比特浏览器**: 必须安装并运行
- **网络连接**: 用于访问Vinted.nl
- **内存**: 建议4GB以上

### Windows特定
- Windows 10/11 64位系统
- .NET Framework (通常已预装)

### macOS特定
- macOS 10.14 (Mojave) 或更高版本
- 64位Intel或Apple Silicon处理器

## 🆘 故障排除

### 下载问题
- **Artifacts找不到**: 确保构建已完成且成功
- **下载失败**: 检查网络连接，尝试刷新页面

### 运行问题
- **应用无法启动**: 检查系统要求是否满足
- **比特浏览器连接失败**: 确保比特浏览器已启动
- **权限问题**: 以管理员身份运行

## 📞 技术支持

如果遇到问题，请提供以下信息：
- 操作系统版本
- 错误信息截图
- 比特浏览器版本
- 应用程序版本 (当前: v1.4.0)
