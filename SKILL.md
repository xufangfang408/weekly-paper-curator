---
name: weekly-paper-curator
description: 为三维多组学、多组学表征学习、虚拟细胞或器官和临床转化抓取并筛选每周新论文，生成去重的中文 Top 100 阅读清单。用于周度文献推送、指定周补跑和记录用户明确给出的正负偏好。
---

# Weekly Paper Curator

通过本目录下的脚本运行。安装、换设备及环境变量设置见 [README.md](README.md)。优先使用技能目录已有的 `.venv`，或使用已安装 `requirements.txt` 中依赖的 Python。

## 生成周报

1. 运行 `python scripts/fetch_and_rank.py --check` 检查依赖、配置和历史库。首次在线运行需要 `OPENAI_API_KEY`，OpenAlex 深分页使用 `OPENALEX_API_KEY`。
2. 运行 `python scripts/fetch_and_rank.py`。默认检索含当天在内的 7 个 UTC 日期，输出最多 100 篇。补跑指定周时用 `--end-date YYYY-MM-DD`，窗口和篇数可用 `--days`、`--top-k` 调整。
3. 根据脚本退出状态和输出路径汇报本次结果。阅读清单给出方法、方向契合与临床转化分数，以及一条中文看点。依据为标题时注明其局限。出现部分抓取时，告知用户来源提示和可用输出，并使用相同结束日期重试。

## 更新偏好

只记录用户明确表示喜欢或希望少看的论文或方向。保留用户给出的理由，缺少理由时省略即可。

```bash
python scripts/fetch_and_rank.py --feedback-add positive --title '论文题目' --reason '用户喜欢的具体理由'
python scripts/fetch_and_rank.py --feedback-add negative --title '论文或方向' --reason '用户不想看的具体理由'
```

脚本把偏好保存到 `feedback.yaml`，下次评分自动读取。配置和已提交的偏好随 Git 同步。运行历史需单独迁移。
