# Weekly Paper Curator

按四个研究方向生成中文周度论文清单。使用 OpenAlex、bioRxiv、arXiv 获取文献，Europe PMC 补齐期刊摘要。每周默认选出最多 100 篇，生成 Markdown 和 CSV。

## 在新设备上使用

安装 Git 和 Python 3.9 或更新版本，并用有仓库权限的账号登录 GitHub。使用 GitHub CLI 时，可先运行 `gh auth login --git-protocol https` 并让 Git 使用该凭据。以下命令适用于 macOS／Linux。

```bash
git clone https://github.com/xufangfang408/weekly-paper-curator.git
cd weekly-paper-curator
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/fetch_and_rank.py --check
```

Windows PowerShell 用 `py -3 -m venv .venv` 创建环境，之后将 `.venv/bin/python` 替换为 `.\.venv\Scripts\python.exe`。

在线运行前，在启动脚本或 Codex 的同一环境设置 `OPENAI_API_KEY`。macOS／Linux 用 `export OPENAI_API_KEY='你的密钥'`，PowerShell 用 `$env:OPENAI_API_KEY = '你的密钥'`。使用兼容服务时可设置 `OPENAI_BASE_URL` 和 `OPENAI_MODEL`（默认 `https://api.openai.com/v1`、`gpt-4o-mini`）。设置 `OPENALEX_API_KEY` 可启用期刊抓取的游标分页。评分请求会将研究画像、偏好、论文标题和摘要发送给配置的模型服务。

```bash
.venv/bin/python scripts/fetch_and_rank.py
.venv/bin/python scripts/fetch_and_rank.py --end-date 2026-11-24 --days 7 --top-k 30
```

如果需要让 Codex 在任意项目识别技能，首次克隆时把目标路径设为 `"$HOME/.agents/skills/weekly-paper-curator"`，然后在该目录完成相同的虚拟环境安装。之后在 Codex CLI 或 IDE 输入 `$weekly-paper-curator` 即可调用。 [Codex 技能目录说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

## 偏好与跨设备连续性

- `config.yaml` 保存 13 本期刊、四类关键词、研究画像和有来源链接的顶会会期。会期与检索窗口重合时，arXiv 会额外检索会名。会名来自预印本元数据时，只作为追踪线索。
- `feedback.yaml` 随仓库分发。用 `--feedback-add positive` 或 `--feedback-add negative` 搭配 `--title` 和可选的 `--reason` 更新。需要同步新增偏好时，提交此文件，再在其他设备 `git pull`。
- `data/history.json` 和 `weekly_digests/` 是本地运行数据。换设备时复制历史库即可延续去重。也可把历史库保存在同步目录，并用 `--history` 指定其路径。每次在一台设备上运行，避免同步盘同时写入。
- 每台设备单独设置 API 密钥。虚拟环境、凭据文件、历史库及生成的周报均由 `.gitignore` 排除。

## 运行与重试

日期用 UTC，检索窗口包含起止两天。默认去重覆盖所有成功评分的候选，并在两个导出文件都写入后更新历史库。重复的 DOI、arXiv ID、OpenAlex ID 和标准化标题会合并，识别到预印本发表于配置中的顶刊时可再次入选。

抓取覆盖不完整时，若仍有候选则生成带来源提示的周报，保留历史库以便用同一日期重试。评分失败时退出并保留原历史库。无新候选时保留现有报告。缺失或空白的历史库可直接启动。

安装依赖后可用 `python -m unittest discover -s tests -v` 运行离线回归测试。
