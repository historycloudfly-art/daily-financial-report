"""
AI 财经分析器
调用 DeepSeek API 对新闻进行产业链穿透分析
"""

import json
import os
import re
from datetime import datetime

from openai import OpenAI


def build_prompt(news_data: dict, mode: str = "brief") -> str:
    """构建发送给 AI 的提示词"""

    # 将新闻数据压缩成文本
    # 限制每类新闻数量，避免输出超长
    MAX_ITEMS = 8

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
        mode_instruction = "每条内容用 1-2 句话概括，保持简洁"
    else:
        mode_instruction = "每个板块写 200-300 字的深度分析，串联产业链上下游影响"

    prompt = f"""你是一位资深财经分析师。以下是今日采集的财经新闻原始素材，请按以下6个板块整理成一份中文财经早报。

日期：{news_data.get('date', datetime.now().strftime('%Y-%m-%d'))}

【中国财经媒体头条】
{china_text}

【全球财经媒体头条】
{global_text}

【科技媒体头条】
{tech_text}

【自媒体/社交媒体观点】
{social_text}

要求：
1. 按以下 JSON 格式输出，不要加 markdown 代码块标记，直接输出纯 JSON
2. 中文撰写，英文人名/术语保留原文（如 "Fed主席Powell"）
3. {mode_instruction}
4. 每条内容必须包含原文链接（从素材中提取）
5. "industry_chain" 板块要把各条新闻串联起来做产业链分析

输出格式：
{{
  "date": "{news_data.get('date', '')}",
  "mode": "{mode}",
  "sections": {{
    "macro": {{
      "title": "🌏 宏观风向",
      "summary": "整体概述（50字以内）",
      "items": [
        {{ "title": "新闻标题", "summary": "分析摘要", "link": "原文链接", "source": "来源名" }}
      ]
    }},
    "industry_chain": {{
      "title": "🏭 产业链透视",
      "summary": "今日核心产业链逻辑概述",
      "analysis": "详细的产业链穿透分析，将各条新闻关联起来...",
      "items": []
    }},
    "research": {{
      "title": "📊 机构研报摘要",
      "summary": "整体概述",
      "items": [
        {{ "title": "机构观点标题", "summary": "观点摘要", "link": "", "source": "机构名称" }}
      ]
    }},
    "tech": {{
      "title": "💡 前沿科技",
      "summary": "整体概述",
      "items": [
        {{ "title": "标题", "summary": "分析", "link": "链接", "source": "来源" }}
      ]
    }},
    "opinion": {{
      "title": "🗣 自媒体声音",
      "summary": "整体概述",
      "items": [
        {{ "title": "观点标题", "summary": "核心观点", "link": "链接", "source": "来源" }}
      ]
    }},
    "links": {{
      "title": "🔗 原文速览",
      "items": [
        {{ "title": "标题", "link": "原文链接", "source": "来源" }}
      ]
    }}
  }}
}}

请确保输出是**严格有效的 JSON**，不要包含任何额外文字。"""
    return prompt


def analyze(news_data: dict, api_key: str, mode: str = "brief") -> dict:
    """调用 DeepSeek API 分析新闻"""
    def _fallback(msg: str = "") -> dict:
        """AI 分析失败时的降级结果 — 直接将原始新闻标题展示出来"""
        # 从 news_data 提取原始新闻标题作为 items
        raw_items = []
        for section_key, section_name in [
            ("china_finance", ""), ("global_finance", ""), ("tech", ""), ("social_media", "")
        ]:
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
            "error": f"AI 分析暂不可用: {msg}",
            "sections": {
                "macro": {
                    "title": "🌏 宏观风向",
                    "summary": "AI 分析暂不可用，以下为原始新闻标题",
                    "items": [i for i in raw_items if "finance" in str(i.get("source","")).lower() or "第一财经" in i.get("source","") or "经济" in i.get("source","") or "CNBC" in i.get("source","") or "Bloomberg" in i.get("source","") or "Reuters" in i.get("source","") or "WSJ" in i.get("source","") or "FT" in i.get("source","")][:15],
                },
                "industry_chain": {
                    "title": "🏭 产业链透视",
                    "summary": "AI 分析暂不可用",
                    "analysis": "今日 AI 产业链分析因 API 调用异常暂不可用。请稍后刷新重试。",
                    "items": [],
                },
                "research": {"title": "📊 机构研报摘要", "summary": "暂不可用", "items": []},
                "tech": {
                    "title": "💡 前沿科技",
                    "summary": "以下为原始科技新闻",
                    "items": [i for i in raw_items if "tech" in str(i.get("source","")).lower() or "36氪" in i.get("source","") or "虎嗅" in i.get("source","") or "TechCrunch" in i.get("source","") or "Verge" in i.get("source","") or "Wired" in i.get("source","")][:10],
                },
                "opinion": {
                    "title": "🗣 自媒体声音",
                    "summary": "以下为原始自媒体内容",
                    "items": [i for i in raw_items if "YouTube" in i.get("source","") or "抖音" in i.get("source","") or "social" in str(i.get("source","")).lower()][:10],
                },
                "links": {
                    "title": "🔗 原文速览",
                    "items": [{"title": i["title"], "link": i["link"], "source": i.get("source","")} for i in raw_items[:30] if i.get("link")],
                },
            }
        }

    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
        )
    except Exception as e:
        print(f"⚠️ OpenAI 客户端初始化失败: {e}")
        return _fallback(str(e)[:100])

    prompt = build_prompt(news_data, mode)

    print(f"[DeepSeek] 正在分析新闻（{mode}模式）...")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的财经分析师，擅长产业链分析和宏观经济解读。请用中文输出严格的 JSON 格式。"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=8192,
        )
        content = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ DeepSeek API 调用失败: {e}")
        return _fallback(str(e)[:100])

    # 清理可能的 markdown 代码块标记
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    try:
        report = json.loads(content)
        report["mode"] = mode
        print("✅ DeepSeek 分析完成")
        return report
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON 解析失败: {e}")
        print(f"原始响应前200字符: {content[:200]}")
        return _fallback(f"JSON解析失败: {e}")


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

    # 找到最新的新闻数据
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
