# 19｜让一张图片动起来：生成、续查与视频验收

本教程从一张可用参考图生成一个短镜头。先做单镜头，可以把问题限制在主体保持、运动和实际视频规格上，不必同时调试分镜、配音与拼接。

示例目标是 5 秒竖屏镜头。选择模型时必须确认它确实支持相应参考输入、时长和画幅；不支持时应换成经过用户同意的目标或模型，而不是无声丢掉要求。

> 状态：正文已完成；未执行线上付费生成或宿主实连。依据：[S1 / S2 / S3](../SOURCES.md)。本地测试范围见 [验证报告](../verification/REPORT.md)。

## 给 Agent 的任务说明

> 使用 Atlas，把这张参考图做成一个 5 秒竖屏镜头。镜头缓慢推进，主体保持稳定，不改变产品外形和文字。先查图生视频模型与 schema，说明音频支持情况、实际参数和费用认知；不先上传或提交。等我确认后生成一次，保存任务 ID，最后检查真实视频的时长、画幅、运动和声音。超时后继续原任务。

## 手动路径：先确认模型和素材

```bash
set -euo pipefail
REFERENCE='./assets/reference.png'
test -s "$REFERENCE"
atlas models list --type video --json
MODEL='替换为支持本次图生视频要求的真实模型ID'
atlas models get "$MODEL" --json
atlas skills read atlas/references/video.md --raw
```

找不到与要求相符的模型时应停在这一步。不要拿文本生视频模型假装已经使用了参考图。

在确认 `--image`、5 秒、9:16 可由当前 CLI 与模型接受后，构建输入：

```bash
PROMPT='A single continuous shot based on the reference image. Slow camera push-in. Keep the main subject stable and preserve the product geometry and visible markings. Subtle natural motion, no scene cut.'
INPUT=(-p "$PROMPT" --image "@$REFERENCE" --duration 5 --aspect-ratio 9:16)
atlas generate video "$MODEL" "${INPUT[@]}" --explain --json
```

分辨率和音频参数应按真实 schema 加入同一 INPUT。不要假设视频一定有声音，也不要把“提示词要求没有声音”当成关闭音频生成参数的替代。费用估算复用同一输入；本地参考与 URL-only 报价的限制见教程 13。

## 授权后提交一次

下方是付费步骤，只用于首次提交：

```bash
mkdir -p tutorial-output
RUN_DIR=$(mktemp -d './tutorial-output/video-XXXXXX')
if ! atlas generate video "$MODEL" "${INPUT[@]}" --no-wait --json > "$RUN_DIR/submit.json"; then
  printf '%s\n' '提交结果需要核对；不要重新运行本生成块。' >&2
  exit 1
fi
PREDICTION_ID=$(python3 scripts/receipt_id.py "$RUN_DIR/submit.json")
printf '%s\n' "$PREDICTION_ID" > "$RUN_DIR/prediction-id.txt"
printf '任务 ID：%s\n' "$PREDICTION_ID"
atlas generate get "$PREDICTION_ID" --json
```

随后继续这个任务：

```bash
atlas generate wait "$PREDICTION_ID" --timeout 10m --json > "$RUN_DIR/result.json"
```

本地等待结束不等于服务端失败。`10m` 仅限制这一轮等待；无论超时还是终端中断，都不要靠重复生成来“再等一下”。

## 技术规格与内容分开检查

从 `saved_files` 找到实际保存的视频路径。已安装 ffprobe 时可检查容器和媒体流：

```bash
VIDEO='替换为 saved_files 中的真实视频路径'
test -s "$VIDEO"
ffprobe -v error \
  -show_entries format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate \
  -of json "$VIDEO"
```

检查实际时长、宽高关系与是否有音频流。这个命令读取媒体信息，不能证明全片都能正常解码，更不能证明动作自然或口型同步。正式交付还应完整播放，必要时加全片解码检查。

内容检查应回答：是否采用了参考主体，是否出现形变或标识漂移，运动是否符合要求，有没有意外切镜或不需要的声音。对未达标部分如实记录；不能只截一张好看的首帧当作视频通过验收。

## 交付清单

交付真实视频文件或远程链接、模型与任务 ID、实际规格、视觉与声音检查结果。下载失败只恢复下载；动作未达标才涉及新的生成决策。二者不要混在一起。


运行路径、授权与状态约定见 [通用执行说明](../common/EXECUTION.md)。
