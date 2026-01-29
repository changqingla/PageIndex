# PageIndex 算法技术报告

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档名称 | PageIndex 算法技术报告 |
| 版本 | 1.0 |
| 日期 | 2025-01-29 |
| 项目 | PageIndex - Vectorless, Reasoning-based RAG |

---

## 目录

- [1. 项目概述](#1-项目概述)
  - [1.1 背景与动机](#11-背景与动机)
  - [1.2 核心特性](#12-核心特性)
  - [1.3 技术架构](#13-技术架构)
- [2. 系统架构](#2-系统架构)
  - [2.1 模块组成](#21-模块组成)
  - [2.2 依赖关系](#22-依赖关系)
  - [2.3 默认配置参数](#23-默认配置参数)
- [3. PDF 文档树索引算法](#3-pdf-文档树索引算法)
  - [3.1 主流程概览](#31-主流程概览)
  - [3.2 目录（TOC）检测算法](#32-目录toc检测算法)
  - [3.3 三种处理模式](#33-三种处理模式)
  - [3.4 验证与修正机制](#34-验证与修正机制)
  - [3.5 后处理与树构建](#35-后处理与树构建)
  - [3.6 大节点递归细分](#36-大节点递归细分)
  - [3.7 输出结构示例](#37-输出结构示例)
- [4. Markdown 文档树索引算法](#4-markdown-文档树索引算法)
  - [4.1 设计思路](#41-设计思路)
  - [4.2 核心流程](#42-核心流程)
  - [4.3 标题提取算法](#43-标题提取算法)
  - [4.4 文本内容提取](#44-文本内容提取)
  - [4.5 树瘦身（Thinning）](#45-树瘦身thinning)
  - [4.6 树构建](#46-树构建)
  - [4.7 摘要生成](#47-摘要生成)
- [5. 工具函数与 LLM 交互](#5-工具函数与-llm-交互)
  - [5.1 Token 计数](#51-token-计数)
  - [5.2 LLM 调用](#52-llm-调用)
  - [5.3 物理索引标签](#53-物理索引标签)
- [6. 算法复杂度与性能](#6-算法复杂度与性能)
  - [6.1 时间复杂度](#61-时间复杂度)
  - [6.2 空间复杂度](#62-空间复杂度)
  - [6.3 并发优化](#63-并发优化)
- [7. 检索算法](#7-检索算法)
  - [7.1 单文档内检索：树搜索](#71-单文档内检索树搜索tree-search)
  - [7.2 多文档检索：文档搜索](#72-多文档检索文档搜索document-search)
  - [7.3 完整检索架构](#73-完整检索架构)
  - [7.4 检索优势对比](#74-检索优势对比)
- [8. 应用场景与基准表现](#8-应用场景与基准表现)
  - [8.1 典型应用场景](#81-典型应用场景)
  - [8.2 FinanceBench 基准](#82-financebench-基准)
- [9. 总结](#9-总结)
  - [9.1 核心算法模块](#91-核心算法模块)
  - [9.2 技术创新点](#92-技术创新点)
  - [9.3 适用场景](#93-适用场景)
- [附录 A：关键函数索引](#附录-a关键函数索引)
- [附录 B：参考文献](#附录-b参考文献)

---

## 1. 项目概述

### 1.1 背景与动机

传统的基于向量的 RAG（Retrieval-Augmented Generation）系统依赖**语义相似度**进行检索，而非真正的**相关性**。在专业长文档分析场景中，相似度 ≠ 相关性，真正的检索需要**推理能力**。当面对需要领域专业知识和多步推理的专业文档时，相似度搜索往往表现不佳。

PageIndex 受 AlphaGo 启发，提出了一种**无向量**、**基于推理**的 RAG 系统，通过构建文档的**层次化树形索引**，并利用大语言模型（LLM）在该索引上进行**推理**，实现**代理式、上下文感知**的检索。它模拟人类专家如何通过**树搜索**在复杂文档中导航和提取知识。

### 1.2 核心特性

与传统的基于向量的 RAG 相比，PageIndex 具有以下特性：

- **无向量数据库**：使用文档结构和 LLM 推理进行检索，而非向量相似度搜索
- **无分块（Chunking）**：文档按自然章节组织，而非人工切分
- **类人检索**：模拟人类专家在复杂文档中导航和提取知识的方式
- **可解释性与可追溯性**：检索基于推理，可追溯、可解释，带有页码和章节引用

### 1.3 技术架构

PageIndex 的检索流程分为两个核心步骤：

1. **生成文档的"目录"树形结构索引**
2. **通过树搜索执行基于推理的检索**

```
┌─────────────────┐     ┌──────────────────────┐     ┌─────────────────┐
│   PDF/MD 文档   │ ──► │  树形结构索引生成    │ ──► │  树搜索检索      │
└─────────────────┘     └──────────────────────┘     └─────────────────┘
```

---

## 2. 系统架构

### 2.1 模块组成

```
PageIndex/
├── pageindex/
│   ├── page_index.py      # PDF 文档树索引核心算法
│   ├── page_index_md.py   # Markdown 文档树索引算法
│   ├── utils.py           # 工具函数、LLM 调用、树操作
│   └── config.yaml        # 默认配置
├── run_pageindex.py       # 命令行入口
└── cookbook/              # 示例 Notebook
```

### 2.2 依赖关系

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| openai | 1.101.0 | LLM API 调用 |
| pymupdf | 1.26.4 | PDF 解析（可选） |
| PyPDF2 | 3.0.1 | PDF 解析 |
| tiktoken | 0.11.0 | Token 计数 |
| python-dotenv | 1.1.0 | 环境变量 |
| pyyaml | 6.0.2 | 配置加载 |

### 2.3 默认配置参数

```yaml
model: "gpt-4o-2024-11-20"
toc_check_page_num: 20          # 检查目录的页数
max_page_num_each_node: 10      # 每个节点最大页数
max_token_num_each_node: 20000  # 每个节点最大 token 数
if_add_node_id: "yes"
if_add_node_summary: "yes"
if_add_doc_description: "no"
if_add_node_text: "no"
```

---

## 3. PDF 文档树索引算法

### 3.1 主流程概览

```
page_index_main()
    │
    ├── get_page_tokens()           # 解析 PDF，获取每页文本和 token 数
    │
    └── page_index_builder()
            │
            ├── tree_parser()      # 树解析主流程
            │       │
            │       ├── check_toc()           # 检测目录
            │       ├── meta_processor()      # 根据模式处理
            │       ├── add_preface_if_needed()
            │       ├── check_title_appearance_in_start_concurrent()
            │       ├── post_processing()     # 后处理为树结构
            │       └── process_large_node_recursively()  # 递归处理大节点
            │
            ├── write_node_id()     # 添加节点 ID
            ├── add_node_text()     # 可选：添加节点文本
            └── generate_summaries_for_structure()  # 可选：生成摘要
```

### 3.2 目录（TOC）检测算法

#### 3.2.1 检测流程

```python
def find_toc_pages(start_page_index, page_list, opt):
    """在文档前 N 页中检测目录页"""
    toc_page_list = []
    for i in range(start_page_index, min(opt.toc_check_page_num, len(page_list))):
        detected_result = toc_detector_single_page(page_list[i][0], model=opt.model)
        if detected_result == 'yes':
            toc_page_list.append(i)
        elif detected_result == 'no' and toc_page_list:
            break  # 目录结束
    return toc_page_list
```

**关键点**：
- 使用 LLM 逐页判断是否为目录页
- 目录页通常连续出现，遇到非目录页即停止
- 默认检查前 20 页

#### 3.2.2 目录内容提取

```python
def toc_extractor(page_list, toc_page_list, model):
    # 1. 拼接目录页文本
    toc_content = "".join(page_list[i][0] for i in toc_page_list)
    # 2. 将 "..." 等省略符替换为 ":"
    toc_content = transform_dots_to_colon(toc_content)
    # 3. 检测目录是否包含页码
    has_page_index = detect_page_index(toc_content, model=model)
    return {"toc_content": toc_content, "page_index_given_in_toc": has_page_index}
```

### 3.3 三种处理模式

根据目录检测结果，系统采用三种处理模式：

| 模式 | 触发条件 | 处理逻辑 |
|------|----------|----------|
| `process_toc_with_page_numbers` | 检测到目录且目录含页码 | 利用目录页码 + 物理页面对齐 |
| `process_toc_no_page_numbers` | 检测到目录但无页码 | 扫描正文，用 LLM 定位各章节起始页 |
| `process_no_toc` | 未检测到目录 | 全文扫描，用 LLM 生成层次结构 |

#### 3.3.1 模式一：目录含页码

```
1. toc_transformer()      # 将目录文本转为 JSON 结构
2. toc_index_extractor()  # 用正文前几页建立"标题→物理页"映射
3. extract_matching_page_pairs()  # 匹配目录页码与物理页码
4. calculate_page_offset()       # 计算页码偏移量（众数）
5. add_page_offset_to_toc_json() # 将偏移应用到所有条目
6. process_none_page_numbers()  # 处理缺失页码的条目
```

**页码偏移计算**：文档内页码与物理页码可能不一致（如前言用罗马数字），通过匹配多个条目计算众数偏移量进行校正。

#### 3.3.2 模式二：目录无页码

```
1. toc_transformer()      # 将目录转为 JSON
2. page_list_to_group_text()  # 按 token 限制将页面分组
3. 对每组调用 add_page_number_to_toc()  # LLM 判断各章节是否在该组开始
4. convert_physical_index_to_int()  # 转换物理索引格式
```

**页面分组策略**：
- 使用 `max_tokens=20000` 限制每组 token 数
- 组间有 `overlap_page=1` 重叠，避免章节边界被切断
- 分组算法保证每组接近 `average_tokens_per_part`

#### 3.3.3 模式三：无目录

```
1. page_list_to_group_text()  # 页面分组
2. generate_toc_init()        # 对第一组生成初始树结构
3. 对后续组调用 generate_toc_continue()  # 延续树结构
4. convert_physical_index_to_int()
```

**LLM Prompt 设计**：
- 文本中插入 `<physical_index_X>` 标签标记页码
- 要求 LLM 提取原始标题，仅修正空格不一致
- 输出格式：`[{structure, title, physical_index}, ...]`

### 3.4 验证与修正机制

#### 3.4.1 验证流程

```python
async def verify_toc(page_list, list_result, start_index, N=None, model):
    """抽样验证目录条目的页码是否正确"""
    # 随机抽样 N 个条目（或全部）
    # 对每个条目调用 check_title_appearance()：检查该标题是否在指定页出现
    # 返回准确率和错误列表
```

#### 3.4.2 降级策略

```
若 accuracy == 1.0：
    直接返回
若 accuracy > 0.6 且有错误：
    调用 fix_incorrect_toc_with_retries() 修正（最多 3 次）
否则：
    降级到下一模式：
    - process_toc_with_page_numbers → process_toc_no_page_numbers
    - process_toc_no_page_numbers → process_no_toc
    - process_no_toc → 抛出异常
```

#### 3.4.3 错误修正算法

```python
async def fix_incorrect_toc(toc_with_page_number, page_list, incorrect_results):
    """对每个错误条目："""
    for item in incorrect_results:
        # 1. 确定搜索范围 [prev_correct, next_correct]
        # 2. 调用 single_toc_item_index_fixer() 用 LLM 重新定位
        # 3. 调用 check_title_appearance() 验证修正结果
        # 4. 仅当验证通过才更新
```

### 3.5 后处理与树构建

#### 3.5.1 标题起始位置检查

```python
async def check_title_appearance_in_start_concurrent(structure, page_list, model):
    """并发检查：每个章节是否在其 physical_index 页的开头开始"""
    # 若章节不在页首开始，则 appear_start='no'
    # 用于正确计算 end_index
```

#### 3.5.2 列表转树

```python
def list_to_tree(data):
    """将扁平列表转为层次树"""
    # structure 格式: "1", "1.1", "1.2", "2" 等
    # 通过 get_parent_structure() 解析父子关系
    # 例如 "1.2.3" 的父节点为 "1.2"
```

#### 3.5.3 确定 start_index 和 end_index

```python
def post_processing(structure, end_physical_index):
    for i, item in enumerate(structure):
        item['start_index'] = item['physical_index']
        if i < len(structure) - 1:
            if structure[i+1]['appear_start'] == 'yes':
                item['end_index'] = structure[i+1]['physical_index'] - 1
            else:
                item['end_index'] = structure[i+1]['physical_index']
        else:
            item['end_index'] = end_physical_index
    return list_to_tree(structure)
```

### 3.6 大节点递归细分

当某节点页数或 token 数超过阈值时，对其进行递归细分：

```python
async def process_large_node_recursively(node, page_list, opt):
    if (node['end_index'] - node['start_index'] > max_page_num_each_node 
        and token_num >= max_token_num_each_node):
        # 对该节点范围内的页面，以 process_no_toc 模式重新生成子结构
        node_toc_tree = await meta_processor(node_page_list, mode='process_no_toc')
        node_toc_tree = await check_title_appearance_in_start_concurrent(...)
        node['nodes'] = post_processing(valid_node_toc_items, node['end_index'])
    # 递归处理子节点
    for child_node in node['nodes']:
        await process_large_node_recursively(child_node, ...)
```

### 3.7 输出结构示例

```json
{
  "doc_name": "2023-annual-report-truncated.pdf",
  "structure": [
    {
      "title": "Preface",
      "start_index": 1,
      "end_index": 4,
      "node_id": "0000"
    },
    {
      "title": "Financial Stability",
      "start_index": 21,
      "end_index": 21,
      "node_id": "0006",
      "nodes": [
        {
          "title": "Monitoring Financial Vulnerabilities",
          "start_index": 22,
          "end_index": 28,
          "node_id": "0007"
        }
      ]
    }
  ]
}
```

---

## 4. Markdown 文档树索引算法

### 4.1 设计思路

Markdown 通过 `#` 层级天然具有结构，无需 LLM 检测目录。算法基于正则解析标题，构建树形索引。

### 4.2 核心流程

```
md_to_tree()
    │
    ├── extract_nodes_from_markdown()    # 提取标题节点
    ├── extract_node_text_content()      # 提取每个节点对应的文本内容
    ├── [可选] tree_thinning_for_index() # 树瘦身：合并过小节点
    ├── build_tree_from_nodes()          # 构建树结构
    ├── write_node_id()
    └── [可选] generate_summaries_for_structure_md()
```

### 4.3 标题提取算法

```python
def extract_nodes_from_markdown(markdown_content):
    header_pattern = r'^(#{1,6})\s+(.+)$'
    # 忽略代码块内的 #（非标题）
    for line in lines:
        if not in_code_block and re.match(header_pattern, line):
            node_list.append({'node_title': title, 'line_num': line_num})
```

### 4.4 文本内容提取

```python
def extract_node_text_content(node_list, markdown_lines):
    """每个节点的文本 = 从该节点行到下一同级或更高级标题行之前"""
    for i, node in enumerate(all_nodes):
        start_line = node['line_num'] - 1
        end_line = all_nodes[i+1]['line_num'] - 1 if i+1 < len(all_nodes) else len(lines)
        node['text'] = '\n'.join(markdown_lines[start_line:end_line])
```

### 4.5 树瘦身（Thinning）

当节点 token 数小于 `min_node_token` 时，将其与子节点合并：

```python
def tree_thinning_for_index(node_list, min_node_token, model):
    """从叶向根遍历，若节点 token 数不足则合并其子节点文本"""
    for i in range(len(result_list) - 1, -1, -1):
        if total_tokens < min_node_token:
            # 合并所有子节点文本到当前节点
            merged_text = parent_text + '\n\n'.join(children_texts)
            result_list[i]['text'] = merged_text
            nodes_to_remove.update(children_indices)
```

### 4.6 树构建

```python
def build_tree_from_nodes(node_list):
    """使用栈维护层级，根据 level 建立父子关系"""
    stack = []  # (node, level)
    for node in node_list:
        while stack and stack[-1][1] >= current_level:
            stack.pop()
        if not stack:
            root_nodes.append(tree_node)
        else:
            parent_node['nodes'].append(tree_node)
        stack.append((tree_node, current_level))
```

### 4.7 摘要生成

- 若节点 token 数 < `summary_token_threshold`（默认 200），直接使用原文作为 summary
- 否则调用 `generate_node_summary()` 用 LLM 生成摘要
- 有子节点的节点使用 `prefix_summary`，叶子节点使用 `summary`

---

## 5. 工具函数与 LLM 交互

### 5.1 Token 计数

```python
def count_tokens(text, model):
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))
```

### 5.2 LLM 调用

- `ChatGPT_API()`：同步调用
- `ChatGPT_API_async()`：异步调用，用于并发
- `ChatGPT_API_with_finish_reason()`：返回 `finish_reason`，用于检测输出是否被截断

所有调用均包含重试机制（最多 10 次），`temperature=0` 保证确定性。

### 5.3 物理索引标签

文档中插入 `<physical_index_X>` 和 `</physical_index_X>` 标签，用于：
1. 让 LLM 明确每页的物理位置
2. 在 `toc_index_extractor`、`add_page_number_to_toc` 等步骤中精确定位章节起始页

---

## 6. 算法复杂度与性能

### 6.1 时间复杂度

| 阶段 | 复杂度 | 说明 |
|------|--------|------|
| PDF 解析 | O(P) | P 为页数 |
| TOC 检测 | O(min(T, P)) | T=toc_check_page_num |
| 目录处理 | O(S × L) | S=章节数，L=LLM 延迟 |
| 验证 | O(N × L) | N=抽样数 |
| 大节点递归 | O(D × L) | D=大节点深度 |

整体以 LLM 调用为主，实际耗时取决于 API 延迟和并发策略。

### 6.2 空间复杂度

- 页面列表：O(P × 平均页长)
- 树结构：O(S)，S 为节点数
- 分组文本：受 `max_token_num_each_node` 限制

### 6.3 并发优化

- `check_title_appearance_in_start_concurrent`：并发检查标题起始位置
- `verify_toc`：并发验证多个条目
- `fix_incorrect_toc`：并发修正多个错误条目

---

## 7. 检索算法

PageIndex 完成树结构构建后，检索分为两个层次：**单文档内检索（树搜索）**和**多文档检索（文档搜索）**。

### 7.1 单文档内检索：树搜索（Tree Search）

#### 7.1.1 基础 LLM 树搜索

最简单的检索策略是使用 LLM 基于树结构进行推理搜索。

**核心 Prompt 模板：**

```python
prompt = f"""
You are given a query and the tree structure of a document.
You need to find all nodes that are likely to contain the answer.

Query: {query}

Document tree structure: {PageIndex_Tree}

Reply in the following JSON format:
{{
  "thinking": <your reasoning about which nodes are relevant>,
  "node_list": [node_id1, node_id2, ...]
}}
"""
```

**工作流程：**

```
用户问题 → LLM 推理 → 识别相关节点 → 返回 node_id 列表 → 提取节点文本 → 生成答案
```

**示例：**

```
Query: "What was the company's revenue in Q3 2023?"

LLM 推理过程：
- 识别关键词："revenue", "Q3 2023"
- 在树结构中定位：node_id "0012" ("Financial Results - Q3 2023")
- 返回：["0012"]
```

#### 7.1.2 结合专家知识的增强树搜索

通过在 prompt 中注入领域专家知识或用户偏好，实现更精准的检索。

**增强 Prompt 模板：**

```python
prompt = f"""
You are given a question and a tree structure of a document.
You need to find all nodes that are likely to contain the answer.

Query: {query}

Document tree structure: {PageIndex_Tree}

Expert Knowledge of relevant sections: {Preference}

Reply in the following JSON format:
{{
  "thinking": <reasoning about which nodes are relevant>,
  "node_list": [node_id1, node_id2, ...]
}}
"""
```

**专家知识示例：**

```
If the query mentions EBITDA adjustments, prioritize:
- Item 7 (MD&A) in 10-K reports
- Footnotes in Item 8 (Financial Statements)
```

**优势：**

- 无需微调 embedding 模型
- 通过自然语言直接注入领域知识
- 灵活适应不同领域和用户偏好

#### 7.1.3 蒙特卡洛树搜索（MCTS）

在 PageIndex 的商业服务（Dashboard 和 API）中，使用**价值函数引导的 MCTS**进行更高级的树搜索。

**MCTS 核心思想：**

```
1. Selection（选择）：从根节点开始，根据价值函数选择最有希望的子节点
2. Expansion（扩展）：扩展选中的叶子节点
3. Simulation（模拟）：评估新节点的相关性得分
4. Backpropagation（回溯）：将评估结果回传更新父节点价值
```

**与 AlphaGo 的类比：**

| AlphaGo | PageIndex |
|---------|-----------|
| 棋盘状态 | 文档树节点 |
| 下一步走法 | 选择子节点 |
| 胜率 | 相关性得分 |
| 目标：赢棋 | 目标：找到答案 |

#### 7.1.4 检索后生成答案

```python
# 1. 树搜索获取相关节点
relevant_nodes = tree_search(query, pageindex_tree)

# 2. 提取节点对应的文本
context = ""
for node_id in relevant_nodes:
    node = find_node_by_id(pageindex_tree, node_id)
    context += f"Section: {node['title']}\n"
    context += f"Pages: {node['start_index']}-{node['end_index']}\n"
    context += node['text'] + "\n\n"

# 3. 基于上下文生成答案
answer = llm_generate(
    prompt=f"Question: {query}\n\nContext:\n{context}\n\nAnswer:"
)
```

### 7.2 多文档检索：文档搜索（Document Search）

当需要在多个文档中检索时，PageIndex 提供三种文档级检索策略：

#### 7.2.1 基于元数据的文档搜索

**适用场景：**
- 财务报告（按公司、时期分类）
- 法律文档（按案件类型分类）
- 医疗记录（按患者、病症分类）

**流程：**

```
1. 生成 PageIndex 树 → 获取 doc_id
2. 建立数据库表：存储 doc_id + 元数据
   ┌─────────┬──────────┬──────────┬──────┐
   │ doc_id  │ company  │ period   │ type │
   ├─────────┼──────────┼──────────┼──────┤
   │ doc_001 │ Apple    │ Q3 2023  │ 10-Q │
   │ doc_002 │ Apple    │ Q4 2023  │ 10-Q │
   └─────────┴──────────┴──────────┴──────┘
3. Query-to-SQL：LLM 将用户问题转为 SQL
   Query: "Apple's Q3 2023 revenue?"
   → SQL: SELECT doc_id FROM docs WHERE company='Apple' AND period='Q3 2023'
4. 使用 doc_id 调用 PageIndex API 进行树搜索
```

#### 7.2.2 基于语义的文档搜索

**适用场景：**
- 文档主题多样
- 需要语义相似度匹配

**流程与评分公式：**

```
1. 文档分块 & Embedding
   - 对所有文档进行分块
   - 使用 embedding 模型转为向量
   - 存储到向量数据库，附带 doc_id

2. 向量搜索
   - 对查询进行 embedding
   - 检索 top-K 相似块及其 doc_id

3. 计算文档得分
```

**文档评分公式：**

$$
\text{DocScore} = \frac{1}{\sqrt{N+1}} \sum_{n=1}^N \text{ChunkScore}(n)
$$

其中：
- $N$ = 该文档相关的块数量
- $\text{ChunkScore}(n)$ = 第 $n$ 个块的相关性得分（向量相似度）
- $\sqrt{N+1}$ 归一化：奖励相关块多的文档，但有边际递减效应
- $+1$ 确保无块的文档不会除零

**设计原理：**
- 累加项：聚合所有相关块的得分
- 平方根：防止大文档因块数量优势占主导
- 倾向于"少而精"的相关内容，而非"多而泛"

```
4. 选择 top 文档，使用 doc_id 调用 PageIndex API 树搜索
```

#### 7.2.3 基于描述的文档搜索

**适用场景：**
- 无元数据
- 文档数量较少（<100）

**流程：**

```
1. 生成 PageIndex 树 → 获取 doc_id 和树结构

2. 生成文档描述
```

```python
prompt = f"""
You are given a table of contents structure of a document. 
Your task is to generate a one-sentence description for the document 
that makes it easy to distinguish from other documents.

Document tree structure: {PageIndex_Tree}

Directly return the description, do not include any other text.
"""
```

```
3. LLM 文档选择
```

```python
prompt = f""" 
You are given a list of documents with their IDs, file names, and descriptions.
Your task is to select documents that may contain information relevant to the query.

Query: {query}

Documents: [
    {{"doc_id": "doc_001", "doc_name": "Annual Report 2023", 
      "doc_description": "Financial performance and strategic initiatives..."}},
    {{"doc_id": "doc_002", "doc_name": "Q3 Earnings", 
      "doc_description": "Quarterly revenue, expenses, and forecasts..."}}
]

Response Format:
{{
    "thinking": "<Your reasoning for document selection>",
    "answer": ["doc_id1", "doc_id2"]  // Return [] if none relevant
}}
"""
```

```
4. 使用 doc_id 调用 PageIndex API 树搜索
```

### 7.3 完整检索架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户查询 (Query)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │   是否多文档？           │
         └─────────┬───────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
    单文档              多文档
         │                   │
         ▼                   ▼
   ┌─────────┐      ┌────────────────┐
   │树搜索   │      │ 文档搜索策略    │
   │(MCTS/   │      │ - 元数据        │
   │ LLM)    │      │ - 语义          │
   └────┬────┘      │ - 描述          │
        │           └────────┬────────┘
        │                    │
        │                    ▼
        │           ┌─────────────────┐
        │           │ 获取 doc_id 列表│
        │           └────────┬────────┘
        │                    │
        │                    ▼
        │           ┌─────────────────┐
        │           │对每个文档树搜索 │
        └───────────┤                 │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ 提取节点文本     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ LLM 生成答案    │
                    └─────────────────┘
```

### 7.4 检索优势对比

| 维度 | 传统向量 RAG | PageIndex 树搜索 |
|------|-------------|-----------------|
| **检索依据** | 语义相似度 | 推理 + 结构 |
| **可解释性** | 低（"vibe retrieval"） | 高（可追溯推理路径） |
| **精确度** | 中（similarity ≠ relevance） | 高（reasoning-based） |
| **长文档** | 需分块，易丢失上下文 | 保持层次，上下文完整 |
| **专家知识注入** | 需微调模型 | 直接注入 prompt |
| **页码/章节引用** | 难以准确 | 内置（start_index/end_index） |

---

## 8. 应用场景与基准表现

### 8.1 典型应用场景

- 财务报告、监管文件
- 学术教材、技术手册
- 法律文档
- 任何超出 LLM 上下文限制的长文档

### 8.2 FinanceBench 基准

PageIndex 驱动的 [Mafin 2.5](https://vectify.ai/mafin) 在 [FinanceBench](https://arxiv.org/abs/2311.11944) 上达到 **98.7%** 准确率，显著优于传统基于向量的 RAG 方案。

**性能对比：**

| 方法 | 准确率 | 说明 |
|------|--------|------|
| **Mafin 2.5 (PageIndex)** | **98.7%** | 推理式树搜索 |
| 传统向量 RAG | ~85-90% | 基于语义相似度 |

**成功关键：**
- 层次化索引保留文档结构
- 推理式检索更贴近人类专家分析流程
- 精确的页码和章节定位

---

## 9. 总结

PageIndex 通过**层次化树索引**和**基于推理的树搜索**，实现了无向量、无分块的 RAG 检索方案。

### 9.1 核心算法模块

1. **树索引生成**
   - 多模式目录处理（有/无目录，有/无页码）
   - 验证与降级机制
   - 大节点递归细分
   - Markdown 标题解析

2. **单文档检索（树搜索）**
   - 基础 LLM 树搜索
   - 专家知识增强
   - MCTS 价值函数引导

3. **多文档检索（文档搜索）**
   - 元数据搜索（Query-to-SQL）
   - 语义搜索（向量 + 评分公式）
   - 描述搜索（LLM 匹配）

### 9.2 技术创新点

- **推理 > 相似度**：用 LLM 推理替代向量相似度，实现 relevance 而非 similarity
- **结构保留**：避免分块导致的上下文丢失
- **可解释性**：检索路径可追溯，结果带页码和章节引用
- **灵活性**：通过自然语言注入领域知识，无需模型微调

### 9.3 适用场景

- **长文档分析**：财报、学术论文、法律文档、技术手册
- **专业领域**：需要精确定位和推理的场景
- **多文档问答**：结合元数据、语义或描述进行文档级检索

整体设计充分利用 LLM 的推理与理解能力，在专业长文档场景下实现了 SOTA 级别的检索效果（FinanceBench 98.7%）。

---

## 附录 A：关键函数索引

### A.1 树索引生成

| 函数名 | 文件 | 功能 |
|--------|------|------|
| `page_index_main` | page_index.py | PDF 主入口 |
| `tree_parser` | page_index.py | 树解析主流程 |
| `check_toc` | page_index.py | 目录检测 |
| `meta_processor` | page_index.py | 多模式处理器 |
| `verify_toc` | page_index.py | 验证目录准确性 |
| `fix_incorrect_toc` | page_index.py | 修正错误条目 |
| `post_processing` | utils.py | 列表转树 |
| `list_to_tree` | utils.py | 扁平列表转树 |
| `md_to_tree` | page_index_md.py | Markdown 主入口 |
| `extract_nodes_from_markdown` | page_index_md.py | 标题提取 |

### A.2 检索相关

检索逻辑在 PageIndex 商业服务（Dashboard/API）中实现，开源库提供树结构生成。关键概念：

- **树搜索 Prompt**：见 `tutorials/tree-search/README.md`
- **文档搜索策略**：见 `tutorials/doc-search/` 目录

## 附录 B：参考文献

- [PageIndex Framework 介绍](https://pageindex.ai/blog/pageindex-intro)
- [Mafin 2.5 基准结果](https://vectify.ai/blog/Mafin2.5)
- [FinanceBench 论文](https://arxiv.org/abs/2311.11944)
