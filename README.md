# demo01 · Olist 电商数据工作区

整理 Olist 电商 CSV 数据，提供可重复的 Python 开发环境和数据完整性检查，供 Codex Cloud、本地开发及 GitHub Codespaces 使用。

当前仓库以数据为主，包含 9 个原始 CSV，共 1,550,922 条记录、126,186,995 字节（约 120.3 MiB）。

## 目录

```text
demo01/
├── data/
│   ├── raw/                    # 原始 CSV
│   ├── manifest.json           # 字段、记录数、字节数和 SHA-256
│   └── README.md               # 数据表与关联说明
├── scripts/
│   ├── setup.sh                # Linux 云端初始化
│   └── validate_data.py        # 流式数据完整性检查
├── tests/                      # 检查脚本的单元测试
├── docs/cloud-environment.md   # Codex Cloud 账号端配置步骤
├── .devcontainer/              # Codespaces / VS Code 开发容器
├── .github/workflows/ci.yml    # Linux、Windows 自动检查
└── AGENTS.md                   # Codex 开发与验证约定
```

## 快速开始

需要 Python 3.11 或更新版本。现有检查工具只使用 Python 标准库。

Linux、macOS 或 Codex Cloud：

```bash
bash scripts/setup.sh
.venv/bin/python scripts/validate_data.py
.venv/bin/python -m unittest discover -s tests -v
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe scripts/validate_data.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

默认完整检查字段顺序、文件大小、CSV 记录宽度、记录数和 SHA-256。需要快速确认工作区时，执行 `python scripts/validate_data.py --quick`，仅检查文件存在、大小和表头。评论字段可能包含换行，记录数应由 CSV 解析器计算。

## 云端开发

- **Codex Cloud**：按 [云端环境配置说明](docs/cloud-environment.md) 创建、测试并发布账号中的环境。
- **GitHub Codespaces**：打开仓库的 Code → Codespaces → Create codespace；开发容器会使用 Python 3.11 并执行初始化脚本。
- **VS Code Dev Containers**：打开仓库后执行 Reopen in Container。

如果已经在 Windows 创建了 `.venv`，进入 Linux 开发容器前先将它改名，让容器创建适用的虚拟环境。

仓库中的初始化脚本需要在 Codex Cloud 环境配置中明确调用。提交配置文件与发布账号中的云环境是两个步骤。

## 数据使用

数据读取路径统一为 `data/raw/<文件名>.csv`，从原仓库根目录读取 CSV 的已有脚本需要更新路径。完整字段和校验基线见 [数据说明](data/README.md) 与 [manifest](data/manifest.json)。

分析结果可写入 `reports/` 或 `output/`；这两个目录的生成文件已加入 Git 忽略规则。新增处理代码放在 `scripts/`，同时补充对应验证。原始数据的更新应同时检查并解释 manifest 的变化。
