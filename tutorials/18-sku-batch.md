# 18｜从 SKU 表批量生成素材，逐条记录状态

把 SKU 表转成素材任务，先解决“哪一行对应哪个任务、发生异常后从哪里继续”。本篇用两条虚构 SKU 演示离线建计划，再逐条授权执行；不会一次自动跑完整个商品目录。

## 输入表的最小结构

`examples/sku.csv` 包含 sku、prompt、reference_url。SKU 必须唯一、大小写也不能冲突；prompt 只能使用经确认的商品事实。真实商品需要参考图时，填写已经获授权且仍有效的 URL，不能只写“商品名”就期待模型还原真实包装。

## 先准备，不联网

```bash
MODEL='替换为当前已确认模型ID'
python3 scripts/batch_plan.py --csv examples/sku.csv --model "$MODEL" \
  --out tutorial-output/sku-batch-01 --max-jobs 2
```

脚本生成每条 SKU 的配置、计划和 `batch.json`。它拒绝重复 SKU、空提示词、路径穿越和超出数量；不调用 Atlas。带单张参考 URL 时，必须按 schema 明确指定 `--reference-field`；模型要数组或其他结构时请改成逐项配置，脚本不会猜字段。

## 抽一行跑通

```bash
python3 scripts/run_job.py preview --run-dir tutorial-output/sku-batch-01/lamp-white
```

预览不是估价。另用与计划相同的模型与 params 查询费用，确认当前账户、数量与参考素材外发授权。首件批准后才执行：

```bash
python3 scripts/run_job.py submit --run-dir tutorial-output/sku-batch-01/lamp-white --approve
python3 scripts/run_job.py wait --run-dir tutorial-output/sku-batch-01/lamp-white
```

`submit` 返回 pending 时脚本退出码为 3，这是任务未完成，不应由上层自动重交。只有 `wait/get` 用来继续原 ID。脚本的 `attempt.json` 在首次尝试前落盘，第二次 submit 会被拒绝；不要删除它绕过保护。

## 从小样到第二行

审核第一件的产品保真、输出尺寸和交付文件。确认后对第二行单独预览、估价和批准。真实规模扩大时要加服务端项目额度、并发限制和账户级任务记录；本地 max-jobs 仅限制这次计划里的数量，不能限制其他机器同时消费。

## 复制给 Agent

> 根据 SKU 表创建本地 Atlas 任务计划，先不上传和生成。检查 SKU 唯一性、事实文案、参考输入和行数上限。先对一条 SKU 做预览与估价，批准后提交一次并保存回执。任何受理未知的行暂停，不用重新提交填满“成功率”。

## 交付与恢复

每条 SKU 保留 prepared、pending、unknown、remote_failed、remote_succeeded 及内容审核结果。重新运行只读取已存在的计划，不创建一组新目录再跑一遍。下载失败恢复下载；包装失真记录内容失败，两者处理不同。

## 依据与复现范围

依据：[S1、S2、S6](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
