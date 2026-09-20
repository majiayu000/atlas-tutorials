# 27｜给同一条视频制作多语言版本

目标是把同一条已审定视频做成多语言版本，同时保留事实、品牌和镜头意义。一个语言版本要经历翻译、配音、对齐、字幕和审核，不应只把中文稿扔给 TTS 后直接交付。

## 先锁定母版

确定画面剪辑、字幕是否烧录、原音轨能否分离，以及片中有没有不能重新使用的素材。保留无字幕母版和独立声音最方便；只有带字幕成片时，应说明旧文字残留和重新制作的限制。用术语表固定产品名、数字、单位与不得翻译的字符串。

> 基于这个已获授权的视频做英文和日文版本。保留画面中的产品事实和品牌，不增加功能或承诺。先交付两种语言的译稿和需要我确认的用语，暂不生成声音；确认后分别检查 TTS 支持，按授权生成。每个语言独立保存任务记录，交付视频、字幕、音轨和未完成的审校项。

## 翻译与口播稿分开管理

建立 `locales/en/` 和 `locales/ja/` 等独立目录，每个目录保存 `script.txt`、`pronunciation.md`、`voice`、`captions.srt` 和 `review.json`。这是项目目录约定，不是 Atlas locale 命令。翻译时明确语境、观众和语气；数字、币种和本地业务承诺需由业务负责人确认，不能由翻译模型顺手替换。

逐句对照母版镜头：画面在讲哪个功能，译稿是否还在说同一件事。回译可发现部分偏差，但不是母语审核的替代。对外发布的重要文案应由熟悉目标语言的人审校。

## 配音长度不等于字幕长度

按 [25](25-voiceover.md) 生成每种语言配音，并读取真实时长。如果声音比画面长，先缩短口播或调整镜头，而不是直接截断；如果更短，可保留呼吸停顿或调整对应片段。普通旁白本篇不承诺人物口型同步。

字幕应按该语言音轨重新对齐，不沿用中文时间戳强行塞入。按 [26](26-transcript-subtitles.md) 制作字幕，时间来自实际音轨或人工对齐。

```bash
python3 scripts/media_audit.py ./assets/master.mp4 --decode
python3 scripts/media_audit.py ./assets/voice-en.wav --require-audio --decode
python3 scripts/subtitles.py lint --input ./assets/captions-en.srt
```

上述路径为你准备的文件。确认配音不长于已批准的母版后，再做本地合成：

```bash
python3 scripts/media_ops.py mix-audio \
  --inputs ./assets/master.mp4 ./assets/voice-en.wav \
  --output tutorial-output/locales/en-vo.mp4
python3 scripts/media_ops.py burn-subtitles \
  --inputs tutorial-output/locales/en-vo.mp4 \
  --subtitles ./assets/captions-en.srt \
  --output tutorial-output/locales/en-final.mp4
```

`mix-audio` 会替换原音轨，并按画面时长裁切/补静音，必须先检查长度；它不会自动安排每句话落在哪个镜头。背景音乐可按脚本第三输入加入，不能因此重复叠入含原人声的音轨。

## 按语言独立验收与恢复

核对发音、字幕、货币与单位、文化语境、缺字和镜头对齐。英文通过不代表日文通过；某个语言失败时只处理该语言的相关步骤。交付每种语言的成片、字幕、干声和审校记录，明确哪些是机器翻译稿，哪些经过人工审校。

## 依据与复现范围

依据：[S3、S5、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
