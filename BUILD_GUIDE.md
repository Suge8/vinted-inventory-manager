# 跨平台构建指南

本文档说明如何为macOS和Windows两个平台构建Vinted.nl库存宝的可执行文件。

## 🎯 构建目标

- **macOS**: `VintedInventoryManager.app` (应用包)
- **Windows**: `VintedInventoryManager.exe` (可执行文件)

## 🔧 构建方法

### 方法一：本地构建（推荐）

#### 在macOS上构建macOS版本

```bash
# 1. 确保环境
python --version  # 需要Python 3.8+

# 2. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 3. 构建
python build.py

# 4. 输出文件
# - dist/VintedInventoryManager (命令行版本)
# - dist/VintedInventoryManager.app (应用包，推荐)
```

#### 在Windows上构建Windows版本

```cmd
# 1. 确保环境
python --version  # 需要Python 3.8+

# 2. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 3. 构建（使用Windows专用脚本）
python build_windows.py

# 4. 输出文件
# - dist/VintedInventoryManager.exe
```

### 方法二：GitHub Actions自动构建

1. **推送标签触发构建**
   ```bash
   git tag v1.3.2
   git push origin v1.3.2
   ```

2. **手动触发构建**
   - 访问GitHub仓库的Actions页面
   - 选择"Build Cross-Platform Executables"
   - 点击"Run workflow"

3. **下载构建结果**
   - 在Actions页面下载artifacts
   - 或在Releases页面下载发布版本

## 📋 构建脚本说明

### build.py (通用构建脚本)
- 适用于macOS和Linux
- 自动检测操作系统
- 生成对应平台的可执行文件

### build_windows.py (Windows专用)
- 专门为Windows优化
- 包含Windows特定的PyInstaller参数
- 更好的错误处理和验证

## 🔍 构建验证

### macOS版本验证
```bash
# 测试命令行版本
./dist/VintedInventoryManager

# 测试应用包
open dist/VintedInventoryManager.app
```

### Windows版本验证
```cmd
# 测试可执行文件
dist\VintedInventoryManager.exe
```

## ⚠️ 注意事项

### PyInstaller限制
- **无法跨平台构建**: 在macOS上无法构建Windows .exe文件
- **需要对应系统**: 每个平台都需要在对应系统上构建
- **依赖系统库**: 生成的文件依赖于构建时的系统环境

### 构建环境要求
- **Python版本**: 3.8+ (推荐3.9)
- **PyInstaller**: 最新版本
- **系统要求**: 
  - macOS: 10.14+
  - Windows: 10/11 64位

### 文件大小
- **macOS应用包**: ~50-80MB
- **Windows可执行文件**: ~30-50MB
- **包含所有依赖**: 无需额外安装Python或库

## 🚀 发布流程

1. **更新版本号**
   ```bash
   python version_manager.py minor "新功能描述"
   ```

2. **本地测试**
   - 在macOS上构建并测试
   - 在Windows上构建并测试

3. **推送标签**
   ```bash
   git add .
   git commit -m "Release v1.x.x"
   git tag v1.x.x
   git push origin main
   git push origin v1.x.x
   ```

4. **自动构建**
   - GitHub Actions自动构建两个平台版本
   - 自动创建Release并上传文件

5. **手动验证**
   - 下载并测试两个平台的文件
   - 确认功能一致性

## 🔧 故障排除

### 常见构建问题

**Q: PyInstaller构建失败**
A: 
- 检查Python版本是否兼容
- 更新PyInstaller到最新版本
- 检查依赖是否完整安装

**Q: 生成的文件无法运行**
A:
- 检查目标系统是否满足要求
- 确认比特浏览器已安装
- 查看错误日志定位问题

**Q: 文件过大**
A:
- 这是正常现象，包含了所有依赖
- 可以使用UPX压缩（可能影响兼容性）
- 考虑移除不必要的依赖

## 📊 构建统计

| 平台 | 文件大小 | 构建时间 | 兼容性 |
|------|----------|----------|--------|
| macOS | ~60MB | 2-3分钟 | 10.14+ |
| Windows | ~40MB | 2-3分钟 | Win10/11 |

## 🔄 持续集成

项目配置了GitHub Actions自动构建：
- **触发条件**: 推送标签或手动触发
- **构建平台**: Windows + macOS
- **输出**: 两个平台的可执行文件
- **发布**: 自动创建GitHub Release
