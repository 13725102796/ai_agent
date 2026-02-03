from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import subprocess
import json
import os
from openai import OpenAI
import os
from openai import OpenAI
from ddgs import DDGS

app = FastAPI(title="LitAgent API")

# DeepSeek client
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TopicRequest(BaseModel):
    topic: str


@app.get("/")
async def root():
    return {"message": "LitAgent Backend is running"}


def stream_deepseek(prompt: str, system_prompt: str | None = None):
    """Stream DeepSeek API output."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    full_text = ""
    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=True,
        temperature=0.8,
        max_tokens=4096,
    )

    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            full_text += text
            yield {"type": "delta", "text": text}

    yield {"type": "complete", "text": full_text}


def stream_claude(prompt: str, system_prompt: str | None = None):
    """Stream Claude CLI output line by line."""
    env = os.environ.copy()
    env["PATH"] = "/Users/maidong/.local/bin:" + env.get("PATH", "")
    env["HOME"] = os.path.expanduser("~")

    cmd = [
        "/Users/maidong/.local/bin/claude",
        "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--include-partial-messages",
    ]
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        stdin=subprocess.DEVNULL,
    )

    full_text = ""
    for line in process.stdout:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            msg_type = data.get("type")

            # Stream text deltas
            if msg_type == "stream_event":
                event = data.get("event", {})
                if event.get("type") == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        full_text += text
                        yield {"type": "delta", "text": text}

            # Final result
            elif msg_type == "result":
                result_text = data.get("result", "")
                if not full_text:
                    full_text = result_text
                yield {"type": "complete", "text": full_text}

        except json.JSONDecodeError:
            continue

    process.wait()
    if not full_text:
        stderr = process.stderr.read()
        raise RuntimeError(f"Claude CLI error: {stderr}")


@app.post("/stream_generate")
async def stream_generate_article(request: TopicRequest):
    """Stream the article generation with real-time updates."""
    topic = request.topic

    def event_generator():
        # Stage 1: Researcher
        yield f"data: {json.dumps({'stage': 'researcher', 'status': 'start', 'message': '正在进行全网搜索...'})}\n\n"

        # Perform Real Web Search
        try:
            with DDGS() as ddgs:
                 search_items = list(ddgs.text(topic, max_results=5))
            
            # Format sources for display
            sources_display = []
            for idx, item in enumerate(search_items[:5], 1):
                title = item.get('title', 'Unknown')
                link = item.get('href', '#')
                sources_display.append(f"[{idx}] {title}")
            
            sources_text = "\\n".join(sources_display)
            if sources_text:
                yield f"data: {json.dumps({'stage': 'researcher', 'status': 'streaming', 'delta': f'找到 {len(search_items)} 个相关来源：\\n{sources_text}\\n\\n开始分析数据...\\n'})}\\n\\n"
            
            research_context = json.dumps(search_items, ensure_ascii=False)
        except Exception as e:
            print(f"Search failed: {e}")
            research_context = f"无法访问外部网络，仅基于模型知识分析：{topic}"
            yield f"data: {json.dumps({'stage': 'researcher', 'status': 'streaming', 'delta': '网络搜索失败，切换到内部知识库...\\n'})}\\n\\n"


        research_prompt = f"""你是一位顶级研究员。
主题：'{topic}'

参考以下搜索结果（如果为空则忽略）：
{research_context}

请用中文生成一份简洁的"知识简报"，包含：
1. 关键事实与历史
2. 未来影响
3. 深层/哲学角度
4. 引用来源（如果有）

控制在300字以内。请用中文回答。"""

        research_data = ""
        for chunk in stream_claude(research_prompt):
            if chunk["type"] == "delta":
                yield f"data: {json.dumps({'stage': 'researcher', 'status': 'streaming', 'delta': chunk['text']})}\n\n"
            elif chunk["type"] == "complete":
                research_data = chunk["text"]
                yield f"data: {json.dumps({'stage': 'researcher', 'status': 'complete', 'content': research_data})}\n\n"

        # Stage 2: Strategist
        yield f"data: {json.dumps({'stage': 'strategist', 'status': 'start', 'message': '制定写作策略...'})}\n\n"

        strategy_prompt = f"""你是一位文学策略师。
基于以下研究资料：
{research_data}

