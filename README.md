# Atlas 多模态 Agent 教程全集

**48 篇中文完整教程 · 可编辑 Markdown · CLI / Skill / MCP / API · 离线脚本与集成样例**

这是上一版“48 个选题＋6 篇正文”的完整扩展：原六篇已统一修订，其余 42 篇全部写成正文。内容从首次接入、网站与产品素材，一直覆盖声音、本地化、后处理、自动化、恢复、评测与 Skill 贡献。模型相关操作先核实当前能力，不以虚构命令填补功能缺口。

**直接阅读：** 双击解压目录中的 [index.html](index.html)，可按类别和全文搜索，点击代码块旁按钮复制。无需启动服务器、联网或安装文档站。也可以从 [完整目录](CATALOG.md) 阅读 Markdown。

## 先分清完成范围

本包完成了全部教程正文、配套教学脚本、配置/工作流示例、离线测试与打包。没有使用你的 API key、登录账户、执行付费模型生成、向客户素材发起上传，也没有修改 GitHub 仓库。n8n、ComfyUI、MCP 宿主和 GitHub Actions 的真实连接未代你联调。

真实输出质量、模型权限、价格与宿主兼容性要在当前环境检查。目录里出现模型占位或 `assets/` 自备文件，是执行配置边界，不是省略教程正文。集成 JSON 可以编辑与导入检查，但不能宣传成已在线认证的现成服务。

## 建议的三条阅读路线

| 使用目标 | 阅读顺序 |
|---|---|
| 第一次用 Agent 做图和视频 | 01 → 02 → 04 → 05 → 13 → 19 → 43 |
| 为项目交付一套素材或成片 | 07 / 08 / 09 → 12 → 16 → 20 → 25 → 26 → 34 → 35 |
| 做可靠自动化与生态贡献 | 18 → 37 / 38 → 39 / 40 / 41 → 42 → 44 → 45 → 46 → 47 → 48 |

所有命令从解压包根目录执行。Shell 使用 Bash；Python 工具采用标准库，要求 Python 3.10+；Node 示例推荐仍受维护且兼容的 Node 22+；本地媒体处理需要可用的 ffmpeg/ffprobe。脚本不会自动安装软件，包内不分发字体。

## 无账户的离线演练

先运行不发网络请求的单元测试：

```bash
python3 -m unittest discover -s tests -v
node --test tests/node-client.test.mjs
```

机器安装 FFmpeg 后，再执行本地媒体 smoke 测试。输出目录必须尚不存在；再次测试换新目录，不删除任何真实任务记录来重试：

```bash
python3 tests/run_smoke.py --out tutorial-output/offline-smoke-01
```

测试会合成图案视频和音调，验证图片适配、截图合成、视频规范化/拼接、字幕、混音、全片解码、对比预览、录音切片、盲评打包和文件清单。合成音调没有人声，示例字幕不是识别结果，这些文件不能作为 Atlas 模型能力样片。

本次实测日志已放在 [verification/](verification/REPORT.md)。完整输出媒体不会重复随包分发；可以运行上述脚本在自己的机器复现，预留的测试输入小样放在 verification/offline-fixtures/。

## 目录用途

| 目录 / 文件 | 内容 |
|---|---|
| `tutorials/` | 48 篇完整中文教程 |
| `scripts/` | 10 个 Python 辅助工具，默认不执行付费生成；run_job 的 submit 需显式放行 |
| `examples/node/` | Node REST 客户端，无第三方 SDK、无自动付费 POST 重试 |
| `examples/workflows/` | n8n、ComfyUI 与手动 CI 教学配置；缺省不带凭据 |
| `examples/briefs/`、`config/`、`subtitles/` | 可编辑需求、配置、时间戳与审批记录示例 |
| `examples/layouts/` | 本地 HTML 标题卡，使用你自己的图片和系统字体 |
| `examples/skills/` | 产品广告 Skill、reference 与六个评测用例 |
| `common/`、`templates/` | 统一执行约定、交付检查和教程模板 |
| `tests/`、`verification/` | 可复跑测试、实测记录和验证边界 |
| `SOURCES.md`、`PUBLISHING.md` | 来源版本、发布复现检查 |
| `SHA256SUMS.txt` | 包内文件摘要；校验文件自身不列入 |

## 接真实账户之前

先读 [执行约定](common/EXECUTION.md)。保留现有账户，不把 key 粘贴到公开文档或 Agent 对话；上传与生成分别确认范围。复制配置后填入实时发现的模型与参数，执行只读预览并取得可靠的费用认知。

`run_job.py --approve` 表示调用者放行一次提交，不是服务端硬预算。原任务超时继续查询原 ID，提交结果不确定时保留 unknown，不自动重交。客户端只记录观察，文件还要解码和人工验收。

## 作为仓库或文档站发布

教程 Markdown 可以按目录直接加入你的文档仓库，保持相对路径。不要把本地 `assets/`、`tutorial-output/`、真实回执、凭据或客户图片一并公开。集成到现有站点后按 [发布清单](PUBLISHING.md) 检查导航、复制代码、能力版本和真实样例。

本包没有代你创建 GitHub commit 或发布线上网站。教程及原创代码为本次交付内容；上游工作流结构的许可证和归属见 [第三方说明](third-party/README.md)，生成素材的使用范围仍需按实际来源与授权确认。
