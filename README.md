# 浏览器启动管理器 (Browser Manager)

基于 Python + Tkinter 构建的图形化浏览器启动管理工具，支持多浏览器、多配置文件的分组管理，通过 JSON 配置文件统一管理所有浏览器启动参数。

## 功能特性

- **分组管理**：按分组路径（如 `工作/Google`）组织配置，支持多级嵌套文件夹结构
- **可视化面板**：左侧树形目录 + 右侧 JSON 详情，一目了然
- **一键启动**：双击或点击按钮即可启动浏览器
- **配置编辑**：支持新建、编辑、复制、移动、删除配置
- **丰富参数**：支持用户数据目录、配置文件目录、代理服务器、隐身模式、应用模式、自定义额外参数等

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | Windows 10+ |
| Python 版本 | 3.6+ |
| 依赖库 | 仅使用 Python 标准库（`json`, `os`, `sys`, `subprocess`, `tkinter`, `shutil`），无需额外安装 |

## 快速开始

```bash
python browser_manager.py
```

首次运行时会自动在当前目录下创建空的配置文件 `browser_configs.json`。

## 配置文件说明

配置文件 `browser_configs.json` 是一个 JSON 数组，每个元素为一个浏览器配置对象，结构如下：

```json
[
  {
    "name": "Google Chrome - 工作账号",
    "group": "工作",
    "browser_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "user_data_dir": "C:\\Users\\Windows 10\\AppData\\Local\\Google\\Chrome\\User Data",
    "profile_directory": "Profile 1",
    "proxy_server": "",
    "disable_plugins": false,
    "incognito": false,
    "app": "",
    "extra_params": ""
  }
]
```

### 字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | string | **是** | 配置名称，在同一分组下需唯一 |
| `group` | string | 否 | 分组路径，使用 `/` 分隔多级分组，如 `工作/常用`。不填则为"未分组" |
| `browser_path` | string | **是** | 浏览器可执行文件的完整路径 |
| `user_data_dir` | string | 否 | 用户数据目录路径 |
| `profile_directory` | string | 否 | 配置文件目录名称（如 `Profile 1`） |
| `proxy_server` | string | 否 | 代理服务器地址，如 `127.0.0.1:7890` |
| `disable_plugins` | boolean | 否 | 是否禁用插件，`true` 或 `false` |
| `incognito` | boolean | 否 | 是否启用隐身/私密模式，`true` 或 `false` |
| `app` | string | 否 | 以应用模式启动指定页面，如 `https://mail.google.com` |
| `extra_params` | string | 否 | 额外的启动参数，多个参数以空格分隔 |

> **注意**：`name` 字段为必填项，保存时若缺少该字段将报错。同一分组下不允许存在相同名称的配置。

## 界面操作

### 左侧面板（树形目录）

- **📁 文件夹**：代表一个分组，可展开/折叠
- **🌐 配置项**：代表一个浏览器配置，可双击启动
- **右键/按钮操作**：新建配置、刷新目录

### 右侧面板（详情与操作）

选中左侧的配置项后，右侧将显示其 JSON 详情，并提供以下按钮：

| 按钮 | 功能 |
|------|------|
| 启动浏览器 | 按当前配置启动浏览器 |
| 编辑配置 | 弹出编辑窗口，可修改全部 JSON 字段 |
| 创建副本 | 基于当前配置创建副本（名称自动加 `_副本` 后缀） |
| 移动分组 | 将配置移动到新的分组路径 |
| 删除配置 | 删除当前选中的配置（需确认） |

## 启动命令构建逻辑

程序会根据配置字段自动构建浏览器启动命令，规则如下：

```
<browser_path> [--user-data-dir=<dir>] [--profile-directory=<dir>]
               [--proxy-server=<server>] [--disable-plugins] [--incognito|-private]
               [--app=<url>] [额外参数...]
```

- 隐身模式参数根据浏览器类型自动选择：Chrome/Chromium 使用 `--incognito`，其他浏览器（如 Firefox）使用 `-private`
- `extra_params` 中的内容会按空格拆分后追加到命令末尾

## 界面预览

```
┌──────────────────────────────────────────────────────────────┐
│  浏览器启动管理器                                             │
├─────────────────┬────────────────────────────────────────────┤
│  📁 工作         │  配置详情:                                   │
│    🌐 Chrome     │  {                                          │
│    🌐 Edge       │    "name": "Chrome",                       │
│  📁 个人         │    "group": "工作",                         │
│    🌐 Firefox    │    "browser_path": "C:\\...",              │
│  🌐 默认配置      │    ...                                     │
│                   │  }                                          │
│  [新建配置] [刷新] │                                            │
├─────────────────┼────────────────────────────────────────────┤
│  [启动] [编辑] [副本] [移动] [删除]                             │
├──────────────────────────────────────────────────────────────┤
│  已加载 4 个配置                                              │
└──────────────────────────────────────────────────────────────┘
```

## 常见问题

**Q: 如何同时启动多个浏览器？**

A: 每个配置项使用独立的数据目录（`user_data_dir`），即可同时运行多个浏览器实例。

**Q: Firefox 如何使用？**

A: 不支持。

**Q: 配置文件可以手动编辑吗？**

A: 可以。`browser_configs.json` 是标准 JSON 格式，可用任意文本编辑器修改。修改后点击"刷新"按钮或重启程序即可生效。

**Q: 支持打包为 exe 吗？**

A: 支持。编辑 `browser_manager.spec` 文件，可使用 PyInstaller 打包：

```bash
pyinstaller browser_manager.spec
```

## 项目结构

```
.
├── browser_manager.py      # 主程序
├── browser_configs.json    # 配置文件（首次运行自动生成）
├── browser_manager.spec    # PyInstaller 打包配置
├── README.md               # 本文件
└── build/                  # 打包输出目录
```

## 许可证

MIT License
