# 集成示例的边界

这些文件已做静态结构检查，未向 n8n、ComfyUI 或 GitHub Actions 在线导入联调。不是已发布集成认证。

`n8n-submit-poll.json` 根据 Atlas 官方公开示例的节点类型和参数形状编写，模型与凭据故意留作不可用占位。导入后从实际下拉框重选模型、补必填项，检查状态字段。工作流未激活不代表点击 Test 不收费；Test 也会执行提交。

`comfyui-image.json` 对照官方单图示例，依赖具体的 Nano Banana Pro 节点类型；不是所有模型通用图。无 API key，导入后需确认节点版本、模型可用性和费用。填写 key 后不要导出分享原工作流，也要检查图片中的工作流元数据。

`manual-generation.yml` 是示例 GitHub Actions，仅允许私有仓库 main 手动触发，execute 默认 false。需要复制到受控仓库并配置 environment 审批者与密钥。JSON 中的业务参数必须先核实，prepare/preview 不等于在线报价。使用 Node REST 示例便于避免安装二进制；CLI 集成可以使用同样的回执策略。第二次 rerun 不自动再次提交；新建 workflow run 仍可能是新计费任务。

节点示例的结构依据与 blob 版本见 SOURCES 的 S11/S12。业务文案、占位和教学说明为本包新增。上游许可证文本放在 `third-party/`，不代表任何宿主在线兼容保证。
