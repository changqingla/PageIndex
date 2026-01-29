# 使用 Ollama 本地运行 PageIndex（5 分钟快速开始）

本指南将帮助你在 5 分钟内使用 Ollama 本地运行 PageIndex，完全免费，无需 API 密钥。

## 前置条件

- 至少 16GB RAM（推荐 32GB 用于 70B 模型）
- 50GB 可用磁盘空间

## 步骤 1：安装 Ollama（1 分钟）

### macOS / Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

下载并安装：[ollama.com/download](https://ollama.com/download)

验证安装：

```bash
ollama --version
```

## 步骤 2：下载模型（2-5 分钟）

### 推荐模型选择

| 模型 | 大小 | RAM 需求 | 语言支持 | 速度 | 适合场景 |
|------|------|---------|----------|------|---------|
| `qwen2.5:72b` | 41GB | 48GB | 中英文 | 慢 | 最佳准确度 |
| `qwen2.5:32b` | 19GB | 24GB | 中英文 | 中 | 平衡性能 |
| `qwen2.5:14b` | 9GB | 16GB | 中英文 | 快 | 日常使用 |
| `llama3.1:70b` | 40GB | 48GB | 英文 | 慢 | 英文文档 |
| `llama3.1:8b` | 4.7GB | 8GB | 英文 | 很快 | 测试/演示 |

### 下载模型

```bash
# 推荐：Qwen2.5 32B（中英文混合文档）
ollama pull qwen2.5:32b

# 或者：Qwen2.5 72B（最佳效果，需要更多内存）
ollama pull qwen2.5:72b

# 或者：Llama 3.1 8B（快速测试）
ollama pull llama3.1:8b
```

## 步骤 3：配置 PageIndex（30 秒）

```bash
cd PageIndex

# 创建 .env 文件
cat > .env << 'EOF'
CHATGPT_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
EOF
```

## 步骤 4：测试配置（30 秒）

```bash
# 测试连接
python3 scripts/test_custom_model.py --model qwen2.5:32b
```

应该看到类似输出：

```
✅ All tests passed! You're ready to use PageIndex.
```

## 步骤 5：运行 PageIndex（1-5 分钟）

```bash
# 基础使用
python3 run_pageindex.py \
    --pdf_path tests/pdfs/2023-annual-report.pdf \
    --model qwen2.5:32b

# 带摘要生成
python3 run_pageindex.py \
    --pdf_path your_document.pdf \
    --model qwen2.5:32b \
    --if-add-node-summary yes

# 完整功能
python3 run_pageindex.py \
    --pdf_path your_document.pdf \
    --model qwen2.5:32b \
    --if-add-node-summary yes \
    --if-add-doc-description yes \
    --if-add-node-text yes
```

## 查看结果

```bash
# 查看生成的树结构
cat results/your_document_structure.json

# 或使用 Python 查看
python3 -c "
import json
with open('results/your_document_structure.json') as f:
    data = json.load(f)
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
"
```

## 性能优化技巧

### 1. 使用 GPU 加速

Ollama 会自动使用 GPU（NVIDIA/AMD/Apple Silicon）。检查：

```bash
# 查看 GPU 使用情况
nvidia-smi  # NVIDIA GPU

# macOS 会自动使用 Metal
```

### 2. 调整并发数

如果内存充足，可以在 `config.yaml` 中调整：

```yaml
max_token_num_each_node: 30000  # 增大以减少调用次数
```

### 3. 模型量化

Ollama 默认使用 4-bit 量化，可以尝试不同精度：

```bash
# Q4_0: 最快，占用最少内存（默认）
ollama pull qwen2.5:32b-q4_0

# Q8_0: 更高精度
ollama pull qwen2.5:32b-q8_0
```

## 常见问题

### Q: Ollama 服务没有启动？

```bash
# macOS/Linux - Ollama 通常自动启动
ollama serve

# 或检查是否已运行
ps aux | grep ollama
```

### Q: 内存不足？

使用更小的模型：

```bash
ollama pull qwen2.5:14b
# 然后使用 --model qwen2.5:14b
```

### Q: 速度太慢？

1. 使用更小的模型（14B 或 8B）
2. 确保使用 GPU
3. 减少 `--if-add-node-summary` 等选项
4. 关闭其他占用 GPU 的程序

### Q: 输出质量不好？

1. 使用更大的模型（32B 或 72B）
2. 对于中文文档，使用 Qwen 系列
3. 对于英文文档，可以尝试 Llama 3.1

### Q: 如何更新模型？

```bash
ollama pull qwen2.5:32b  # 会自动更新到最新版本
```

## 与 OpenAI 对比

| 特性 | Ollama (本地) | OpenAI API |
|------|--------------|-----------|
| 成本 | 免费 | 按使用付费 |
| 隐私 | 完全本地 | 数据上传到云端 |
| 速度 | 取决于硬件 | 通常更快 |
| 准确度 | Qwen 72B ≈ GPT-4 | GPT-4o 最佳 |
| 网络要求 | 仅下载模型时 | 始终需要 |

## 进阶使用

### 批量处理多个文档

```bash
for pdf in docs/*.pdf; do
    python3 run_pageindex.py \
        --pdf_path "$pdf" \
        --model qwen2.5:32b \
        --if-add-node-summary yes
done
```

### 自定义模型参数

创建 Modelfile：

```bash
cat > Modelfile << 'EOF'
FROM qwen2.5:32b
PARAMETER temperature 0
PARAMETER top_p 0.9
PARAMETER num_ctx 32768
EOF

# 创建自定义模型
ollama create my-qwen -f Modelfile

# 使用自定义模型
python3 run_pageindex.py --pdf_path doc.pdf --model my-qwen
```

### 监控资源使用

```bash
# 监控 GPU
watch -n 1 nvidia-smi

# 监控内存
htop
```

## 下一步

- 📖 阅读 [CUSTOM_MODELS.md](CUSTOM_MODELS.md) 了解更多配置选项
- 🔍 查看 [tutorials/tree-search/](../tutorials/tree-search/) 学习如何使用生成的树结构进行检索
- 💬 加入 [Discord 社区](https://discord.com/invite/VuXuf29EUj) 获取帮助

## 故障排除

如遇到问题：

1. 运行测试脚本：`python3 scripts/test_custom_model.py --model qwen2.5:32b`
2. 检查日志：`ls logs/` 查看详细错误信息
3. 查看 Ollama 日志：`journalctl -u ollama -f` (Linux) 或 `/var/log/ollama/ollama.log`
4. 访问 [GitHub Issues](https://github.com/VectifyAI/PageIndex/issues)

## 完整示例输出

```json
{
  "doc_name": "2023-annual-report.pdf",
  "structure": [
    {
      "title": "Overview",
      "node_id": "0001",
      "start_index": 1,
      "end_index": 5,
      "summary": "This section provides an overview of the company's performance in 2023..."
    },
    {
      "title": "Financial Results",
      "node_id": "0002",
      "start_index": 6,
      "end_index": 15,
      "nodes": [
        {
          "title": "Revenue Analysis",
          "node_id": "0003",
          "start_index": 6,
          "end_index": 10,
          "summary": "Revenue increased by 23% year-over-year..."
        }
      ]
    }
  ]
}
```

---

🎉 恭喜！你已经成功在本地运行 PageIndex！
