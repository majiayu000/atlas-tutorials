# 05｜看懂 schema、--explain、dry_run 与费用估算

“这个请求长什么样”“参数是否符合模型”“大概要花多少钱”是三个问题。本篇用同一组文本生图输入，把它们分别查清。最终交付三份记录：schema、请求预览、费用信息；不提交生成。

## 读取模型参数

```bash
mkdir -p tutorial-output/schema-lab
MODEL='替换为已经发现的真实模型ID'
atlas models get "$MODEL" --json > tutorial-output/schema-lab/model.json
```

查看 required、字段类型、枚举、上下界和默认值。`"false"` 与 `false` 不同，图片数组与单一 URL 不同，视频的时长单位也必须确认。不要仅凭字段名字猜测取值。将已确认的模型输入保存为自己的 `params.json`；本包 `examples/config/image.json` 的 params 只是教学起点。

## 用同一输入做预览和估价

```bash
PARAMS='./tutorial-output/schema-lab/params.json'
test -s "$PARAMS"
atlas generate image "$MODEL" --params-json "@$PARAMS" --explain --json \
  > tutorial-output/schema-lab/preview.json
atlas generate cost image "$MODEL" --params-json "@$PARAMS" --json \
  > tutorial-output/schema-lab/cost.json
```

`params.json` 内只放模型参数，不放 `model`、凭据或整份 MCP 工具调用。预览后检查 CLI 是否进行了字段映射、采用了哪些默认值。估价和后续执行必须使用同样的模型、尺寸、数量和时长；修改其中任一项后重新估价。

## MCP 的对应做法

发现当前生成工具的 schema，确认存在 `dry_run`，然后用 `model`、`params`、`dry_run: true` 调用。工具返回“预览成功”不代表锁价。本次读取的独立 MCP 实现还允许在取不到模型 schema 时跳过部分验证；遇到这种情况，应停止并补齐 schema，不能把工具返回成功当成必填项全部通过。

## 本地参考素材的特殊情况

CLI 的预览不上传文件，费用命令也不会为了估价先上传。报价必须要已有 URL 时，先得到用户对上传的授权，再使用该 URL；或者明确指出报价不完整。省略必需参考图得到的文本生图报价，不是原编辑任务的准确报价。

## 刻意制造一个无费用错误

从真实枚举里选一个不合法值，或把已知数字字段改成对象，只运行预览，观察是否在提交前得到错误。然后恢复原参数。不要为了测试错误使用真实付费提交，也不要把完整 schema 复制进模型输入。完成后保存错误样例，以后升级时复测。

## 复制给 Agent

> 检查这份 Atlas 请求。先读取实际模型 schema，对 required、类型、枚举、数量和参考图字段逐项核对。只做 explain 或 dry_run，并单独解释估价；缺少 schema 或价格就报告未知，不上传、不生成、不自动改模型。

## 验收与排错

能够指出一个参数错误发生在哪一层，并明确“本次未提交”。JSON 语法错误先修语法；模型不接受字段先查 schema；报价服务不可用不代表免费。如果计划改变，把旧预览保留为历史记录，不悄悄覆盖已批准的请求。

## 依据与复现范围

依据：[S1、S2、S3、S6](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
