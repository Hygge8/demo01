# Codex Cloud 环境配置

仓库包含可调用的初始化脚本和 Codespaces 开发容器。Codex Cloud 的环境属于 ChatGPT 账号，需要在账号中完成创建、测试和发布。

## 当前 Codex Cloud

1. 登录 ChatGPT，在 **Settings → Codex Cloud → Environments → Create environment** 创建环境。也可从新任务的 **Work in → Cloud → Select environment → Create environment** 进入。
2. 选择 GitHub 仓库 **Hygge8/demo01**。使用包含本配置的版本；如果配置仍在 PR 分支，先合并 PR，或者在环境设置支持选择版本时选该分支。
3. 点击 **Get started**。在环境设置会话中给出下面的配置要求：

   ```text
   为 Hygge8/demo01 配置 Python 3.11 云端数据工作区。
   在仓库根目录以 bash scripts/setup.sh 初始化 .venv。
   将这条命令记录到 Install script。
   这个项目是数据工作区，无需常驻服务。
   在启动检查中使用 .venv/bin/python scripts/validate_data.py --quick。
   用 .venv/bin/python -m unittest discover -s tests -v 运行测试，
   并用 .venv/bin/python scripts/validate_data.py 做完整数据检查。
   当前工具只用标准库，无需第三方依赖或环境密钥。
   保持环境仅本人可用。
   ```

4. 检查配置中的 **Install script** 和 **Start skill**，核对初始化与测试报告。保存配置并点击 **Publish**。
5. 看到 **Environment published** 后，点击 **Start a new task**。选择该环境并再次运行快速检查，确认发布后的工作区可以使用。

Python 虚拟环境的激活仅影响当前 shell。后续命令直接调用 `.venv/bin/python`，以确保使用项目解释器。

新任务使用已发布环境准备好的文件系统；已有任务继续使用各自的状态。更新安装配置后，通过环境菜单 **Edit → Republish** 发布新的起点。仓库自动刷新保留依赖缓存，不重新运行安装或启动命令。

## 旧版 Codex Cloud 集成

旧版环境仍用于 Code Review、Linear 和 GitHub 集成，其配置名称为 **Setup script** 和可选的 **Maintenance script**。这两个字段都可填写：

```bash
bash scripts/setup.sh
```

该脚本可重复运行，已有虚拟环境会复用，并执行轻量数据检查。旧版 Setup script 的 `export` 不会自动传递到后续 agent 会话；使用明确的解释器路径。

## GitHub Codespaces

仓库的 `.devcontainer/devcontainer.json` 使用 Python 3.11 开发镜像，创建容器时执行同一个初始化脚本。在 GitHub 的 **Code → Codespaces** 创建工作区后，运行：

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_data.py
```

## 官方资料

- [当前 Codex Cloud 环境：创建、发布与更新](https://learn.chatgpt.com/docs/environments/cloud-environments)
- [旧版 Codex Cloud 环境：Setup / Maintenance script](https://learn.chatgpt.com/docs/environments/cloud-environment)

本说明依据 2026-10-04 的官方文档。
