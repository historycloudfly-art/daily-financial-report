"""
AI 财经分析器 v2
调用 DeepSeek API 对新闻进行深度产业链穿透分析
"""

import json
import os
import re
from datetime import datetime

from openai import OpenAI


def build_prompt(news_data: dict, mode: str = "brief") -> str:
    """构建发送给 AI 的高质量分析提示词"""

    MAX_ITEMS = 20

    china_text = ""
    for item in news_data.get("sections", {}).get("china_finance", [])[:MAX_ITEMS]:
        china_text += f"- [{item['source']}] {item['title']}\n"

    global_text = ""
    for item in news_data.get("sections", {}).get("global_finance", [])[:MAX_ITEMS]:
        global_text += f"- [{item['source']}] {item['title']}\n"

    tech_text = ""
    for item in news_data.get("sections", {}).get("tech", [])[:MAX_ITEMS]:
        tech_text += f"- [{item['source']}] {item['title']}\n"

    social_text = ""
    for item in news_data.get("sections", {}).get("social_media", [])[:MAX_ITEMS]:
        social_text += f"- [{item['source']}] {item['title']}\n"

    mode_instruction = ""
    if mode == "brief":
        mode_instruction = """
- 每条新闻用 1-2 句写出核心逻辑，**必须包含明确的投资含义或产业影响判断**
- 避免"可能""有望"等模糊表述，给出明确的看多/看空/中性立场

示例好写法：
"摩根大通部署AI代理 → 利好AI算力基础设施（英伟达、AMD），利空传统BPO服务商。金融IT支出结构正在发生根本性转变。"

示例差写法（禁止）：
"摩根大通加速AI应用，提升金融服务效率。"（太浅、无观点）"""
    else:
        mode_instruction = """
每条新闻写 100-150 字深度分析，要求：
1. 点出事件本质（不只是发生了什么，而是为什么重要）
2. 产业链传导路径（上游什么受益/受损，下游什么受益/受损）
3. 给出明确的多空判断和投资含义
4. 与近期其他事件形成关联（如果相关）

示例好写法：
"摩根大通宣布部署AI代理。实质是华尔街正从'AI试点'进入'AI规模部署'阶段，信号意义重大。
上游看：AI基础设施（GPU、数据中心、电力）需求确定性增强，英伟达、博通等供应商继续受益。
下游看：传统金融IT外包商（如Infosys、埃森哲金融板块）面临结构性替代风险。
横向看：若摩根大通率先跑通AI代理，高盛、花旗将被迫跟进，形成行业级资本开支周期。
投资含义：做多AI基础设施，做空传统IT服务商。"

示例差写法（禁止）：
"摩根大通加速AI应用，提升效率，利好AI板块。"（太浅、无产业链视角、无观点）"""

    prompt = f"""你是一位在华尔街和国内头部券商拥有20年经验的首席经济学家兼策略分析师。以下是今日采集的全球财经新闻原始素材。请以专业投资研究的标准，按以下6个板块整理成一份中文财经日报。

日期：{news_data.get('date', datetime.now().strftime('%Y-%m-%d'))}

【中国财经媒体头条】
{china_text}

【全球财经媒体头条】
{global_text}

【科技媒体头条】
{tech_text}

【社交媒体/知名投资人观点】
{social_text}

===== 分析质量硬性要求 =====

{mode_instruction}

===== 板块特殊要求 =====

【🌏 宏观风向】
每条必须包含：核心逻辑 + 看多/看空/中性判断 + 资产含义
内容覆盖：利率政策、经济数据、地缘风险、监管变化

【🏭 产业链透视 - 这是全文核心板块】
写一篇 400-600 字的分析，要求：
1. 识别当日最重要的 2-3 条产业链逻辑主线
2. 每条主线画出：上游输入 → 中游制造/服务 → 下游需求 的传导链
3. 对每条链给出可操作的投资判断（哪些子行业受益/受损）
4. 横向交叉：指出不同产业链之间的相互影响
5. 如果产业链中存在瓶颈环节或边际变化最大的节点，明确标出

【📊 机构研报摘要】
基于新闻素材识别高盛、摩根士丹利、摩根大通、中金、中信等头部机构的隐含观点
每条写明：机构名称 + 核心判断 + 对投资的影响
如果没有直接研报，基于其公开言论和立场做合理推断，并在开头标注"据推断"

【💡 前沿科技】
每条约100字，写出：技术本质 + 产业化进度（实验/早期/规模） + 受益方向

【🗣 知名人士观点】
基于新闻素材和你的知识，整理以下知名投资人和财经人士的核心观点/立场：
- Cathie Wood（ARK Invest）：侧重颠覆性创新和AI
- Elon Musk：侧重科技趋势和宏观判断
- Ray Dalio（桥水）：侧重宏观经济和债务周期
- 但斌（东方港湾）：侧重中国科技和消费
- 李蓓（半夏投资）：侧重宏观对冲
- 其他相关知名人士
若素材中无法直接提取，根据该人士近期公开言论做一致推断，写明"据近期言论"

【🔗 原文速览】
按来源分组的链接汇总

===== 输出格式 =====
严格输出以下 JSON 格式，不要包含任何额外文字：
{{{{
  "date": "{news_data.get('date', '')}",
  "mode": "{mode}",
  "sections": {{{{
    "macro": {{{{
      "title": "🌏 宏观风向",
      "summary": "50字以内今日宏观核心判断",
      "items": [
        {{{{
          "title": "事件标题",
          "analysis": "核心逻辑 + 立场判断 + 资产含义",
          "link": "原文链接",
          "source": "来源"
        }}}}
      ]
    }}}},
    "industry_chain": {{{{
      "title": "🏭 产业链透视",
      "summary": "今日核心产业链逻辑概述",
      "main_lines": [
        {{{{
          "theme": "产业链主线1主题",
          "chain": "上游→中游→下游传导路径描述",
          "bottleneck": "瓶颈节点或边际变化最大的节点",
          "verdict": "明确的投资判断：受益/受损方向",
          "items": []
        }}}}
      ]
    }}}},
    "research": {{{{
      "title": "📊 机构研报摘要",
      "summary": "整体概述",
      "items": [
        {{{{
          "title": "机构观点标题",
          "analysis": "核心判断及对投资的影响",
          "link": "",
          "source": "机构名称"
        }}}}
      ]
    }}}},
    "tech": {{{{
      "title": "💡 前沿科技",
      "summary": "整体概述",
      "items": [
        {{{{
          "title": "技术标题",
          "analysis": "技术本质 + 产业化进度 + 受益方向",
          "link": "链接",
          "source": "来源"
        }}}}
      ]
    }}}},
    "opinion": {{{{
      "title": "🗣 知名人士观点",
      "summary": "整体概述",
      "items": [
        {{{{
          "title": "人物/观点标题",
          "analysis": "核心观点和立场",
          "link": "",
          "source": "人物名"
        }}}}
      ]
    }}}},
    "links": {{{{
      "title": "🔗 原文速览",
      "items": [
        {{{{
          "title": "标题",
          "link": "原文链接",
          "source": "来源"
        }}}}
      ]
    }}}}
  }}}}
}}}}

请确保：
1. 每板块至少 10 条，最多不超 20 条
2. 以中文撰写，英文人名/术语保留原文
3. 每条内容携带明确的判断和立场
4. 产业链板块必须有深度穿透分析，不是泛泛而谈
5. 知名人士板块真实引用可验证的观点
"""

    return prompt


