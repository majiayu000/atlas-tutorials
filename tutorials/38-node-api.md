# 38｜把媒体生成功能接进 Node.js 项目

本篇提供一个不用第三方 SDK 的 Node.js REST 示例。它覆盖本地准备、单次提交和原任务查询，适合学习后端集成；它不是面向所有业务的生产 SDK，也不内置实时模型发现、报价、认证刷新或文件上传。

## 保持三种接口形状清楚

CLI 使用命令参数，MCP 生成工具常接收 `{model, params, dry_run}`，公开媒体 REST 的请求体则按所选模型使用展平字段。随包配置仍是 `{kind, model, params}`，客户端会编译为 `{...params, model}`，不把配置原封不动当 API 请求。

接口路径依据公开 MCP 源码核对：图像 `/api/v1/model/generateImage`、视频 `generateVideo`、音频 `generateAudio`；3D 使用图像路径并要求先核实模型能力；查询为 `/api/v1/model/prediction/{id}`。模型是否当前可用、必填项和价格仍需单独查询。

> 帮我用 Node 接入 Atlas 的媒体生成接口，先完成本地配置和假响应测试，不调用付费接口。密钥只保留在服务端，POST 不自动重试。上线后保存每次尝试、原始回执与任务 ID，浏览器只拿业务任务 ID；不要把服务端 API key 发给前端。

## 从可运行示例开始

文件在 [atlas-media.mjs](../examples/node/atlas-media.mjs)。推荐使用仍在维护的 Node 22 或更高兼容版本；脚本利用内置 fetch。准备经过 schema 核对的 `my-image.json`，先执行不联网的两个动作：

```bash
node examples/node/atlas-media.mjs prepare --config my-image.json --run-dir tutorial-output/node-001
node examples/node/atlas-media.mjs preview --run-dir tutorial-output/node-001
node --test tests/node-client.test.mjs
```

**这里的 preview 仅展示 REST 请求体，不等于 CLI 的在线 schema 编译，更不是 MCP dry_run 或报价。**测试使用注入的假 fetch，不读真实 API key、不发送网络请求。

授权后才让进程安全获取 `ATLASCLOUD_API_KEY`；不要写进代码、网页或 Git。下面是实际付费入口：

```bash
node examples/node/atlas-media.mjs submit --run-dir tutorial-output/node-001 --approve
node examples/node/atlas-media.mjs get --run-dir tutorial-output/node-001
node examples/node/atlas-media.mjs wait --run-dir tutorial-output/node-001 --seconds 120
```

与 Python 包装器相同，退出 3 表示仍在处理，2 表示错误/未知，4 表示远程失败。请求可能已经受理但响应丢失，不能据此自动再次 POST。`attempt.json` 永不自动清除。

## 认证、查询与下载的边界

示例固定请求源站并拒绝 HTTP 重定向，不会把 Authorization 附到输出 CDN URL。查询返回中的非 2xx 也可能描述终态失败，要读 task status；401/403 停止，不擅自换账号。GET 可继续查询，但不能沿用 GET 重试策略去重试付费 POST。

脚本不下载媒体。应用需要下载时，先核实结果来自对应任务，再使用不带 Atlas key 的受控下载器；限制来源、协议、重定向、大小和本地路径，不能向用户任意指定的内网 URL 发带凭据请求。

## 接入你自己的服务

浏览器调用你自己的业务接口，服务端将业务 ID 映射到 Atlas ID，数据库持久化账户、请求摘要和状态。只有所属用户能读该任务。使用队列处理长任务，并区分任务完成与产物保存。本文的本地目录教学方式不能替代多租户数据库、账务限制、审计和并发控制。

最小验收包括：请求体没有多余 params 包装、密钥未输出、一个操作只发一次 POST、非零 HTTP 返回中的任务 ID 不丢失、查询错误不更换账户。假响应测试通过后，再按明确授权做一项真实小任务联调，核对正式 API 的返回形状。

受理未知的请求进入核对队列，原任务成功只重试下载；这些流程在 [42](42-polling-webhook.md) 与 [45](45-unknown-submission.md) 继续展开。

## 依据与复现范围

依据：[S3、S6、S10、S14](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
