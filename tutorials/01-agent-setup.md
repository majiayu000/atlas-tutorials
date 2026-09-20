# 01｜把 Atlas 接入你的 Agent，先不花钱生成

你已经有自己的 Agent，希望它能调用 Atlas。第一步只验证三件事：终端能找到 CLI，当前登录状态清楚，Agent 能读到 Atlas 的操作指南。完成配置不需要先生成一张测试图片。

本文适合本地有终端能力的 Agent。没有终端访问能力的网页宿主，不能照搬这条路径。MCP 用户参见 [03](03-local-mcp.md)，不必同时安装两条执行路线。

> 状态：正文已完成；未执行线上付费生成或宿主实连。依据：[S1 / S2 / S3](../SOURCES.md)。本地测试范围见 [验证报告](../verification/REPORT.md)。

## 先确认安装

已有 Atlas 时先检查，不要覆盖现有配置：

```bash
atlas version --json
atlas --help
```

没有安装且已有 Node.js/npm 的环境，可以采用公开包：

```bash
npm install -g atlascloud-cli
atlas version --json
```

没有 npm 的环境，使用公开 CLI 仓库给出的系统安装器；不要为了一个安装步骤下载来历不明的脚本。安装成功后如果 Agent 仍报告找不到命令，确认 Agent 启动时使用的 PATH，并重新启动对应进程。

## 检查认证，不要把密钥贴给 Agent

```bash
atlas auth status --json
```

这里检查的是本地认证状态。`logged_in` 表示本地访问令牌尚未过期，不保证某个供应商模型一定接受调用。遇到 `not_logged_in`、`expired` 或 `refresh_required`，按当前 CLI 提示完成登录：

```bash
atlas auth login
```

保留用户原有的账户和环境。不要因为供应商错误，替用户切换开发环境、其他账户或认证方式。需要诊断时使用：

```bash
atlas doctor --json
```

诊断结果也可能包含账户或机器信息。发布 issue 前只保留解决问题所需的字段，不上传密钥或完整凭据文件。

## 安装一个适合当前宿主的 Skill 入口

只选当前 Agent 对应的一条：

```bash
atlas skills install --agent claude
```

或者：

```bash
atlas skills install --agent codex
```

项目级目录可以显式指定，路径须与你的宿主实际配置相符：

```bash
atlas skills install --dir .claude/skills
```

这只是将 Atlas 入口写到相应的 Skill 目录，不会自动替其他客户端完成 MCP 配置。出现已有文件冲突时先看差异，不要删除别人的 Skill。随后启动新会话，再验证：

```bash
atlas skills read atlas --raw
```

如果当前二进制没有这些命令，按自己的安装渠道更新，再重新检查；不要把教程中的命令名改成猜测的近义词。

## 发给 Agent 的第一句话

> 请检查我的 Atlas 是否可以使用。先确认 CLI 版本、当前本地认证状态和 Atlas Skill 是否可读；需要登录时由我完成授权。保留我的账户与环境，不读取或显示令牌，不上传文件，不调用付费模型。最后告诉我已验证的部分和仍未验证的部分。

## 怎样算完成

能够确认版本；本地认证状态清楚；Skill 正文可读；Agent 能解释下一次任务会先查询模型能力。到这里仍然没有证明任何模型成功生成过内容，这很正常。下一篇再完成第一张图片。

常见误区是把“Skill 已安装”“CLI 已登录”“模型可用”当成同一个状态。记录三者，可以少走很多排错弯路。


运行路径、授权与状态约定见 [通用执行说明](../common/EXECUTION.md)。
