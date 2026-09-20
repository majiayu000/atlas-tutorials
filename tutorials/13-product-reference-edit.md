# 13｜给产品图换场景，同时检查包装与 logo

目标是将一张你有权使用的产品照片放进新的场景，同时尽可能保持产品形状、包装、文字和 logo。模型对这些细节的保持不是保证；教程的最后必须检查实际图片，不能只相信提示词里的“不要改变”。

准备一张清晰产品图。可读标签、合适的拍摄角度与完整外形，比给一张模糊截图堆叠约束更容易检查结果。不要上传未获授权的客户资料或保密样品。

> 状态：正文已完成；未执行线上付费生成或宿主实连。依据：[S1 / S2 / S3](../SOURCES.md)。本地测试范围见 [验证报告](../verification/REPORT.md)。

## 复制给 Agent

> 用 Atlas 编辑我提供的产品照片。把背景换成浅色工作台和自然窗光，保留产品外形、包装颜色、全部可见文字与 logo，不添加新卖点或标识。先确认图片可读、查询参考图编辑模型和 schema，展示输入及费用认知，暂不上传或提交。等我同意后只生成一个版本；完成后与原图比较，指出变形或文字不一致的地方。

这里让 Agent 先停止在预览阶段，因为上传本身也是数据外发，需要与生成一起说明。已明确授权上传与生成的工作流可以合并交互，但不能把“先估价”解释成允许发出素材。

## 把保留项写成能检查的要求

用具体描述替代“品牌保持一致”。例如瓶身长宽比例不能明显改变；盖子颜色不变；正面标签保持原来位置；不新增容量、功效或认证文字。对文字准确性有硬要求时，准备好使用原图抠图、背景生成与合成的替代路径，而不是无限重抽。

## CLI：确认真实输入文件和模型

从教程包根目录开始，在同一 Bash 会话操作：

```bash
set -euo pipefail
REFERENCE='./assets/product.png'
test -s "$REFERENCE"
atlas models list --type image --json
MODEL='替换为支持参考图编辑的真实模型ID'
atlas models get "$MODEL" --json
atlas skills read atlas/references/image.md --raw
```

只有模型支持相应单图输入时才用下面的 `--image`。多参考模型可能需要 `--images` 或 schema 专用字段，不要把图片路径直接塞进 prompt 当作已经上传。

```bash
PROMPT='Edit the provided product photo. Change only the surrounding scene to a light worktable with natural window light. Keep the product geometry, packaging colors, visible label text and logo unchanged. No new claims, labels or objects on the product.'
INPUT=(-p "$PROMPT" --image "@$REFERENCE")
atlas generate image "$MODEL" "${INPUT[@]}" --explain --json
```

## 费用估算遇到本地参考图怎么办

`--explain` 不上传文件；`generate cost` 同样不会为了估价上传本地参考。若模型的报价输入要求已有 HTTP(S) URL，而目前只有本地文件，就不能把删掉参考图后的报价当成这次编辑的准确费用。

可以使用已经获授权上传且仍有效的素材 URL 估价，或先解释为何报价不完整，再由用户决定是否授权下一步。不要为了让 cost 成功而偷偷把图片传到第三方图床。也不要把同模态另一个模型的价格当成本次报价。

## 经授权后执行与验收

与教程 02 一样，提交一次、保存回执、继续同一个 ID。下面会产生生成费用，并可能按模型要求上传参考图：

```bash
mkdir -p tutorial-output
RUN_DIR=$(mktemp -d './tutorial-output/product-XXXXXX')
if ! atlas generate image "$MODEL" "${INPUT[@]}" --no-wait --json > "$RUN_DIR/submit.json"; then
  printf '%s\n' '保留回执并核对受理结果，不要自动重新生成。' >&2
  exit 1
fi
PREDICTION_ID=$(python3 scripts/receipt_id.py "$RUN_DIR/submit.json")
printf '%s\n' "$PREDICTION_ID" > "$RUN_DIR/prediction-id.txt"
atlas generate wait "$PREDICTION_ID" --timeout 10m --json > "$RUN_DIR/result.json"
```

执行块只用于第一次提交。故障后不要重复运行它，转到 [恢复教程](43-recover-job.md)。

检查 JSON 的任务状态和 `saved_files`，再打开原图与生成图对比。至少核对外形、包装颜色、文字/logo、背景边缘四项。不具备视觉检查能力时，明确标记等待人工确认。

如果背景成功但标签变了，结果应写“背景已完成，标签保真未达标”，不能写“全部保持一致”。保存失败样例，让用户决定局部修复、原图合成或一次新的生成。新尝试需要计入原有预算与授权范围。

## 最终交付

交付编辑图、原始参考图标识、模型与任务 ID、通过与未通过的保留项。不强制复制原始客户照片到公共素材目录；对外演示时另用可公开的参考素材。


运行路径、授权与状态约定见 [通用执行说明](../common/EXECUTION.md)。
