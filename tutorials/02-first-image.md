# 02｜生成第一张图片，同时保存任务回执

本教程的目标是一张实际可打开的图片，以及能再次查询它的任务 ID。演示主题是网站的抽象配图，不使用参考文件，也不要求模型生成标题文字。

准备好 Atlas CLI、可用账户和 Python 3.9+。从本教程包根目录执行 Bash 示例。所有模型 ID 必须从当前目录复制；本教程不预设某个旧 ID 永久可用。

> 状态：正文已完成；未执行线上付费生成或宿主实连。依据：[S1 / S2 / S3](../SOURCES.md)。本地测试范围见 [验证报告](../verification/REPORT.md)。

## 给 Agent 的任务说明

> 用 Atlas 为一个开发者工具网站生成一张抽象配图，画面有清楚的主体与留白，不包含文字和 logo。先查询支持文本生成图片的模型，给出一个选择及依据，核对参数并估价。只预览，不提交，等我确认后生成一张。保存原任务 ID，交付时给出真实文件；等待超时不要重新生成。

## 手动执行：先选模型

```bash
set -euo pipefail
atlas version --json
atlas auth status --json
atlas models list --type image --json
```

选择支持文本生成图片的模型，确认所需参数。不要选择必须带参考图的编辑模型：

```bash
MODEL='替换为当前可用的真实模型ID'
atlas models get "$MODEL" --json
atlas skills read atlas/references/image.md --raw
```

如果 schema 需要 prompt 以外的字段，应先补齐。例子里的主题没有尺寸硬约束，可以使用该模型的默认尺寸；需要具体画幅时，再按模型实际支持的字段和取值填写。

## 预览与估价使用同一组输入

```bash
PROMPT='Abstract visual for a developer tool website. One clear sculptural subject, soft studio lighting, ample clean negative space. No text, no letters, no logos.'
INPUT=(-p "$PROMPT")

# 有其他必填字段时，先按真实 schema 加入 INPUT，再执行下面两条。
# 例如语法是 INPUT+=(--param "字段名=实际值")，不要原样使用这个占位表达。
atlas generate image "$MODEL" "${INPUT[@]}" --explain --json
atlas generate cost image "$MODEL" "${INPUT[@]}" --json
```

检查预览里的模型、输入与默认值。估价失败或价格不明确时，不要拿零费用代替未知；先说明不确定性。本文把“确认后执行一张”作为示范授权边界，它不是服务端硬额度设置。

## 用户确认后，提交一次并保留回执

下方会产生真实模型调用费用。先确认数量与配置符合授权，再执行。目录只在第一次创建；出现异常后不要从创建新目录开始重新跑一遍。

```bash
mkdir -p tutorial-output
RUN_DIR=$(mktemp -d './tutorial-output/image-XXXXXX')
printf '%s\n' "$MODEL" > "$RUN_DIR/model.txt"
printf '%s\n' "$PROMPT" > "$RUN_DIR/prompt.txt"
printf '本次记录目录：%s\n' "$RUN_DIR"

if [ -e "$RUN_DIR/submit.json" ]; then
  printf '%s\n' '已有提交记录，请查询原任务，不要再次提交。' >&2
  exit 1
fi

if ! atlas generate image "$MODEL" "${INPUT[@]}" --no-wait --json > "$RUN_DIR/submit.json"; then
  printf '%s\n' '提交返回异常。保留回执，先核对是否受理，不要自动重试生成。' >&2
  exit 1
fi

PREDICTION_ID=$(python3 scripts/receipt_id.py "$RUN_DIR/submit.json")
printf '%s\n' "$PREDICTION_ID" > "$RUN_DIR/prediction-id.txt"
printf '任务 ID：%s\n' "$PREDICTION_ID"
```

辅助脚本只从已知 CLI 字段读取 ID；不把状态为 processing 的任务当成完成，也不会自行发网络请求。空回执、损坏 JSON 或缺少 ID 都需要核对，不能证明请求没有受理。上面的本地文件检查也不是跨进程幂等保证。

## 等待和交付

```bash
atlas generate wait "$PREDICTION_ID" --timeout 10m --json > "$RUN_DIR/result.json"
```

`10m` 是这次本地等待的上限，不是视频或图片预计完成时间。等待返回后同时看命令退出状态和 JSON 中的 prediction 状态。结果处于处理中时，继续查询同一个 ID。

完成后检查 `outputs` 与 `saved_files`。未指定输出路径时，让 CLI 使用实际媒体类型选择扩展名；不要看到 URL 末尾就猜本地文件名。打开 `saved_files` 中的真实路径，确认文件非空并检查画面。不具备图片查看能力时，应明确“只验证了文件，未做视觉检查”。

最终交付说明至少写清：模型 ID、任务 ID、生成状态、真实文件路径、画面是否已经人工或视觉检查。远程完成但没有本地文件时，进入 [43 恢复教程](43-recover-job.md)。

## 不要把日志与素材混进公开仓库

建议将生成目录加入项目已有的 `.gitignore`。不要覆盖整个文件，只追加所需规则。prompt、文件路径、输出 URL 和模型回执也可能包含业务信息，应与密钥一样谨慎审查后再分享。


运行路径、授权与状态约定见 [通用执行说明](../common/EXECUTION.md)。
