# 20｜把三段产品镜头剪成一条完整短广告

本篇把三段各5秒的获批产品镜头剪成15秒短广告。输入来自你已经完成的生成或拍摄；本地剪辑不产生模型费用。最终交付应有一个完整 MP4、字幕与审核记录，不能只给三段链接。

## 先确认时间线

使用 `examples/briefs/product-ad.md` 的三镜头练习：全貌、材质、使用场景。每段都应通过产品保真审核。逐段核对时长与画幅；少于5秒的镜头不能悄悄冻结末帧补足而不说明，长度多出的镜头则根据剪辑决定裁切位置。

## 复制给 Agent

> 把已批准的三个产品镜头剪成15秒竖屏短广告，不重新生成。先检查每段时长、画幅和产品一致性，再统一视频规格。保留无字幕母版，另外添加我确认的字幕与配音。不要编写新卖点；原音轨是否保留先告诉我。

## 统一规格再拼接

```bash
python3 scripts/media_ops.py concat \
  --inputs assets/shot-01.mp4 assets/shot-02.mp4 assets/shot-03.mp4 \
  --output tutorial-output/ad/picture-master.mp4 --width 1080 --height 1920 --fps 30
```

此工具会先把各镜头转成相同的画幅、帧率与编码，再拼接；为了后续统一声音，输出故意不含原音轨。不要用它保存有价值的对白；那种项目应在编辑器中逐轨管理。本地转码可能重复/丢弃帧来形成目标帧率，不能把它写成运动质量提升。

## 添加声音和字幕

```bash
python3 scripts/media_ops.py mix-audio \
  --inputs tutorial-output/ad/picture-master.mp4 assets/voice.wav assets/music.wav \
  --output tutorial-output/ad/with-audio.mp4 --music-volume 0.10
python3 scripts/subtitles.py lint --input assets/ad.srt --duration 15
python3 scripts/media_ops.py burn-subtitles --inputs tutorial-output/ad/with-audio.mp4 \
  --subtitles assets/ad.srt --output tutorial-output/ad/final.mp4
```

mix-audio 按视频时长补静音或裁音频；过长旁白会被截断，因此应先确认稿件时长，不能用该命令解决朗读过长。背景音乐大小是示例值，必须听审。字幕字号与位置也要在实际竖屏预览中确认。

## 验收整片

```bash
python3 scripts/media_audit.py tutorial-output/ad/final.mp4 \
  --decode --width 1080 --height 1920 --duration 15 --require-audio \
  --output tutorial-output/ad/audit.json
```

技术检查后完整播放，检查切点、产品变化、字幕、声音突变和最后一个字是否完整。报告生成与后处理的各自状态，明确字体与音轨来源。

## 故障恢复

拼接失败只修视频规格，字幕乱码只修本地渲染环境；缺一个镜头再恢复该镜头任务。不要因为最后的 MP4 没导出就让 Agent 把前三个付费镜头全部重做。交付无字幕母版、最终版和分离音轨，便于后续本地化。

## 依据与复现范围

依据：[S2、S5、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
