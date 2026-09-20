# 34｜给生成视频加字幕、logo 与片尾

本教程把字幕、logo 和片尾作为确定性后期，叠到已经通过检查的视频上。文字由审定文案和排版工具生成，不要求生成模型逐字写出商标或字幕。准备母版 MP4、UTF-8 SRT、有使用权的透明 logo 和片尾画面。

## 固定交付规格

先确定分辨率、帧率、字幕字号、安全区、logo 显示位置与片尾时长。批准稿保存成文件，生成模型不应临时改写产品承诺。字幕、logo、片尾三步分别保存输出，这样可以只重做出错的阶段。

> 给这个已完成视频加上我提供的字幕、logo 和两秒片尾。保留原始内容和声音，不调用付费生成。先核对字幕时间与母版时长，再给出排版预览；检查中文缺字、品牌比例和遮挡，最后交付实际 MP4、外挂字幕与后期说明。

## 第一步：检查并烧录字幕

```bash
mkdir -p tutorial-output/post
python3 scripts/subtitles.py lint --input ./assets/captions.srt
python3 scripts/media_ops.py burn-subtitles --inputs ./assets/master.mp4 \
  --subtitles ./assets/captions.srt --font-size 24 \
  --output tutorial-output/post/captioned.mp4
```

FFmpeg 需要有 `subtitles` 滤镜/libass，系统还需可用的中文字形。本包不附带字体文件。执行成功也要看屏幕上是否出现方框；换用有授权且覆盖所需语言的本地字体，再确认画面。需要复杂样式时可用 ASS，并在自己的后期工具中验证，而非把 SRT 当成任意排版容器。

## 第二步：叠加 logo

下面以宽 160 像素、右下角留 40 像素为教学示例。先确认母版尺寸足够，logo 不压住字幕。输入须为你准备的图片，文件后缀不能代替真实透明通道。

```bash
ffmpeg -nostdin -n -i tutorial-output/post/captioned.mp4 -i ./assets/logo.png \
  -filter_complex '[1:v]scale=160:-1[logo];[0:v][logo]overlay=W-w-40:H-h-40[out]' \
  -map '[out]' -map '0:a?' -c:v libx264 -pix_fmt yuv420p -c:a aac \
  tutorial-output/post/branded.mp4
```

logo 是静态输入，overlay 默认重复其末帧。完整看一遍开头和结尾，确认不会消失、拉伸或挡住画面。上述位置不是平台强制安全区。

## 第三步：片尾与音轨

先按母版尺寸准备片尾图，再将它生成两秒静态视频；示例采用 1080×1920 和 30fps：

```bash
ffmpeg -nostdin -n -loop 1 -i ./assets/outro.png -t 2 \
  -vf 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1' \
  -r 30 -an -c:v libx264 -pix_fmt yuv420p tutorial-output/post/outro.mp4
python3 scripts/media_ops.py concat \
  --inputs tutorial-output/post/branded.mp4 tutorial-output/post/outro.mp4 \
  --output tutorial-output/post/with-outro-silent.mp4 --width 1080 --height 1920 --fps 30
```

注意：本包 concat 为降低轨道不一致问题，明确输出无声母版。**不能把这个文件直接当有声成片交付。**从原母版提取获授权的声音后，使用 [29](29-background-music.md) 的混音步骤恢复，并设计片尾两秒如何收音；也可以在可信编辑器里统一编排音频。字幕总时长必须适配新的片长，片尾不能被误认为漏字幕。

最终完整检查声音、字幕、logo、片尾和实际时长。分别交付原字幕与最终有声成片；单个阶段失败从上一文件继续，不重新生成画面。

## 依据与复现范围

依据：[S5、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
