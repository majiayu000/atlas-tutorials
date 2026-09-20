# 10｜给应用制作一套 onboarding 插图

本次为应用做三张引导插图，分别表达“创建项目”“添加素材”“导出结果”。这三张图要像同一套，而不是三个模型各画各的。交付含原图、统一尺寸文件和一张并排审核记录。

## 先固定视觉规则

确定背景、线条或材质、视角、主角、阴影方向、构图密度与留白区。每个页面只有一个主动作。不要用图像模型画真实按钮文字或完整交互截图，引导标题应由应用组件渲染。

## 复制给 Agent

> 用 Atlas 为应用做三张 onboarding 插图：创建项目、添加素材、导出结果。使用同一风格、同一角色和统一留白，不绘制真实按钮或文字。先制作第一张作为母版，等我认可后用它指导另外两张。逐张检查角色外形、视角、配色和内容，不因其中一张失败重做整套。

## 从母版走到系列

第一张只做风格决定，不急于批量。批准后保存母版和提示词的固定部分。后两张仅改变主动作。模型支持参考图时按实际 schema 附母版；不支持时明确采用文本风格约束，承认一致性需要更严格的人工检查。不同画面使用同一个 seed 并不自动获得同一角色。

## 导出统一尺寸

```bash
python3 scripts/media_ops.py fit-image --inputs assets/onboarding-01.png \
  --output tutorial-output/onboarding/01.png --width 900 --height 900 --mode contain
python3 scripts/media_ops.py fit-image --inputs assets/onboarding-02.png \
  --output tutorial-output/onboarding/02.png --width 900 --height 900 --mode contain
python3 scripts/media_ops.py fit-image --inputs assets/onboarding-03.png \
  --output tutorial-output/onboarding/03.png --width 900 --height 900 --mode contain
```

这组尺寸仅用于练习。图片若需要透明背景，先确认真实 alpha，不能把白底看成透明；本包 contain 会补白，不适合假装输出透明图。需要 alpha 的项目选择支持透明的来源或单独抠图工作流。

## 在真实页面验收

并排看三张图的主体大小与视觉重量，再逐页检查小屏幕、动态字体和不同语言。插图不能承担唯一的操作说明，页面标题应独立清楚。用不认识应用的同事测试其是否能解释每张图表达的动作。

## 故障与交付

某张角色换了衣服或材质跑偏，只重做该张并继续引用母版。留白不够可调整页面或图像构图，不能缩小标题到无法阅读。交付文件与固定风格规则一起保存，以后新增第四张时有可复用依据。

## 依据与复现范围

依据：[S1、S2、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
