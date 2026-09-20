# 16｜一套素材输出不同渠道尺寸，不拉伸原图

本次把一张获批素材输出为横版、方形和竖版。目标是在不同槽位保留主体与文字，不把原图拉伸成任意尺寸。三个尺寸是教学规格，不代表平台当前要求。

## 先区分三种操作

contain 等比缩小到框内，再补边，适合不允许丢信息的截图和产品图；cover 等比填满后裁掉边缘，适合背景；重新构图需要回到生成或设计步骤，适合原主体与目标画幅明显不兼容的情况。补边不是生成式扩图，扩图也不能保证新区域真实。

## 复制给 Agent

> 把获批素材导出横版1600×900、方形1080×1080、竖版1080×1920三种版本。先分析主体和文字所在区域。能安全裁切就裁切，不能裁切就补边或给重新构图方案，不拉伸。不调用新的模型，除非我明确批准重构图。

## 执行两种确定性导出

```bash
python3 scripts/media_ops.py fit-image --inputs assets/approved.png \
  --output tutorial-output/sizes/landscape.png --width 1600 --height 900 --mode cover
python3 scripts/media_ops.py fit-image --inputs assets/approved.png \
  --output tutorial-output/sizes/square.png --width 1080 --height 1080 --mode contain
python3 scripts/media_ops.py fit-image --inputs assets/approved.png \
  --output tutorial-output/sizes/portrait.png --width 1080 --height 1920 --mode contain
```

脚本按中心裁切，不能自动找到人脸或产品。主体偏左或边缘有文字时先检查，不要把命令成功等同于构图正确。补白版本适合做排版底稿；透明素材需要单独保留 alpha 的处理链，本包的白色补边会改变背景。

## 文字后加

带标题的宣传图最好保存无字底图和可编辑标题层。先确定画幅再排文字，避免小图中标题太小或被裁掉。真实截图需要像素可读性，不能为了填满画幅把文字放到看不清。遇到密集信息，应减少图内信息或单独制作竖版布局。

## 质量检查

逐张读取宽高，打开最终文件，检查主体、logo、字幕区、安全留白与边缘。不同图像格式的透明和压缩特性不同，转换后再查看；扩展名不是格式证明。上传到实际渠道后检查平台二次裁切与压缩，必要时保留针对该渠道的派生版本。

## 交付与恢复

为三张文件写明用途与处理方法。某一张失败只重做对应派生图，母版保持不变。原分辨率不足时说明放大只是改变采样数量，不能声称新增的像素恢复了真实细节；需要超分或重生成再取得批准。

## 依据与复现范围

依据：[S5、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
