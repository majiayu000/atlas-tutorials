# 25｜把脚本生成配音，检查数字、专有名词与停顿

本篇交付一段可听的配音、最终口播稿，以及数字和专有名词检查记录。先把内容审定，再合成声音；否则每次改一个产品名称，都可能需要重新付费。示例文本使用虚构品牌，不克隆任何人的声音。

## 准备文稿与声音要求

将口播稿保存为 UTF-8 文本，写清语言、情绪、目标时长和使用场景。把“3.5”“2026”“API”“DeskLight”等读法另记在 [发音表](../examples/briefs/pronunciation.md)。界面显示文案与实际发音文本可以不同，但不要擅自改动事实、金额、单位或人名。

目标时长是验收条件，不是所有 TTS 模型都有的参数。先用实际稿件读一遍，再决定删字、拆段或调整停顿；不要为了塞进十秒把声音加速到无法听懂。

## 复制给 Agent

> 用 Atlas 为我的已审定文稿制作普通合成配音，使用当前可用且适合中文的标准声音，不克隆真人。先查询 TTS 模型、语言、voice 和输入字段，预览完整请求与费用认知。等我确认后生成一次，保留任务 ID。交付音频、实际时长、数字和专有名词的逐项听检结果；未听检的部分明确标注。

## 选择 TTS，而非音乐或转写模型

CLI 支持音频命令的安装版本可以先执行：

```bash
atlas version --json
atlas models list --type audio --json
MODEL='替换为目录中的TTS模型ID'
atlas models get "$MODEL" --json
atlas skills read atlas/references/audio-3d.md --raw
```

同属 audio 不代表用途相同。核实模型用途是文本转语音，查看文本字段究竟叫 `text` 还是其他名称，voice 是枚举、ID 还是可选默认值。不把音乐模型当作配音模型。如果当前 CLI 没有该命令，转到已连接 MCP 的 `atlas_list_models`、`atlas_get_model_info` 与 `atlas_generate_audio` 路线，不猜命令别名。

复制 [图片配置](../examples/config/image.json) 为你自己的 `voice.json`，将 `kind` 改成 `audio`，填入真实模型与已核对的参数，删除不适用的 prompt。该配置是本包脚本输入，不是服务端原生请求体：

```bash
python3 scripts/run_job.py prepare --config voice.json --run-dir tutorial-output/voice-01
python3 scripts/run_job.py preview --run-dir tutorial-output/voice-01
```

只有确认本次费用与上传范围后，执行付费步骤：

```bash
python3 scripts/run_job.py submit --run-dir tutorial-output/voice-01 --approve
python3 scripts/run_job.py wait --run-dir tutorial-output/voice-01
```

## 对照文稿逐句听

先用 `media_audit.py` 读取时长和音轨，再完整播放。数字、单位、缩写、品牌、人名各听一遍；注意句末是否被截断、词间是否出现不自然停顿、情绪是否偏离使用场景。机器转写回听可以辅助发现漏词，但不是正确发音的证明，额外转写同样可能计费。

```bash
python3 scripts/media_audit.py ./assets/voice.wav --require-audio --decode
```

路径需要替换成实际文件。若只发现一句读音错误，先修改对应短段并获得必要授权，重新生成该段后再合成。不要让 Agent 为比较几十个声音自动连续下单。提交过且正在处理的音频仍应续查原 ID。

交付采用真实输出格式，不把 MP3 改名为 WAV。保存原始音频、最终稿、模型/voice 选择和听检结论；客户稿件不要混入公共示例。

## 依据与复现范围

依据：[S1、S2、S3、S5](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
