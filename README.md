# Weekly Paper Curator

这是一个面向 Codex 的周度论文筛选技能。一次安装后，直接在对话中要求检索、打分、生成中文文献清单或记录阅读偏好。默认对话模式使用 Codex 的检索工具和模型。

## 在 Codex 安装

使用有仓库访问权限的 GitHub 账号，在 Codex 中发送下面这句话。仓库根目录即为技能目录。

> 请用 $skill-installer 从私有仓库 xufangfang408/weekly-paper-curator 的 main 分支根目录安装 weekly-paper-curator，并确认 Codex 能发现它。

已有本地仓库时，也可以把本目录放到 Codex 识别的技能目录（例如 `~/.agents/skills/weekly-paper-curator`）。打开新对话后可在技能选择器中选择它，或在提示词中输入 `$weekly-paper-curator`。 [Codex 技能目录说明](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

## 直接下达指令

- `$weekly-paper-curator 帮我筛选本周最值得读的 20 篇，重点看虚拟细胞和药物响应。`
- `$weekly-paper-curator 补跑 2026-11-18 到 2026-11-24，给我 Markdown 和 CSV。`
- `$weekly-paper-curator 记住，我更喜欢用外部队列验证的空间多组学论文，因为结论更容易迁移。`

默认检索最近 7 个 UTC 日期，最多推荐 100 篇，按方法学、研究契合度和转化价值打分。每条推荐包含原始链接和证据级别。完整报告保存到当前工作区的 `weekly_digests/`，也可在指令中指定目录。

## 迁移配置与阅读记录

- `config.yaml` 保存 13 本期刊、四类方向、研究画像及已核实的顶会会期。
- `feedback.yaml` 随私有仓库分发。Codex 记录的新偏好可提交到同一仓库，让新设备安装时带上这些偏好。
- `data/history.json` 是本地历史库。若要在新设备延续跨周去重，复制到新安装技能的相同相对路径。旧设备的周报可以另外复制。
- 技能目录只读时，新记录保存在当前工作区的 `.weekly-paper-curator/`。迁移同一工作区时，可以一起复制这个目录。

## 独立命令行模式

此模式供需要定时或批量调用引擎的用户使用。安装 Python 3.9 或更新版本，在仓库目录运行以下命令。

```bash
python -m pip install -r requirements.txt
python scripts/fetch_and_rank.py --check
```

脚本使用 `OPENAI_API_KEY` 评分。可用 `OPENAI_BASE_URL` 和 `OPENAI_MODEL` 指定兼容服务。设置 `OPENALEX_API_KEY` 可启用 OpenAlex 游标分页。评分请求会把研究画像、偏好、论文标题和摘要发送给所配置的模型服务。

```bash
python scripts/fetch_and_rank.py
python scripts/fetch_and_rank.py --end-date 2026-11-24 --days 7 --top-k 30
python -m unittest discover -s tests -v
```

命令行模式在两份报告导出后才更新历史库。遇到关键来源失败而生成部分结果时保留历史库，可用同一结束日期补跑。通过 `--history` 可指向已有历史库，通过 `--feedback-add positive` 或 `--feedback-add negative` 搭配 `--title` 和可选的 `--reason` 可更新偏好。
