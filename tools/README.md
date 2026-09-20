# 文档维护工具

实际教程脚本与单元测试使用 Python 标准库；重建 HTML 与可选 YAML 静态检查才需要以下文档开发依赖：

```bash
python3 -m pip install -r requirements-docs.txt
python3 tools/build_reader.py
python3 tests/validate_package.py --output verification/static-checks-local.json
```

请在独立虚拟环境安装依赖。`build_reader.py` 将 Markdown 编译为单个自包含 HTML，不下载字体、模型或客户素材。修改 Markdown 后需重建 HTML。

静态检查不执行正文里的生成命令，只检查 Shell 语法、JSON/YAML、Python/Node 语法和相对路径；即使全部通过也不能替代真实模型联调。
