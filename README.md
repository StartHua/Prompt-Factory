# Prompt Factory

AI Prompt Factory - Automated High-Quality Prompt Suite Generation

After the system runs, various roles required by agents will be created, responsible for different functions!

It's not a single prompt word, it's a complete set of agent prompt word engineering！！！！

Example : server/result/时尚分镜助手，能分析图片并生成多角度分镜_2025-12-18

## Overview

Prompt Factory is a multi-agent collaborative prompt generation system. Input your requirements, and the system will automatically:

1. **Analyze** - Analyzer breaks down requirements, designs system architecture and roles
2. **Generate** - Generator creates professional prompts for each role
3. **Review** - Reviewer evaluates prompt quality, scores and suggests improvements
4. **Optimize** - Optimizer refines prompts based on review until they pass

Output is a structured set of prompt files ready for use in AI applications.

## Features

- 🚀 Multi-agent pipeline automation
- 🔄 Review-optimize iteration loop for quality assurance
- 💾 Checkpoint recovery, resume after interruption
- 🌍 Bilingual interface (Chinese/English)
- 📁 Real-time saving to Markdown files

## Installation

### Requirements

- Python 3.9+
- Node.js 18+
- pnpm (recommended) or npm

### 1. Install Dependencies

**Backend:**
```bash
cd factory/server
pip install -r requirements.txt
```

**Frontend:**
```bash
cd factory/client
pnpm install
```

### 2. Start Services

**Option 1: Using scripts**
```bash
# Start backend
start_server.bat

# Start frontend (new terminal)
start_client.bat
```

**Option 2: Manual**
```bash
# Backend
cd factory/server
python run.py

# Frontend
cd factory/client
npm run dev
```

### 3. Access

Open browser at `http://localhost:5173`

### 4. Configure API

On first use, click the settings button (top right) to configure:
- API Key: Your LLM API key
- Base URL: API endpoint (OpenAI-compatible format)
- Model: Select the model to use

## Usage

1. Select prompt type (Programmer, AI Image, Customer Service, etc.)
2. Fill in or modify the requirement description
3. Click "Start Generate"
4. Wait for the agent pipeline to complete
5. Check generated prompt files in the results directory

## Project Structure

```
factory/
├── client/          # Frontend React app
├── server/          # Backend FastAPI service
│   ├── app/
│   │   ├── services/    # Core services (pipeline, llm, storage)
│   │   ├── routes/      # API routes
│   │   └── prompts/     # Agent prompt templates
│   └── results/         # Generated output directory
└── README.md
```
<img width="1289" height="859" alt="9176137369cda925eeb59c4fd7213c13" src="https://github.com/user-attachments/assets/9d740f9c-efa9-4c14-b868-048c11da0083" />

AI 提示词工厂 - 自动化生成高质量提示词套件

系统运行后会创建各种agent 需要的角色，负责不同的职能！

不是单一的提示词，是一整套agent 提示词工程！！！

## 项目简介

Prompt Factory 是一个基于多 Agent 协作的提示词生成系统。输入你的需求描述，系统会自动：

1. **分析需求** - Analyzer 拆解需求，设计系统架构和角色分工
2. **生成提示词** - Generator 为每个角色生成专业提示词
3. **质量审核** - Reviewer 评估提示词质量，打分并提出改进建议
4. **迭代优化** - Optimizer 根据审核结果优化提示词，直到达标

最终输出一套结构化的提示词文件，可直接用于各类 AI 应用。

## 功能特点

- 🚀 多 Agent 流水线自动化生成
- 🔄 审核-优化迭代循环，确保质量
- 💾 断点恢复，支持中断后继续
- 🌍 中英双语界面
- 📁 结果实时保存为 Markdown 文件

## 安装使用

### 环境要求

- Python 3.9+
- Node.js 18+
- pnpm（推荐）或 npm

### 1. 安装依赖

**后端：**
```bash
cd factory/server
pip install -r requirements.txt
```

**前端：**
```bash
cd factory/client
pnpm install
```

### 2. 启动服务

**方式一：使用启动脚本**
```bash
# 启动后端
start_server.bat

# 启动前端（新终端）
start_client.bat
```

**方式二：手动启动**
```bash
# 后端
cd factory/server
python run.py

# 前端
cd factory/client
npm run dev
```

### 3. 访问

打开浏览器访问 `http://localhost:5173`

### 4. 配置 API

首次使用时，点击右上角设置按钮，配置：
- API Key：你的 LLM API 密钥
- Base URL：API 地址（默认兼容 OpenAI 格式）
- 模型：选择要使用的模型

## 使用流程

1. 选择提示词类型（程序员助手、AI绘图、客服系统等）
2. 填写或修改需求描述
3. 点击「开始生成」
4. 等待 Agent 流水线执行完成
5. 在结果目录查看生成的提示词文件

## 目录结构

```
factory/
├── client/          # 前端 React 应用
├── server/          # 后端 FastAPI 服务
│   ├── app/
│   │   ├── services/    # 核心服务（pipeline, llm, storage）
│   │   ├── routes/      # API 路由
│   │   └── prompts/     # Agent 提示词模板
│   └── results/         # 生成结果输出目录
└── README.md
```
<img width="1289" height="855" alt="5c2e4984986f2a17ecc365703b684cba" src="https://github.com/user-attachments/assets/403f2623-5e21-4423-88c1-55c6cc434d54" />

