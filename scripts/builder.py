"""
网页构建器
将 AI 报告 JSON 渲染为完整的静态 HTML 页面
"""

import json
import os
import glob
from datetime import datetime


def build_html(report_data: dict, mode: str = "brief") -> str:
    """构建单页 HTML"""
    date_str = report_data.get("date", datetime.now().strftime("%Y-%m-%d"))
    sections = report_data.get("sections", {})

    # 格式化日期显示
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = f"{dt.year}年{dt.month}月{dt.day}日"
        weekday = dt.weekday()
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        display_date += f" {weekdays[weekday]}"
    except:
        display_date = date_str

    # 构建各板块的 HTML
    sections_html = ""

    # 板块顺序
    section_keys = ["macro", "industry_chain", "research", "tech", "opinion", "links"]

    for key in section_keys:
        section = sections.get(key, {})
        if not section:
            continue

        section_title = section.get("title", key)
        section_summary = section.get("summary", "")

        sections_html += f"""
        <div class="section" data-section="{key}">
            <div class="section-header">
                <h2>{section_title}</h2>
                <span class="section-toggle" onclick="toggleSection(this)">收起</span>
            </div>
            <div class="section-body">"""

        # 产业链特殊处理（有长文本 analysis）
        if key == "industry_chain":
            analysis = section.get("analysis", "")
            if analysis:
                paragraphs = analysis.replace("\n", "</p><p>")
                sections_html += f"""
                <div class="chain-analysis">
                    <p>{paragraphs}</p>
                </div>"""

        # 摘要
        if section_summary:
            if mode == "brief":
                sections_html += f'<p class="section-summary">{section_summary}</p>'

        # 具体条目
        items = section.get("items", [])
        if items:
            sections_html += '<div class="items-list">'
            for item in items:
                title = item.get("title", "")
                summary = item.get("summary", "")
                link = item.get("link", "")
                source = item.get("source", "")

                link_html = ""
                if link:
                    link_html = f'<a href="{link}" target="_blank" class="source-link" onclick="event.stopPropagation()">→ 原文</a>'

                source_html = f'<span class="source-tag">{source}</span>' if source else ""

                sections_html += f"""
                <div class="news-item" onclick="toggleDetail(this)">
                    <div class="item-header">
                        <span class="item-title">{title}</span>
                        <span class="item-meta">{source_html} {link_html}</span>
                    </div>
                    <div class="item-detail">
                        <p>{summary}</p>
                    </div>
                </div>"""
            sections_html += '</div>'

        sections_html += """
            </div>
        </div>"""

    # 当前时间
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 完整 HTML
    brief_btn = 'active' if mode == 'brief' else ''
    deep_btn = 'active' if mode == 'deep' else ''

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日财经透视 | {display_date}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="header">
        <div class="header-content">
            <h1>📈 每日财经透视</h1>
            <p class="date">{display_date}</p>
            <div class="mode-switcher">
                <button class="mode-btn {brief_btn}" onclick="switchMode('brief')" id="btn-brief">📋 简报版</button>
                <button class="mode-btn {deep_btn}" onclick="switchMode('deep')" id="btn-deep">🔍 深度版</button>
            </div>
            <p class="update-time">更新于 {now}</p>
        </div>
    </div>

    <div class="container">
        <div class="news-content" id="report-content">
            {sections_html}
        </div>
    </div>

    <div class="footer">
        <p>每日财经透视 · AI 自动生成 · 仅供学习参考，不构成投资建议</p>
    </div>

    <script src="script.js"></script>
</body>
</html>"""

    return html


def build_all(report_path: str, output_dir: str):
    """从报告 JSON 生成所有 HTML 页面"""
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    os.makedirs(output_dir, exist_ok=True)

    # 生成简报版
    brief_html = build_html(data, mode="brief")
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(brief_html)
    print(f"✅ 简报版已生成: {output_dir}/index.html")

    # 生成深度版
    deep_html = build_html(data, mode="deep")
    with open(os.path.join(output_dir, "deep.html"), "w", encoding="utf-8") as f:
        f.write(deep_html)
    print(f"✅ 深度版已生成: {output_dir}/deep.html")

    print(f"📊 报告日期: {date_str}")


if __name__ == "__main__":
    # 找到最新的报告
    files = sorted(glob.glob("data/report_*.json"), reverse=True)
    if not files:
        print("❌ 没有找到报告数据，请先运行 analyzer.py")
        exit(1)

    build_all(files[0], "site")
    print(f"\n💡 用浏览器打开 site/index.html 即可预览！")
