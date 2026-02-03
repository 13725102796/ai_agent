import subprocess
from .state import AgentState


def _ask_claude(prompt: str, system_prompt: str | None = None) -> str:
    """Call local Claude Code CLI and return text response."""
    import os
    from duckduckgo_search import DDGS
    env = os.environ.copy()
    env["PATH"] = "/Users/maidong/.local/bin:" + env.get("PATH", "")
    env["HOME"] = os.path.expanduser("~")

    cmd = ["/Users/maidong/.local/bin/claude", "-p", prompt, "--output-format", "text"]
    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    print(f"[DEBUG] Running: {cmd[:3]}...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
        stdin=subprocess.DEVNULL,
    )
    print(f"[DEBUG] returncode={result.returncode}, stdout_len={len(result.stdout)}, stderr_len={len(result.stderr)}")
    if result.stderr:
        print(f"[DEBUG] stderr: {result.stderr[:500]}")

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error: {result.stderr}")
    return result.stdout.strip()


def researcher_node(state: AgentState):
    topic = state["topic"]
    print(f"--- RESEARCHER: Analyzing {topic} ---")

    
    # Perform Real Web Search
    from duckduckgo_search import DDGS
    try:
        import json
        with DDGS() as ddgs:
            # text returns iterator of dicts
            search_items = list(ddgs.text(topic, max_results=5))
        research_context = json.dumps(search_items, ensure_ascii=False)
    except Exception as e:
        print(f"Search failed: {e}")
        research_context = f"无法访问外部网络，仅基于模型知识分析：{topic}"

    prompt = f"""你是一位顶级研究员。
    主题：'{topic}'

    参考以下搜索结果（如果为空则忽略）：
    {research_context}

    请用中文生成一份简洁的"知识简报"，包含：
    1. 关键事实与历史
    2. 未来影响
    3. 深层/哲学角度
    4. 引用来源（如果有）

    控制在300字以内。请用中文回答。
    """
    response = _ask_claude(prompt)
    return {"research_data": response}


def strategist_node(state: AgentState):
    print("--- STRATEGIST: Planning ---")
    research_data = state["research_data"]

    prompt = f"""你是一位文学策略师。
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

    请用中文回答。
    """
    response = _ask_claude(prompt)
    return {"strategy_prompt": response}


def writer_node(state: AgentState):
    print("--- WRITER: Drafting ---")
    strategy_response = state["strategy_prompt"]
    
    # Extract writer prompt
    system_prompt = strategy_response
    if "【作家提示词】" in strategy_response:
         parts = strategy_response.split("【作家提示词】")
         if len(parts) > 1:
             system_prompt = parts[1].strip()

    research_data = state["research_data"]

    prompt = f"""基于以下资料撰写文章：
    {research_data}

    请用中文写作，现在开始写。
    """
    response = _ask_claude(prompt, system_prompt=system_prompt)
    return {"draft": response}


def editor_node(state: AgentState):
    print("--- EDITOR: Polishing ---")
    draft = state["draft"]

    prompt = f"""你是一位诺贝尔奖级别的编辑。
    请润色以下草稿：
    {draft}

    规则：
    1. 提升词汇（使用更有表现力的词语）
    2. 修复行文和节奏
    3. 增添细腻的感官描写和深刻的情感共鸣
    4. 【重要】严格控制字数在用户期望的范围内（不要过短也不要过长）。如果原文太长，请精简；如果太短，请适当扩充。
    5. 必须保留文章的核心观点和依据。

    只输出最终润色后的版本。请用中文回答。
    """
    response = _ask_claude(prompt)
    return {"final_article": response}
