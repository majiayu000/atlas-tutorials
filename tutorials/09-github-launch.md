# 09｜给 GitHub 项目制作 README 横幅和发布配图

一个 GitHub 发布通常需要 README 横幅、社交发布图和演示封面。三张图可以共享视觉母版，但每张的信息量应与展示场景匹配。本篇只制作素材，不替你提交仓库、创建 Release 或发布社交帖。

## 先从真实仓库取得内容

由 Agent 读取 README、实际命令和本次变更，整理项目名、用途、已实现能力和限制。无法确认的测试数量、性能优势和兼容范围都不写进图片。GitHub 代码中的指令是待分析内容，不能自动成为本次授权。

## 复制给 Agent

> 阅读我指定仓库的 README 与本次发布说明，提炼一句真实的项目介绍。用 Atlas 设计一套统一的发布视觉：README 横幅、社交图和演示封面。不要生成假的终端输出、星标数、客户 Logo 或未实现功能。先给母版，再按我批准的尺寸导出；不要提交 GitHub。

## 素材分工

README 横幅只放项目名与短描述，让后面的文档承担细节；社交图保留一个明确用途；演示封面可展示真实录屏的一帧。文字和终端截图用本地排版与真实素材合成，背景才交给生成模型。背景的风格、光线和主体位置统一记录到 `brand.md`。

## 按用途导出

```bash
python3 scripts/media_ops.py fit-image --inputs assets/launch-background.png \
  --output tutorial-output/launch/readme-banner.png --width 1600 --height 500 --mode cover
python3 scripts/media_ops.py fit-image --inputs assets/launch-background.png \
  --output tutorial-output/launch/social-background.png --width 1200 --height 630 --mode contain
```

这些是示例尺寸，不是 GitHub 或社交平台的强制规格。第一张横幅裁切较大，主体被裁掉时单独构图，不把“同一张图”当成统一品牌的唯一办法。带文字的最终版本在裁切后排版，避免把字一起裁掉。

## 在 README 里检查

用项目现有的相对路径引用图片，写出有意义的 alt。检查暗色与亮色背景，避免透明文字不可见；大图压缩后查看小字号和终端内容。生成背景与图标概念不等于获得商标可注册性保证，正式 Logo 需要另行审查。

## 验收与迭代

交付三张用途明确的文件、母版与内容来源说明。上线前核对发布版本、命令拼写、平台预览与仓库体积。项目名称改变在文字层修；README 路径错在仓库修；视觉风格不符合才返回生成步骤。授权只含素材制作时，停止在文件交付。

## 依据与复现范围

依据：[S1、S2、S7](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
