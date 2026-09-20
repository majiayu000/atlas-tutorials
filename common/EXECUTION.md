# 通用执行约定：先准备，再提交，再交付

本教程包的 48 篇正文全部写完。正文和离线样例的完成，不代表 48 个付费工作流已经联调。在线模型、账户权限、价格和插件版本可能改变，执行前必须查当前环境。真实客户照片、私有代码、字体文件和账户密钥均未随包分发。

## 环境与路径

Shell 示例采用 Bash，从教程包根目录执行；Windows 可用 WSL，或用 PowerShell 按同样步骤操作，不能把 Bash 数组原样贴入 PowerShell。Python 脚本使用 Python 3.10+ 标准库；Node 示例使用带内建 fetch 的 Node 22+，生产环境选仍受维护的版本。媒体步骤需要 ffmpeg、ffprobe，脚本不会自动安装软件。`assets/` 路径代表你自己准备的获授权素材；无需把它们上传到 Git 仓库。

`MODEL`、`MODEL_ID`、`REFERENCE_URL` 都是明确的配置变量，不是产品自带模型或素材。本包不固定某家模型及价格。查询实际 schema 后，把必填项、单位、默认值、参考字段和允许值保存到任务记录中；不能仅改一个模型名称便复用其他模型的参数。

## 三种入口各自使用自己的契约

CLI：`atlas models get MODEL --json` 读取参数，`--explain` 预览编译后请求，`generate cost` 估价。CLI 的参数与 REST 字段可能有映射，优先看预览。独立 MCP：通过实际发现的工具 schema 调用，`params` 内是模型参数；当前实现常返回文字内容，不保证 structuredContent。REST：生成请求是 `{"model":"实际模型ID", ...模型参数}`，不是把 MCP 的整个请求包原样 POST。

查 schema 本身不等于调用生成模型。LLM chat、媒体生成都是潜在付费操作；上传会外发素材，即使上传步骤没有单独收费也需要授权。`--explain`、`dry_run` 不替代价格估算。独立 MCP 源码在 schema 缺失时存在跳过验证的路径，因此使用者必须自己确认 schema 已取得；不要把 dry_run 解释成所有参数一定经过完整验证。

## 完整操作记录

推荐一项业务任务固定一个目录：`tutorial-output/run-001/`。保存配置、版本、schema 记录、费用认知、授权范围、提交尝试、服务端 ID、结果观察、真实文件和验收结果。目录名不是服务端幂等键。异常后不要换一个目录再次提交相同业务任务。

本包的 `scripts/run_job.py` 提供 prepare / preview / submit / get / wait / inspect。prepare 完全离线；preview 读取服务并预览，不生成；submit 需要 `--approve` 才会尝试提交。脚本只保存本地事实，不替代账户授权、服务端幂等或硬预算。`--approve` 仅表示操作者明确放行，不证明获得了外部客户授权。

```bash
python3 scripts/run_job.py --help
python3 scripts/run_job.py prepare --config examples/config/image.json --run-dir tutorial-output/run-001
```

示例中的模型是占位符，prepare 会拒绝未填写的模型。先在当前账户发现真实模型并修改你自己的配置副本；不要随意填一个字符串来绕过检查。教程中的本地媒体工具则可使用离线 fixture，见 README 的离线演练。

## 何时可以重试

只读状态查询失败可以有界重试；已经确定受理的任务继续使用原 ID。提交超时且未得到 ID，记为 unknown，保留证据，核对同一账户历史或服务端记录。不得因为 HTTP 5xx、CLI 非零退出、空输出或断网就自动重交付费 POST。Ctrl+C 和本地等待超时不能证明服务端取消。再次运行新生成通常属于新操作，要重新确认范围。

远程状态 completed/succeeded、文件下载成功、文件可解码、内容符合要求是四个独立检查。技术工具不会证明产品标签准确、声音自然、肖像授权有效或广告有转化效果。

## 素材与输出的安全边界

不自动上传目录、不把凭据写进配置、不读取系统密钥文件。下载链接不应携带 Atlas API key；第三方地址也不能获得 Authorization 头。示例后处理只处理本地可信文件，解析非可信媒体仍应放进受限容器。敏感资料的 URL、提示词、回执和缩略图也需要访问控制；不要因为它们不是密码就公开。

## 阅读方式

每篇都给出明确目标、实际步骤、可复制的 Agent 指令、验收与失败分支。标明“本包约定”的 JSON 是教程辅助格式；Atlas 不会自动识别这些字段。模型特有能力缺失时，教程会给出可执行的基础路径或明确停止点，不凭空创造命令。