请先制定策略：
1. 风格选择（Style）：如诗意/忧郁、犀利/批判、远见/乐观等。
2. 结构选择（Structure）：如英雄之旅、SCQA、黄金圈法则等。
3. 核心依据（Rationale）：简述为什么要选择这种风格和结构（基于研究资料的哪个特点）。

最后，输出一段专门给作家的系统提示词（System Prompt）。
提示词要求：
- 包含具体的风格和结构指令
- 包含使用比喻和感官细节的要求
- 不要有其他废话

请按以下格式输出：
【策略分析】
...（这里写风格、结构和依据）...

【作家提示词】
...（这里写给作家的Prompt）...

请用中文回答。"""

        strategy_prompt_result = ""
        for chunk in stream_claude(strategy_prompt):
            if chunk["type"] == "delta":
                yield f"data: {json.dumps({'stage': 'strategist', 'status': 'streaming', 'delta': chunk['text']})}\n\n"
            elif chunk["type"] == "complete":
                strategy_prompt_result = chunk["text"]
                yield f"data: {json.dumps({'stage': 'strategist', 'status': 'complete', 'content': strategy_prompt_result})}\n\n"

        # Stage 3: Writer (使用 DeepSeek)
        yield f"data: {json.dumps({'stage': 'writer', 'status': 'start', 'message': '撰写草稿（DeepSeek）...'})}\n\n"

        
        # 简单解析一下策略师的输出，提取出 Prompt 用于 Writer
        # 如果策略师比较听话，应该有【作家提示词】标记
        writer_system_prompt = strategy_prompt_result
        if "【作家提示词】" in strategy_prompt_result:
             parts = strategy_prompt_result.split("【作家提示词】")
             if len(parts) > 1:
                 writer_system_prompt = parts[1].strip()

        writer_prompt = f"""基于以下资料撰写文章：
{research_data}

请用中文写作，文笔要优美、富有感染力。
注意：最终成文后的字数需要在1000-1500字之间，请充分展开论述，多用细节。

现在开始写。"""

        draft = ""
        for chunk in stream_deepseek(writer_prompt, system_prompt=writer_system_prompt):
            if chunk["type"] == "delta":
                yield f"data: {json.dumps({'stage': 'writer', 'status': 'streaming', 'delta': chunk['text']})}\n\n"
            elif chunk["type"] == "complete":
                draft = chunk["text"]
                yield f"data: {json.dumps({'stage': 'writer', 'status': 'complete', 'content': draft})}\n\n"

        # Stage 4: Editor (使用 DeepSeek)
        yield f"data: {json.dumps({'stage': 'editor', 'status': 'start', 'message': '润色打磨（DeepSeek）...'})}\n\n"

        editor_prompt = f"""你是一位诺贝尔奖级别的编辑，擅长用诗意而富有感染力的语言打磨文章。
请润色以下草稿：
{draft}

规则：
1. 提升词汇（使用更有表现力、更富文学性的词语）
2. 修复行文和节奏，让文章更有韵律感
3. 增添细腻的感官描写和深刻的情感共鸣
4. 【重要】严格控制字数在用户期望的范围内（不要过短也不要过长）。如果原文太长，请精简；如果太短，请适当扩充。
5. 必须保留文章的核心观点和依据。

只输出最终润色后的版本。请用中文回答。"""

        final_article = ""
        for chunk in stream_deepseek(editor_prompt):
            if chunk["type"] == "delta":
                yield f"data: {json.dumps({'stage': 'editor', 'status': 'streaming', 'delta': chunk['text']})}\n\n"
            elif chunk["type"] == "complete":
                final_article = chunk["text"]
                yield f"data: {json.dumps({'stage': 'editor', 'status': 'complete', 'content': final_article})}\n\n"

        # Done
        yield f"data: {json.dumps({'stage': 'done', 'final_article': final_article})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Keep the old non-streaming endpoint for compatibility
from graph.workflow import app as agent_app

@app.post("/generate")
async def generate_article(request: TopicRequest):
    """Run the agent workflow (non-streaming)."""
    inputs = {"topic": request.topic}
    try:
        result = agent_app.invoke(inputs)
        return {
            "status": "completed",
            "final_article": result.get("final_article"),
            "research_data": result.get("research_data"),
            "strategy": result.get("strategy_prompt"),
            "draft": result.get("draft")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