def _fallback(news_data: dict, mode: str, msg: str = "") -> dict:
    """AI 分析失败时的降级结果"""
    raw_items = []
    for section_key in ["china_finance", "global_finance", "tech", "social_media"]:
        for item in news_data.get("sections", {}).get(section_key, []):
            raw_items.append({
                "title": item.get("title", ""),
                "summary": item.get("summary", "")[:200],
                "link": item.get("link", ""),
                "source": item.get("source", ""),
            })

    return {
        "date": news_data.get("date", ""),
        "mode": mode,
        "error": f"AI分析暂不可用: {msg}",
        "sections": {
            "macro": {
                "title": "🌏 宏观风向",
                "summary": "AI分析暂不可用，以下为原始新闻",
                "items": [{"title": i["title"], "analysis": i["summary"], "link": i["link"], "source": i.get("source","")} for i in raw_items[:20]],
            },
            "industry_chain": {
                "title": "🏭 产业链透视",
                "summary": "暂不可用",
                "main_lines": [{"theme": "分析暂不可用", "chain": "请稍后刷新重试", "bottleneck": "", "verdict": "", "items": []}],
            },
            "research": {"title": "📊 机构研报摘要", "summary": "暂不可用", "items": []},
            "tech": {
                "title": "💡 前沿科技",
                "summary": "以下为原始新闻",
                "items": [{"title": i["title"], "analysis": i["summary"], "link": i["link"], "source": i.get("source","")} for i in raw_items if any(k in str(i.get("source","")).lower() for k in ["36氪","虎嗅","tech","verge","wired","youtube"])][:20],
            },
            "opinion": {
                "title": "🗣 知名人士观点",
                "summary": "暂不可用",
                "items": [],
            },
            "links": {
                "title": "🔗 原文速览",
                "items": [{"title": i["title"], "link": i["link"], "source": i.get("source","")} for i in raw_items[:30] if i.get("link")],
            },
        }
    }


def analyze(news_data: dict, api_key: str, mode: str = "brief") -> dict:
    """调用 DeepSeek API 分析新闻"""
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    except Exception as e:
        print(f"⚠️ OpenAI 客户端初始化失败: {e}")
        return _fallback(news_data, mode, str(e)[:100])

    prompt = build_prompt(news_data, mode)

    print(f"[DeepSeek] 正在分析新闻（{mode}模式）...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位顶级首席经济学家兼策略分析师。你必须严格按照用户要求的格式输出 JSON，每条分析都传递有信息量的判断和立场，拒绝模棱两可。"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=8192,
        )
        content = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ DeepSeek API 调用失败: {e}")
        return _fallback(news_data, mode, str(e)[:100])

    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    try:
        report = json.loads(content)
        report["mode"] = mode
        print("✅ DeepSeek 分析完成")
        return report
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 解析失败: {e}")
        print(f"响应前300字符: {content[:300]}")
        return _fallback(news_data, mode, f"JSON解析失败: {e}")


def generate_brief_and_deep(news_data: dict, api_key: str) -> dict:
    """同时生成简报版和深度版"""
    brief = analyze(news_data, api_key, mode="brief")
    deep = analyze(news_data, api_key, mode="deep")
    return {"brief": brief, "deep": deep, "date": news_data.get("date", "")}


if __name__ == "__main__":
    import glob

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 请设置环境变量 DEEPSEEK_API_KEY")
        exit(1)

    files = sorted(glob.glob("data/news_*.json"), reverse=True)
    if not files:
        print("❌ 没有找到新闻数据，请先运行 collector.py")
        exit(1)

    with open(files[0], "r", encoding="utf-8") as f:
        news_data = json.load(f)

    result = generate_brief_and_deep(news_data, api_key)

    os.makedirs("data", exist_ok=True)
    path = f"data/report_{result['date']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 报告已保存到 {path}")
