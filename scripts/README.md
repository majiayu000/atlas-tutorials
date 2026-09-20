# 工具索引

所有工具可用 `--help` 查看参数。均为本包教学工具，不是新增 Atlas 子命令。

| 文件 | 能力 | 副作用 |
|---|---|---|
| run_job.py | prepare/preview/submit/get/wait/inspect | prepare 本地；preview/查询可联网；submit 需 --approve，可能计费 |
| receipt_id.py | 读取 CLI 根字段 ID | 只读本地，不解析所有 MCP/REST |
| batch_plan.py | CSV → 单 SKU 配置/目录 | 本地写文件，不批量提交 |
| media_audit.py | ffprobe 与可选全片解码 | 只读媒体，写可选报告 |
| media_ops.py | 适配尺寸、叠图、拼接、字幕、混音、对比 | 本地写新文件，拒绝覆盖 |
| make_fixtures.py | 合成测试图案/音调 | 无网络，无模型生成 |
| subtitles.py | 时间戳/SRT 校验与偏移合并 | 不转写、不自动对齐声音 |
| audio_chunks.py | 切分音频与保存偏移 | 本地 PCM，默认单声道，不做 ASR |
| blind_pack.py | 匿名候选与空评分表 | 复制文件，元数据仍需审查 |
| manifest.py | 字节数/SHA-256 清单 | 不扫描隐私或证明版权 |

run_job 的状态退出码：0 本次成功、3 仍处理中、4 远程失败、2 错误或未知。并非所有脚本都采用这个退出码表，见对应 --help 与教程。

素材、回执和 prompt 可包含私人信息。输出目录保持受控，不把 --approve 当成账户授权，不删除 attempt 标记重提任务。FFmpeg 工具只在可信本地素材上使用；不可信媒体需要隔离环境。
