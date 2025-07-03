# Windows .exe 构建指南

由于你在macOS上无法直接构建Windows .exe文件，这里提供几种解决方案：

## 🔥 方案1: 使用GitHub Codespaces (推荐)

1. **创建GitHub仓库**
   ```bash
   # 在项目目录中
   git init
   git add .
   git commit -m "Initial commit"
   # 推送到GitHub仓库
   ```

2. **使用Codespaces**
   - 在GitHub仓库页面点击"Code" > "Codespaces" > "Create codespace"
   - 等待环境启动完成

3. **在Codespaces中构建**
   ```bash
   # 安装依赖
   pip install -r requirements.txt
   pip install pyinstaller
   
   # 构建Windows版本
   python build_windows.py
   
   # 下载生成的文件
   # 在Codespaces中右键点击 dist/VintedInventoryManager.exe 选择下载
   ```

## 💻 方案2: 使用Replit

1. **访问 replit.com**
2. **创建新的Python项目**
3. **上传项目文件**
4. **运行构建命令**
   ```bash
   pip install pyinstaller
   python build_windows.py
   ```

## ☁️ 方案3: 使用在线Windows环境

### 选项A: Windows 365 Cloud PC
- 微软官方云Windows服务
- 按需付费使用

### 选项B: AWS Windows实例
- 创建Windows EC2实例
- 远程桌面连接
- 构建完成后下载文件

## 🖥️ 方案4: 本地虚拟机

### 使用Parallels Desktop (macOS)
1. **安装Parallels Desktop**
2. **创建Windows 11虚拟机**
3. **在虚拟机中安装Python**
4. **复制项目文件到虚拟机**
5. **运行构建脚本**

### 使用VMware Fusion
- 类似Parallels的步骤

## 🚀 方案5: 自动化构建 (最佳长期解决方案)

### GitHub Actions配置
项目已包含 `.github/workflows/build.yml` 文件，可以：

1. **推送到GitHub**
2. **创建Release标签**
   ```bash
   git tag v1.4.0
   git push origin v1.4.0
   ```
3. **自动构建两个平台版本**

## 📋 当前状态

✅ **macOS版本已完成**
- 文件位置: `dist/VintedInventoryManager.app`
- 可直接发给macOS用户使用

⏳ **Windows版本待构建**
- 需要使用上述任一方案
- 推荐使用GitHub Codespaces（免费且简单）

## 🔧 快速构建步骤 (GitHub Codespaces)

1. **创建GitHub仓库并推送代码**
2. **打开Codespaces**
3. **运行以下命令**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   python build_windows.py
   ```
4. **下载生成的 VintedInventoryManager.exe**

## 💡 提示

- GitHub Codespaces每月有免费额度
- 构建过程大约需要2-3分钟
- 生成的.exe文件可在任何Windows 10/11系统上运行
- 无需在目标Windows电脑上安装Python或其他依赖
