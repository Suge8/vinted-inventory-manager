# Vinted 库存宝 / Vinted Inventory Manager

<div align="center">

[![GitHub release](https://img.shields.io/github/v/release/Suge8/vinted-inventory-manager)](https://github.com/Suge8/vinted-inventory-manager/releases)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows-blue)](https://github.com/Suge8/vinted-inventory-manager/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Language / 语言**: [🇺🇸 English](#english) | [🇨🇳 中文](#中文)

</div>

---

## 🇨🇳 中文

> 🛍️ **自动化Vinted库存监控工具** - 实时监控员工账户库存状态，自动发现待补货账号

一个专为Vinted电商网站设计的库存管理工具，通过BitBrowser API自动监控多个员工账户的库存状态，及时发现需要补货的账号。

### 💼 **产品背景与意义**

在Vinted电商运营中，通常采用以下组织架构：
- **管理员账号**: 负责监督和管理，关注所有员工账号
- **员工账号**: 负责发布和销售商品，处理日常订单

**核心问题**: 当员工账号的商品全部售完时，如果不及时补货，会导致：
- ❌ 账号长期无商品展示，影响店铺活跃度
- ❌ 错失潜在销售机会
- ❌ 影响Vinted平台算法推荐
- ❌ 降低整体团队销售业绩

**解决方案**: 本工具通过自动化监控，实时发现无库存的员工账号，确保：
- ✅ 及时发现待补货账号，避免长期空店
- ✅ 提高团队整体运营效率
- ✅ 保持所有账号的活跃状态
- ✅ 最大化销售机会和收益

## 🎯 核心功能

### 📊 **智能库存监控**
- 自动检测员工账户库存状态
- 实时发现无库存账号（待补货）
- 支持多管理员账户同时监控
- 24/7循环监控模式

### 🔔 **即时提醒系统**
- 🎵 音效提醒：发现待补货账号时播放提示音
- ⚠️ 视觉提醒：橙色警告图标闪烁
- 📋 持久显示：待补货账号列表持续显示
- 🔄 自动更新：补货后自动从列表移除

### 🖥️ **现代化界面**
- 简洁直观的操作流程，按提示操作即可
- 实时进度显示和状态更新
- 支持多窗口轮询监控，可设置间隔时间
- 支持macOS和Windows双平台

## 📥 下载安装

### 💾 **直接下载**（推荐）
前往 [Releases页面](https://github.com/Suge8/vinted-inventory-manager/releases) 下载最新版本：

- **macOS**: `Vinted 库存宝.app`
- **Windows**: `Vinted 库存宝.exe`

### 🔧 **系统要求**
- **macOS**: 10.14+ (Mojave或更高版本)
- **Windows**: 10/11 64位系统
- **BitBrowser**: 必须安装并运行
- **网络**: 稳定的互联网连接

## 📋 前置需求

### 🏢 **团队架构要求**
在使用本工具前，请确保您的Vinted团队已按以下方式组织：

1. **管理员账号设置**
   - 创建专门的管理员账号（或使用现有账号）
   - **重要**: 管理员账号必须关注所有需要监控的员工账号
   - 管理员账号用于监控，不一定需要发布商品

2. **员工账号设置**
   - 员工账号负责发布和销售商品
   - 确保员工账号已被管理员账号关注
   - 员工账号正常运营，发布商品和处理订单

3. **关注关系建立**
   ```
   管理员账号 → 关注 → 员工账号A
                ↓
              员工账号B
                ↓
              员工账号C
                ↓
               ...
   ```

### 🔧 **技术环境要求**
- **BitBrowser**: 已安装并运行
- **浏览器窗口**: 已登录管理员账号的Vinted
- **网络连接**: 稳定的互联网连接

## 🚀 快速开始

### 1️⃣ **准备工作**
```bash
# 1. 安装BitBrowser并启动
# 2. API服务会自动运行在 http://127.0.0.1:54345
# 3. 创建浏览器窗口并登录Vinted账户
```

### 2️⃣ **启动应用**
- **macOS**: 双击 `Vinted 库存宝.app`
- **Windows**: 双击 `Vinted 库存宝.exe`

### 3️⃣ **开始监控**
1. **选择浏览器窗口**: 从列表中选择已登录的窗口
2. **添加管理员账户**: 输入要监控的管理员用户ID
3. **设置监控参数**: 可配置循环间隔时间
4. **开始监控**: 按界面提示操作，系统将自动循环检查

## 🔍 工作原理

### 核心逻辑流程

1. **比特浏览器API连接**
   - 连接到比特浏览器API服务（默认：http://127.0.0.1:54345）
   - 获取可用的浏览器窗口列表
   - 用户选择要使用的浏览器窗口

2. **关注列表提取**
   - 通过比特浏览器API控制指定浏览器窗口
   - 访问管理员的关注列表页面
   - 智能分页检测：逐页提取所有被关注的员工用户信息
   - 支持多语言结束标志检测（"doesn't follow anyone yet"、"volgt nog niemand"等）
   - 自动停止翻页当检测到无更多用户

3. **库存检查**
   - 依次访问每个员工的个人商店页面
   - 智能商品检测：检测页面中的商品列表
   - 空状态识别：识别"没有商品在售"等状态信息
   - 商品信息提取：统计商品数量和提取真实商品标题

4. **结果分类**
   - **✅ 有库存**：检测到商品的员工账户
   - **❌ 无库存**：显示"没有商品在售"的员工账户
   - **⚠️ 访问异常**：无法正常访问或解析的员工账户

5. **报告生成**
   - 生成详细的 TXT 格式报告
   - 包含每个分类的用户列表和商品信息
   - 显示采集统计数据和时间戳

### 🏗️ 技术架构

```
vinted-inventory-manager/
├── src/                           # 源代码目录
│   ├── main.py                   # 主程序入口
│   ├── gui/                      # 图形界面模块
│   │   ├── main_window.py        # 主窗口界面（现代化UI）
│   │   └── components.py         # UI组件
│   ├── core/                     # 核心功能模块
│   │   ├── vinted_scraper.py     # Vinted数据采集引擎
│   │   ├── bitbrowser_api.py     # 比特浏览器API管理器
│   │   └── data_processor.py     # 数据处理器
│   ├── utils/                    # 工具函数
│   │   ├── helpers.py            # 通用辅助函数
│   │   ├── config.py             # 配置管理
│   │   └── logger.py             # 日志管理
│   └── tests/                    # 测试文件
├── dist/                         # 构建输出目录
│   ├── VintedInventoryManager.app # macOS应用程序包
│   └── VintedInventoryManager.exe # Windows可执行文件
├── resources/                    # 资源文件
├── build.py                      # 构建脚本
├── version_manager.py            # 版本管理工具
├── requirements.txt              # Python依赖
├── CHANGELOG.md                  # 更新日志
└── README.md                     # 项目说明
```

## 🛠️ 开发环境设置

### 环境要求
- Python 3.8+
- 比特浏览器 (BitBrowser)
- Selenium WebDriver

### 安装步骤

```bash
# 克隆项目
git clone <repository-url>
cd vinted-inventory-manager

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 运行开发版本

```bash
# 运行主程序
python src/main.py

# 运行测试
python -m pytest src/tests/
```

### 构建应用程序

#### 本地构建
```bash
# macOS构建
python build.py

# Windows构建（需要在Windows系统上运行）
python build_windows.py
```

#### 跨平台自动构建
```bash
# 使用GitHub Actions自动构建两个平台版本
git tag v1.x.x
git push origin v1.x.x
```

**重要**:
- PyInstaller无法跨平台构建，需要在对应系统上分别构建
- 详细构建说明请查看 [BUILD_GUIDE.md](BUILD_GUIDE.md)
- 每次修改代码后都需要重新构建应用程序包

### 版本管理

```bash
# 补丁版本更新（Bug修复）
python version_manager.py patch "修复描述"

# 次版本更新（新功能）
python version_manager.py minor "功能描述"

# 主版本更新（重大变更）
python version_manager.py major "重大变更描述"
```

## 📖 使用说明

### 准备工作
1. **安装比特浏览器**：确保比特浏览器已安装并运行
2. **启动API服务**：比特浏览器会自动启动API服务（默认端口54345）
3. **创建浏览器窗口**：在比特浏览器中创建新的浏览器窗口
4. **登录Vinted**：在浏览器窗口中登录 Vinted 账户
5. **准备关注列表URL**：获取管理员账户的关注列表页面URL

### 操作步骤
1. **启动应用程序**：双击运行可执行文件
2. **🔧 Step 1**: 确认比特浏览器API地址（通常无需修改）
3. **🔗 Step 2**: 点击"🧪 测试连接"验证API连接状态
4. **🌐 Step 3**: 从列表中选择要使用的浏览器窗口
5. **📋 Step 4**: 输入管理员关注列表的完整 URL
6. **🚀 Step 5**: 点击"🔍 开始查询"按钮
7. **📊 Step 6**: 等待采集完成，点击"📄 打开结果"查看报告

### 注意事项
- 采集过程中请勿关闭比特浏览器或目标浏览器窗口
- 网络连接需要稳定，避免采集中断
- 大量用户的采集可能需要较长时间（每个用户约2-3秒）
- 报告文件会保存在应用程序同目录下
- 可以点击"📋 显示日志"查看详细的采集过程

## 🔧 故障排除

### 常见问题

**Q: 程序提示"连接失败"或找不到比特浏览器**
A:
- 确保比特浏览器已启动并运行
- 检查API地址是否正确（默认：http://127.0.0.1:54345）
- 确认比特浏览器的API服务已启用

**Q: 程序提示找不到浏览器窗口**
A:
- 在比特浏览器中创建并打开至少一个浏览器窗口
- 确保浏览器窗口已登录 Vinted 账户
- 点击"🔄 刷新列表"重新获取窗口列表

**Q: 采集过程中断或出错**
A:
- 检查网络连接，确保 Vinted 网站可正常访问
- 确认目标浏览器窗口没有被关闭
- 查看日志区域了解具体错误信息

**Q: 无法检测到用户关注列表结束**
A:
- 程序会自动检测多语言结束标志
- 检查关注列表URL是否正确
- 确认管理员账户的关注列表是公开的

**Q: 生成的报告为空或数据不完整**
A:
- 检查关注列表是否为空
- 确认访问权限，某些用户可能设置了隐私保护
- 查看日志了解具体的采集过程

**Q: 商品信息显示不正确**
A:
- 程序会智能过滤价格、评级等信息，只显示商品名称
- 如果显示"1"等数字，可能是商品名称提取失败
- 这通常不影响库存状态的判断

## 📋 更新日志

详细的更新记录请查看 [CHANGELOG.md](CHANGELOG.md)

当前版本：**v1.3.2** - 修正README文档，更新为比特浏览器API的正确描述

## 📞 技术支持

如有问题或建议，请：
- 查看 [Issues](https://github.com/Suge8/vinted-inventory-manager/issues)
- 提交新的 Issue 描述问题
- 查看 [CHANGELOG.md](CHANGELOG.md) 了解更新历史

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 🇺🇸 English

> 🛍️ **Automated Vinted Inventory Monitoring Tool** - Real-time monitoring of employee account inventory status, automatically discover accounts that need restocking

A specialized inventory management tool designed for Vinted e-commerce platform that automatically monitors the inventory status of multiple employee accounts through BitBrowser API and promptly identifies accounts that need restocking.

### 🎯 Core Features

#### 📊 **Smart Inventory Monitoring**
- Automatically detect employee account inventory status
- Real-time discovery of out-of-stock accounts (need restocking)
- Support monitoring multiple admin accounts simultaneously
- 24/7 continuous monitoring mode

#### 🔔 **Instant Alert System**
- 🎵 Audio alerts: Play notification sound when out-of-stock accounts are found
- ⚠️ Visual alerts: Orange warning icon flashing
- 📋 Persistent display: Out-of-stock account list continuously displayed
- 🔄 Auto-update: Automatically remove from list after restocking

#### 🖥️ **Modern Interface**
- Simple and intuitive 6-step operation process
- Real-time progress display and status updates
- Beautiful HTML format report generation
- Support for both macOS and Windows platforms

### 📥 Download & Installation

#### 💾 **Direct Download** (Recommended)
Go to [Releases page](https://github.com/Suge8/vinted-inventory-manager/releases) to download the latest version:

- **macOS**: `Vinted 库存宝.app`
- **Windows**: `Vinted 库存宝.exe`

#### 🔧 **System Requirements**
- **macOS**: 10.14+ (Mojave or higher)
- **Windows**: 10/11 64-bit system
- **BitBrowser**: Must be installed and running
- **Network**: Stable internet connection

### 🚀 Quick Start

#### 1️⃣ **Preparation**
```bash
# 1. Install BitBrowser and start it
# 2. API service runs automatically on http://127.0.0.1:54345
# 3. Create browser window and login to Vinted account
```

#### 2️⃣ **Launch Application**
- **macOS**: Double-click `Vinted 库存宝.app`
- **Windows**: Double-click `Vinted 库存宝.exe`

#### 3️⃣ **Start Monitoring**
1. **Select Browser Window**: Choose logged-in window from the list
2. **Add Admin Account**: Enter admin user ID to monitor
3. **Configure Parameters**: Set monitoring interval time
4. **Start Monitoring**: Follow interface prompts, system will automatically loop check

### 🔍 How It Works

#### 📋 **Monitoring Process**
The application follows a simple loop:
1. **Connect** to BitBrowser API
2. **Fetch** following lists from admin accounts
3. **Check** each user's inventory status
4. **Alert** when out-of-stock accounts are found
5. **Repeat** continuously with configurable intervals

#### 🔧 **Technical Implementation**
1. **BitBrowser Integration**: Control browser windows through API, avoid anti-crawling detection
2. **Smart Parsing**: Automatically recognize Vinted page structure, accurately determine inventory status
3. **Loop Monitoring**: Configurable interval time, continuous monitoring of inventory changes
4. **Real-time Alerts**: Audio + visual dual alerts, ensure timely discovery of accounts needing restock

### 🎯 Use Cases

#### 👥 **Target Teams**
- **Vinted Sellers**: Manage multiple employee account inventories
- **E-commerce Teams**: Real-time monitoring of product inventory status
- **Operations Staff**: Timely discovery of accounts needing restock

#### 💼 **Typical Workflow**
1. **Setup Monitoring**: Add admin accounts to monitor
2. **Start Monitoring**: Program automatically loops to check inventory status
3. **Receive Alerts**: Immediate notification when out-of-stock accounts are found
4. **Timely Restock**: Restock relevant accounts based on alerts
5. **Continuous Monitoring**: 24/7 uninterrupted monitoring, ensure sufficient inventory

### 🛡️ Security & Compliance

#### ✅ **Security Guarantee**
- **Local Operation**: All data processing is local, no upload to external servers
- **Open Source**: Complete source code is public, can be audited independently
- **Privacy Protection**: Only access public information, no collection of sensitive data
- **Compliant Usage**: Follow website terms of use, reasonable control of access frequency

### 🔧 Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Interface** | CustomTkinter | Modern desktop GUI |
| **Automation** | Selenium WebDriver | Browser control |
| **Parsing** | BeautifulSoup4 | HTML content parsing |
| **Network** | Requests | HTTP request handling |
| **Packaging** | PyInstaller | Generate executable files |
| **Build** | GitHub Actions | Automated CI/CD |

### 📞 Technical Support

For questions or suggestions, please:
- Check [Issues](https://github.com/Suge8/vinted-inventory-manager/issues)
- Submit new Issue describing the problem
- Check [CHANGELOG.md](CHANGELOG.md) for update history

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⭐ If this project helps you, please give it a Star!**
