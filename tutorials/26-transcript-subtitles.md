# 26｜从录音得到转写和字幕，检查时间轴

从录音得到“可读文本”和得到“能同步播放的字幕”，是两项交付。字幕还需要可靠时间戳、分句和人工复核。本教程先检查 ASR 返回能力，再把实际结果转换为 SRT，不通过平均分配时长伪造对齐。

## 准备与首次请求

确保录音有合法使用范围，尤其是客户会议和个人语音。先检查音轨、实际时长、文件大小，再查询语音识别模型允许的语言、格式、长度与输入字段。Atlas 的 `atlas_transcribe_audio` 用于转写，但所选模型是否返回逐字或逐段时间戳，需要读取当前 schema 和结果说明。

> 请用 Atlas 转写这段已获授权的录音。先查 ASR 模型是否支持本次语言和带时间戳输出，说明上传、费用与限制，不先提交。授权后保留原任务 ID，先交付原始转写；只有获得可靠时间戳时才制作 SRT。遇到不清楚的人名标注待核对，不补写听不见的内容。

远程服务不能读取你机器上的 `/Users/...`。本地 MCP 上传需要你允许外发；已有授权 URL 则作为所选模型规定的音频输入。生成工具里的 `params` 结构也不等于本包 `run_job.py` 的配置或 REST 请求体。

## 将真实结果转换到中间结构

本包用数组存放 `start`、`end`（单位秒）和 `text`。这是教学中间结构，不声称 Atlas 每个 ASR 都返回这个结构。把实际 ASR 返回结果按其说明转换，保留原始响应以便追溯。示例文件 [segments.json](../examples/subtitles/segments.json) 是手写测试数据，没有经过真实转写。

```bash
mkdir -p tutorial-output/subtitles
python3 scripts/subtitles.py from-json \
  --input examples/subtitles/segments.json \
  --output tutorial-output/subtitles/demo.srt --duration 4
python3 scripts/subtitles.py lint \
  --input tutorial-output/subtitles/demo.srt --duration 4
```

换成你的结果时，`--duration` 使用实际录音时长。脚本检查非负时间、结束晚于开始、顺序、重叠和越界；不会判断一句话对应哪段声音，也不会自动修正错字。双人同时讲话等确需重叠的材料，人工检查后再使用 `--allow-overlap`。

## 没有时间戳时怎么继续

可以先交付带“未对齐”标记的文本，再使用经过核实的对齐工具或人工标点时间轴。不要按字数均分整段音频，并声称已完成同步字幕。对于长录音，先读 [30 分段教程](30-long-recording.md)，明确模型时间戳相对片段还是相对原音频。

## 字幕内容与显示检查

专有名词按原始录音核对，不能用“读起来通顺”替代听证。逐句回放开头、中间和结尾，确认提示没有提前剧透、字幕消失时间合适、句子没有越过镜头或说话人变化。必要时分行，但不要在本来连续的专名中间断开。

将字幕叠加到预览视频后再检查字号与遮挡，见 [34](34-subtitles-logo-outro.md)。字幕 lint 通过只代表结构合规；中文缺字、遮住产品、时间对不上都仍然可能发生。

完成后交付 `transcript.txt`、真实时间戳结构、`captions.srt`、不确定词清单和转写任务 ID。保留审校前后版本；录音不清的地方用明确标记，不编造补全。

## 依据与复现范围

依据：[S3、S5、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
