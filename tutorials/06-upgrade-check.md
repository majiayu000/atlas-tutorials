# 06｜升级 Atlas 后，怎样检查旧教程还能不能用

升级后最危险的现象是命令仍能执行，但默认参数或结果结构改变。本篇建立一个无需生成的兼容检查，再把有费用的回归测试留给明确批准的测试账户。

## 升级前保存一个基线

```bash
mkdir -p tutorial-output/compat-before
atlas version --json > tutorial-output/compat-before/version.json
atlas --help > tutorial-output/compat-before/help.txt
atlas skills read atlas --raw > tutorial-output/compat-before/skill.md
atlas generate image --help > tutorial-output/compat-before/image-help.txt
```

基线还应记录安装渠道、操作系统、宿主与 MCP 包版本，以及当前工作流的配置摘要。不要把 auth 凭据目录打包。项目使用的模型 schema 另存快照，但价格仍需要执行时刷新。

## 按原渠道升级

npm 安装由 npm 管理，Homebrew 由 Homebrew 管理，原生安装由其支持的更新机制管理。不要同时装几份不同来源的 `atlas` 再猜正在执行哪份。用 `command -v atlas` 查看实际入口；PATH 中旧目录排在前面时，升级可能根本没有影响当前进程。

升级后在 `compat-after` 保存相同四份文件。团队自动化应锁定经过自己验证的版本，不在计费任务执行中自动追浮动最新版。

## 分四层对照

第一层看命令是否存在；第二层看当前 `skills read` 的操作说明；第三层用原参数运行 `--explain`，检查字段、类型和默认值；第四层用已存在的任务 ID 查询结果，观察 JSON 字段。第四层是只读核对，不能为了方便重新生成一批旧任务。

```bash
diff -u tutorial-output/compat-before/help.txt tutorial-output/compat-after/help.txt || true
python3 -m unittest discover -s tests -v
```

`diff` 的非零返回通常表示存在差异，不等于升级失败。离线测试也只验证本包脚本，不证明当前 Atlas 模型服务可用。遇到 `id`/`prediction_id` 差异应修适配器与测试，不让 Agent 从任意 JSON 中猜 ID。

## 再进行小规模在线回归

由操作者批准一个低风险任务，固定输入与交付规格，记录价格、模型和返回状态。检查参考素材是否真的使用、文件是否保存、下载失败能否仅恢复下载。不要要求生成字节完全相同，除非模型服务明确提供相应确定性保证。

## 复制给 Agent

> 帮我核对 Atlas 升级兼容性。保留原账户与环境，只检查版本、命令、内置指南、请求预览和已有任务状态，不创建新的付费任务。把破坏性变化与新增能力分开，给出需要修改的文件和测试项。

## 通过与回退

能够解释旧流程在哪个版本上通过，哪些字段需要适配。回退客户端不能自动回退服务端模型 schema；一个旧二进制也可能无法继续使用已变更或下线的模型。故障任务仍使用原 ID 查证，勿因回退操作再次计费。

## 依据与复现范围

依据：[S1、S2](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
