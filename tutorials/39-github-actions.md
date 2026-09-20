# 39｜在 GitHub Actions 中生成发布素材

在 CI 中生成发布素材，需要显式触发、固定代码来源、保护凭据和保存回执。不要把付费生成默认挂在每个 PR 或每次 push 上。本包提供手动触发示例，并将“只预览”和“真的生成”分开。

## 示例的具体保护

[manual-generation.yml](../examples/workflows/manual-generation.yml) 放在 examples 目录，不会自动启用。它采用 `workflow_dispatch`，只允许私有仓库的 main 分支，execute 默认 false，固定单次图片提交。生成 job 使用名为 `atlas-generation` 的 environment，必须由你在仓库中配置审批人和密钥；写了环境名并不会自动创建审批规则。

> 为这个私有仓库配置一条手动生成发布素材的 CI，默认只做请求预览。只使用受信任分支代码，API key 存于受审批环境。提交后保留回执，不因 workflow 重跑而重新生成；失败后先核对原任务。不要配置 pull_request_target 来运行贡献者代码并读取生成密钥。

## 准备仓库与参数

先把所需教程脚本审阅后放入目标仓库，核对真实模型 schema、价格和示例 prompt。复制 YAML 到 `.github/workflows/` 后再检查 paths。当前示例使用 Node REST 客户端，因此托管 runner 不需要额外安装 Atlas 二进制；已有安全安装渠道的自托管 runner 也可以用 [37](37-python-cli.md) 的 CLI 包装器。

示例中的 actions 使用主版本引用以便阅读。上线前应按团队供应链策略核实并固定完整 commit SHA，记录升级流程；本包没有把未核实的 SHA 写成可信锁定值。

## 先跑 preview，再决定付费

在工作流手动触发页填入已核实模型，保持 execute=false。模型值经环境变量传到 Node，不直接插入 Shell 代码。预览只展示请求形状；该 Node 客户端没有实时 schema/价格查询，因此仍需事先确认模型当前必填参数和费用。

确定范围后再显式 execute=true，并经 environment 审批。密钥仅在生成步骤注入。生成以单次提交开始，接受到任务 ID 后只轮询它。本例禁止同一次运行的第二次 attempt 自动执行生成，但新开 workflow run 仍可能重复付费，不能把它当作跨运行幂等。

## 回执与失败恢复

受理后，即使等待超时，仍将回执保存在受控 artifact，示例保留一天。回执可能有 prompt 与临时 URL，因此示例限制私有仓库；生产中还需设置访问范围、保存周期与脱敏。不要为方便下载，公开包含客户素材的整个运行目录。

取回回执后使用原 ID 查询，不要点击 rerun 来“继续等待”。如果 runner 在落盘前被销毁而没有 ID，按 [45](45-unknown-submission.md) 核对。取消工作流只停止 CI 进程，不一定取消已经受理的服务端生成。

## 发布检查

真正用于 Release 或网站的文件需要下载、技术验收与人工内容检查，见 [35](35-delivery-audit.md)。本示例只演示请求与回执，不自动把未经审核的产物发布到 Release，也不自动修改代码提交。

验收包括：默认无付费请求、非受信代码拿不到密钥、日志无明文 key、未知请求不重提、结果可用原 ID 继续查询。YAML 静态解析通过不等于 GitHub 云端联调成功；本包没有替你创建或运行工作流。

## 依据与复现范围

依据：[S6、S8、S10](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
