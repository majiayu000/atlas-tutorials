# 资料依据与核对范围

编写/核对日期：2026-09-20。以下链接是原始资料，不代表在线集成或付费模型测试。会变化的模型能力、价格、节点和认证路径，执行前仍须核对。正文中的脚本、JSON 中间格式、审批记录是本包教学约定。

## S1 · 公开 CLI 与 Agent 上手指南

[AtlasCloudAI/cli](https://github.com/AtlasCloudAI/cli)；[AGENT_QUICKSTART.md](https://github.com/AtlasCloudAI/cli/blob/main/docs/AGENT_QUICKSTART.md)，核对 blob `ba530452cc741093ab9b9d341ad6af5a2bcff96c`。用于安装、认证状态、Skill 入口、结果和续查说明。公开首页与维护源码可能不同步，最终以安装版本的 help、内置指南和实际账户为准。

## S2 · 与安装版本绑定的 CLI 操作指南

已核对维护中的 image/video/troubleshooting 操作规则，正文不随包分发私有源码。用户通过安装的 CLI 读取本机实际版本：

```bash
atlas skills read atlas --raw
atlas skills read atlas/references/image.md --raw
atlas skills read atlas/references/video.md --raw
atlas skills read atlas/references/troubleshooting.md --raw
```

用于 --explain/cost 的无上传边界、ID 字段差异、saved_files 和不重复提交规则。源码已有音频/3D 命令不保证每个历史发布都包含。

## S3 · 独立 MCP 服务

[README](https://github.com/AtlasCloudAI/mcp-server/blob/main/README.md)，blob `c5dba8c12aae382c9715858d7f71e115e5f9e978`；[图像工具](https://github.com/AtlasCloudAI/mcp-server/blob/main/src/tools/image.ts)，blob `da7a00469e510e9eb38d041052a66a4a0a18c0d9`。用于本地 stdio、API key、模型发现、生成/音频/转写/3D、上传与历史说明。它不是插件远程 OAuth 接入文档。实际 MCP 返回常为 text 内容，不套用 CLI 根 JSON 字段。

## S4 · 原配方目录

[Recipe Library](https://github.com/AtlasCloudAI/atlas-cloud-skills/blob/main/library/README.md)，blob `53c1ad6f993cf1fda23a6b64a6bc682f31eb5ca5`。用于对照已有 visual/motion/edit/social 配方，长教程在其任务范围上补执行、验收与恢复，而不是声称全部选题首次出现。

## S5 · ffprobe

[FFmpeg ffprobe 文档](https://ffmpeg.org/ffprobe.html)。用于媒体流/容器读取和 JSON 输出。元数据不等于全片解码，解码不等于内容质量审核。当前网页与本地 FFmpeg 版本可能不同，执行以本地功能为准。

## S6 · 已核对的媒体 REST 与异常语义

[api-client.ts](https://github.com/AtlasCloudAI/mcp-server/blob/main/src/services/api-client.ts)，blob `a2f411dcc6c52698e002302bd0ac16519dc87493`；[generation.ts](https://github.com/AtlasCloudAI/mcp-server/blob/main/src/services/generation.ts)，blob `b061dd0fb36d5ef4db570d97127b8c392c00bc46`。

用于媒体 endpoint、展平请求体、response.data.id、POST 不自动重试及非 2xx 可能携带终态的说明。源码在模型 schema 无法获取时有跳过校验的路径，因此教程不能无条件承诺 dry_run 完整验证。没有由这些文件证明通用 webhook 参数或服务端硬预算。

## S7 · FFmpeg 本地后处理

[官方滤镜文档](https://ffmpeg.org/ffmpeg-filters.html)，涉及 scale/pad/crop、overlay、subtitles、amix、apad、atrim 与 alimiter；[ffmpeg 命令文档](https://ffmpeg.org/ffmpeg.html)。所附脚本只面向本地可信素材，尺寸、fps、增益均是教学参数，不是行业通用发布标准。静音拼接和替换音轨的语义在教程中明确说明。

## S8 · GitHub Actions

[手动触发](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)；[工作流语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)。用于 workflow_dispatch、inputs、permissions、job/step 配置与显式执行。示例不是已在用户仓库运行的 workflow。

## S9 · n8n 通用节点

[HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/)；[Wait](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.wait/)。n8n 自身能等待 webhook 不证明 Atlas 接口支持原生 webhook 回调。

## S10 · Node 内置 fetch

[Node globals / fetch](https://nodejs.org/api/globals.html#fetch)。随包示例使用 Node 标准库与 fetch，不宣称 Atlas 有同名官方 SDK。实际离线测试 runtime 版本见验证报告。

## S11 · Atlas n8n 节点与示例

[节点 README](https://github.com/AtlasCloudAI/n8n-nodes-atlascloud/blob/main/README.md)，blob `4880a2676dcf064c3760b747f0d820f620da78e4`；[异步示例](https://github.com/AtlasCloudAI/n8n-nodes-atlascloud/blob/main/workflows/03-async-video.json)，blob `e793f658f6d4fc603cfc4b8fac030909c30f93cb`。

用于 Task Submit / Task Status 节点类型、提交模式和 prediction_id 表达式。随包派生图故意无有效凭据、使用不可用模型占位，导入后必须重选实际字段。MIT 许可副本见 third-party。

## S12 · Atlas ComfyUI 节点与示例

[节点仓库](https://github.com/AtlasCloudAI/atlascloud_comfyui)；[单图示例](https://github.com/AtlasCloudAI/atlascloud_comfyui/blob/main/examples/01-text-to-image.json)，blob `c8b709bd662a617be13eec498b3af92543ba60c8`。用于具体三节点结构与插槽类型，不作为所有模型可用性的证据。随包图去掉可用凭据并替换业务 prompt，保留上游许可和来源。

## S13 · glTF 验证

[Khronos glTF Validator](https://github.khronos.org/glTF-Validator/)。用于结构合规检查，不证明网格外观、物理尺度、制造或实时渲染性能。本次 Blender 官方手册页面读取失败，故教程不依据它声称某个版本的确定菜单、快捷键或导出选项；导入导出按实际安装工具验证。

## S14 · 本包原创设计与测试

run_job、Node 客户端、本地审批样例、回执目录、盲评与验收约定是本次设计建议；不是已有平台特性。离线测试日志见 verification。本地防重提不等于服务端 exactly-once，也不等于跨账户硬额度。评测建议描述方法，不包含伪造效果或收益数据。

## S15 · Agent Skills

[Agent Skills 规范](https://agentskills.io/specification)。用于 SKILL.md、name/description 与按需 references 的结构。宿主发现路径与实际能力要另行核实；包内样例及 expected 测试案例不代表特定 Agent 已实测通过。

## S16 · Open Graph

[Open Graph protocol](https://ogp.me/)。用于网页分享元数据 og:title/type/image/url 等。教程的 1200×630 等尺寸是项目示例，不是协议唯一强制尺寸。
