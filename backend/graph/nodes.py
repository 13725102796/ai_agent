import subprocess
from .state import AgentState


def _ask_claude(prompt: str, system_prompt: str | None = None) -> str:
    """Call local Claude Code CLI and return text response."""
    import os
    from ddgs import DDGS
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
    from ddgs import DDGS
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

    请用中文生成一份结构化的"知识简报"，包含：
    1. 定义/身份（What is it?）
    2. 关键属性/特征（如性格、外观、参数等）
    3. 主要经历/功能/历史
    4. 核心亮点/评价
    5. 引用来源（如果有）

    请保持客观、中立，罗列事实数据，不要进行过度的哲学发散或文学渲染。
    控制在400字以内。
    """
    response = _ask_claude(prompt)
    return {"research_data": response}


def strategist_node(state: AgentState):
    print("--- STRATEGIST: Planning ---")
    research_data = state["research_data"]
    topic = state.get("topic", "")

    prompt = f"""你是一位高级内容策略师。
    用户的原始请求是：'{topic}'
    
    基于以下研究资料：
    {research_data}

    请先判断用户意图和最佳写作风格：
    1. **百科简介模式**：如果用户请求“简介”、“介绍”、“谁是...”、“...是什么”，必须选择此模式。
       - 目标：快速获取信息。
       - 风格：客观、中立、结构化、高信息密度。
       - 格式：推荐使用 实体+属性 的列表形式，或简短的段落。
    
    2. **文学故事模式**：只有当用户明确请求“写一个故事”、“写一段描写”、“散文”时才使用。
       - 目标：沉浸式体验。
       - 风格：感性、细腻、有画面感。

    3. **深度分析模式**：如果用户请求“分析”、“评价”、“为什么”，使用此模式。

    请制定策略：
    1. 风格选择（Style）：明确是百科简介、文学故事还是深度分析。
    2. 结构选择（Structure）：如“总-分-总”、“属性列表”、“时间线”等。
    3. 核心依据（Rationale）：简述选择理由。

    最后，输出一段专门给作家的系统提示词（System Prompt）。
    
    **如果判定为【百科简介模式】，System Prompt 必须包含以下要求：**
    - 严禁使用华丽的辞藻、比喻、煽情。
    - 严禁使用“仿佛”、“宛如”、“那一刻”等文学性连接词。
    - 使用 Markdown 格式，多用无序列表（- ）来罗列信息。
    - 结构建议：第一段定义；第二段核心属性；第三段主要经历/功能。
    
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

    prompt = f"""你是一位资深主编。
    请润色以下草稿：
    {draft}

    规则：
    1. 根据文章类型进行针对性优化：
       - 如果是【简介/百科】：确保语言简洁、客观、准确，去除多余的修饰和煽情，增强信息密度。
       - 如果是【文学/故事】：优化文笔，增强感染力。
    2. 修复行文和节奏，使其通顺流畅。
    3. 【重要】严格控制字数在用户期望的范围内。
    4. 必须保留文章的核心观点和事实信息。

    只输出最终润色后的版本。请用中文回答。
    """
    response = _ask_claude(prompt)
    return {"final_article": response}
