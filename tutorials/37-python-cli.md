# 37｜用 Python 调用 CLI，持久保存每次任务回执

本篇用 Python 调用 Atlas CLI，并把一项业务操作对应到一个稳定目录。目的在于保留请求、受理状态和产物位置，尤其避免脚本在等待超时后从头重新生成。随包的 `run_job.py` 是教学包装器，不是 Atlas 官方持久工作流服务。

## 配置与目录

准备 Python 3.10+ 和已登录的 Atlas CLI。先从当前目录选模型，检查必填参数与价格，再把实际参数写入配置。样例 [image.json](../examples/config/image.json) 的模型 ID 是故意设置的不可用占位，不改就会被拒绝。

```bash
atlas version --json
atlas auth status --json
atlas models list --type image --json
```

本包配置只有 `kind`、`model`、`params`。`params` 是已经核对的模型参数，不能包含凭据或覆盖 model。包装器不映射本地 `@file` 媒体，只接受获授权的 URL；需要上传本地参考时先按 [13](13-product-reference-edit.md) 处理，不把本地路径当成远程 URL。

> 将这个已核对请求作为一项稳定操作执行，使用固定 run 目录。先准备与预览，不提交；授权后只提交一次，保存任何返回的 ID，即使进程退出非零。等待失败只查原任务，受理未知时停止重提，不删除 attempt 标记来绕过保护。

## 分开运行，分开观察

```bash
python3 scripts/run_job.py prepare --config my-image.json --run-dir tutorial-output/job-001
python3 scripts/run_job.py preview --run-dir tutorial-output/job-001
```

prepare 只写本地文件，preview 调用 CLI 的 `--explain`，可能读取当前目录但不提交生成。价格需要另用正式估价入口，不能把 preview 当成报价。审查 `plan.json` 和预览后才进入付费步骤：

```bash
python3 scripts/run_job.py submit --run-dir tutorial-output/job-001 --approve
python3 scripts/run_job.py get --run-dir tutorial-output/job-001
python3 scripts/run_job.py wait --run-dir tutorial-output/job-001 --wait-seconds 600
python3 scripts/run_job.py inspect --run-dir tutorial-output/job-001
```

这些是独立阶段，不要在有 `set -e` 的一条 Shell 链里盲目串联。包装器退出 3 代表已知处理中，4 代表已知远程失败，2 代表错误或未知，0 才是本次阶段满足成功条件。被接受的异步提交通常就是处理中，所以 3 不代表需要再提交。

## 标记能保护什么，不能保护什么

提交前，脚本通过独占创建 `attempt.json` 记录一次尝试；同目录第二次提交会被阻止，崩溃也不自动移除。请求与参数有摘要校验，修改原计划会被拒绝。命令通过参数数组执行，不用 Shell 拼接，因此 prompt 不会直接成为 Shell 命令。

这些措施只约束这个目录和包装器。新建另一个目录、另一台机器或直接调用 API 仍可能产生新任务；客户端文件不能保证服务端 exactly-once、跨设备额度或账号级幂等。共享不可信目录也不是安全边界。

## 测试与接入应用

先运行离线测试：

```bash
python3 -m unittest discover -s tests -v
```

测试用模拟调用覆盖超时、非零退出仍有 ID、未知状态、计划变化与重复提交，不实际调用 Atlas。将其接入应用时，可导入模块或使用 subprocess 参数数组启动；不要让外部请求指定任意 `--atlas` 可执行路径。

日志包含 prompt、素材 URL 和路径等业务信息，应保存在受控位置；不要把完整 run 目录当成默认公开 artifact。成片验收另用 [35](35-delivery-audit.md)，不要把 wrapper 成功当成画面质量通过。

## 依据与复现范围

依据：[S1、S2、S6、S14](../SOURCES.md)。本文使用本包约定的教学文件；模型能力与价格以执行时实际目录为准。线上付费步骤未代用户执行，离线验证结果见 [测试报告](../verification/REPORT.md)。通用路径、授权和状态约定见 [执行约定](../common/EXECUTION.md)。
