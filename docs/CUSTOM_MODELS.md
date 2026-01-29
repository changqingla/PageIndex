# 使用自定义 OpenAI 兼容模型

PageIndex 支持任何与 OpenAI API 格式兼容的模型服务。本指南将帮助你配置和使用各种自定义模型。

## 目录
- [快速开始](#快速开始)
- [支持的服务](#支持的服务)
- [配置方法](#配置方法)
- [常见问题](#常见问题)

---

## 快速开始

### 1. 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

### 2. 设置 API 配置

在 `.env` 文件中设置：

```bash
# API Key（必需）
CHATGPT_API_KEY=your_api_key_here

# 自定义 API 端点（可选）
OPENAI_API_BASE=http://localhost:11434/v1
```

### 3. 运行 PageIndex

```bash
python3 run_pageindex.py --pdf_path your_document.pdf --model your_model_name
```

---

## 支持的服务

### 1. Ollama（本地部署）

**优势**：完全本地运行，隐私保护，免费

**配置**：

```bash
# .env
OPENAI_API_BASE=http://localhost:11434/v1
CHATGPT_API_KEY=ollama  # 任意值即可
```

**使用示例**：

```bash
# 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 拉取模型
ollama pull qwen2.5:72b
ollama pull llama3.1:70b

# 运行 PageIndex
python3 run_pageindex.py \
    --pdf_path document.pdf \
    --model qwen2.5:72b
```

**推荐模型**：
- `qwen2.5:72b` - 适合中英文混合文档
- `llama3.1:70b` - 适合英文文档
- `qwen2.5:32b` - 较快速度，适合测试

---

### 2. vLLM（高性能推理）

**优势**：高吞吐量，支持批处理

**配置**：

```bash
# .env
OPENAI_API_BASE=http://localhost:8000/v1
CHATGPT_API_KEY=your_token
```

**启动 vLLM 服务器**：

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-72B-Instruct \
    --port 8000 \
    --api-key your_token
```

---

### 3. LM Studio（桌面应用）

**优势**：图形界面，易于使用

**配置**：

```bash
# .env
OPENAI_API_BASE=http://localhost:1234/v1
CHATGPT_API_KEY=lm-studio  # 任意值即可
```

**使用步骤**：
1. 下载并安装 [LM Studio](https://lmstudio.ai/)
2. 在 LM Studio 中下载模型
3. 启动本地服务器（在 LM Studio 的 "Local Server" 标签页）
4. 运行 PageIndex

---

### 4. Azure OpenAI

**优势**：企业级部署，数据隐私保障

**配置**：

```bash
# .env
OPENAI_API_BASE=https://your-resource.openai.azure.com/openai/deployments/your-deployment-name
CHATGPT_API_KEY=your_azure_api_key
```

**注意**：
- URL 格式：`https://{resource-name}.openai.azure.com/openai/deployments/{deployment-name}`
- API 版本会自动处理

---

### 5. OpenRouter（多模型聚合）

**优势**：访问多种模型，按需付费

**配置**：

```bash
# .env
OPENAI_API_BASE=https://openrouter.ai/api/v1
CHATGPT_API_KEY=your_openrouter_api_key
```

**支持的模型**：
- `anthropic/claude-3.5-sonnet`
- `google/gemini-pro-1.5`
- `meta-llama/llama-3.1-405b-instruct`

---

### 6. Together AI

**优势**：价格实惠，模型丰富

**配置**：

```bash
# .env
OPENAI_API_BASE=https://api.together.xyz/v1
CHATGPT_API_KEY=your_together_api_key
```

---

### 7. Groq（超快推理）

**优势**：极快推理速度

**配置**：

```bash
# .env
OPENAI_API_BASE=https://api.groq.com/openai/v1
CHATGPT_API_KEY=your_groq_api_key
```

**推荐模型**：
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`

---

## 配置方法

### 方法 1：环境变量（推荐）

在 `.env` 文件中设置：

```bash
CHATGPT_API_KEY=your_key
OPENAI_API_BASE=http://localhost:11434/v1
```

### 方法 2：配置文件

在 `pageindex/config.yaml` 中设置：

```yaml
model: "qwen2.5:72b"
api_base_url: "http://localhost:11434/v1"
```

**注意**：环境变量 `OPENAI_API_BASE` 会覆盖配置文件中的 `api_base_url`

---

## 模型选择建议

### 文档类型与推荐模型

| 文档类型 | 推荐模型 | 说明 |
|---------|---------|------|
| 中文/中英混合 | Qwen2.5-72B | 中文理解能力强 |
| 英文 | Llama-3.1-70B | 英文文档效果好 |
| 财务报告 | GPT-4o, Claude-3.5 | 需要高精度推理 |
| 学术论文 | GPT-4o, Qwen2.5-72B | 需要理解复杂结构 |
| 测试/小文档 | Qwen2.5-32B, Llama-3.1-8B | 速度快，成本低 |

### 性能考虑

- **准确度优先**：使用 70B+ 参数模型（GPT-4o, Qwen2.5-72B, Llama-3.1-70B）
- **速度优先**：使用 32B 以下模型或 Groq 服务
- **成本优先**：使用本地 Ollama 或 Together AI

---

## 常见问题

### Q1: 如何验证配置是否正确？

```python
import openai
import os
from dotenv import load_dotenv

load_dotenv()

client = openai.OpenAI(
    api_key=os.getenv("CHATGPT_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)

response = client.chat.completions.create(
    model="your_model_name",
    messages=[{"role": "user", "content": "Hello"}]
)

print(response.choices[0].message.content)
```

### Q2: Token 计数不准确怎么办？

对于自定义模型，PageIndex 会自动使用以下策略：
1. 尝试使用 tiktoken 的 GPT-4 tokenizer
2. 如果失败，使用字符数估算（约 4 字符 = 1 token）

这不会影响功能，只可能影响文档分组的精确度。

### Q3: 提示 "Connection Error" 怎么办？

检查：
1. 服务是否正常运行（如 Ollama: `curl http://localhost:11434/v1/models`）
2. `OPENAI_API_BASE` URL 是否正确（注意末尾的 `/v1`）
3. 防火墙或端口是否开放

### Q4: 模型输出不稳定怎么办？

建议：
1. 使用参数量 ≥32B 的模型
2. 对于关键文档，使用 GPT-4o 或 Claude-3.5
3. 检查模型是否支持 JSON 输出格式

### Q5: 如何使用多个不同的模型？

可以通过不同的配置运行：

```bash
# 使用 Ollama 的 Qwen
OPENAI_API_BASE=http://localhost:11434/v1 \
python3 run_pageindex.py --pdf_path doc.pdf --model qwen2.5:72b

# 使用 OpenAI
OPENAI_API_BASE= \
CHATGPT_API_KEY=sk-xxx \
python3 run_pageindex.py --pdf_path doc.pdf --model gpt-4o
```

---

## 完整示例

### Ollama 本地部署完整流程

```bash
# 1. 安装 Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. 拉取模型
ollama pull qwen2.5:72b

# 3. 配置 PageIndex
cat > .env << EOF
CHATGPT_API_KEY=ollama
OPENAI_API_BASE=http://localhost:11434/v1
EOF

# 4. 运行
python3 run_pageindex.py \
    --pdf_path tests/pdfs/2023-annual-report.pdf \
    --model qwen2.5:72b \
    --if-add-node-summary yes

# 5. 查看结果
cat results/2023-annual-report_structure.json
```

---

## 技术支持

如有问题，请访问：
- [GitHub Issues](https://github.com/VectifyAI/PageIndex/issues)
- [Discord 社区](https://discord.com/invite/VuXuf29EUj)
- [文档](https://docs.pageindex.ai)

---

## 贡献

欢迎提交 PR 添加更多模型服务的使用示例！
