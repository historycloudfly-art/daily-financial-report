"""
网页构建器 v2
将 AI 报告 JSON 渲染为紧凑专业的静态 HTML 页面
"""

import json
import os
import glob
from datetime import datetime, timedelta, timezone

BJT = timezone(timedelta(hours=8))
def beijing_now():
    return datetime.now(BJT)


def build_html(report_data: dict, mode: str = "brief") -> str:
    """构建单页 HTML"""
    if "brief" in report_data and "deep" in report_data:
        report_data = report_data.get(mode, report_data)

    date_str = report_data.get("date", beijing_now().strftime("%Y-%m-%d"))
    sections = report_data.get("sections", {})

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        display_date = f"{dt.year}年{dt.month}月{dt.day}日"
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        display_date += f" {weekdays[dt.weekday()]}"
    except:
        display_date = date_str

    sections_html = ""
    section_keys = ["macro", "markets", "industry_chain", "research", "tech", "opinion", "links"]

    for key in section_keys:
        section = sections.get(key, {})
        if not section:
            continue

        section_title = section.get("title", key)
        section_summary = section.get("summary", "")

        if key == "industry_chain":
            sections_html += f"""
        <div class="section" data-section="{key}">
            <div class="section-hd">
                <h2>{section_title}</h2>
                <span class="section-toggle" onclick="toggleSection(this)">−</span>
            </div>
            <div class="section-bd">
                <p class="section-summary">{section_summary}</p>"""

            main_lines = section.get("main_lines", [])
            for line in main_lines:
                theme = line.get("theme", "")
                chain = line.get("chain", "")
                bottleneck = line.get("bottleneck", "")
                verdict = line.get("verdict", "")

                sections_html += f"""
                <div class="chain-card">
                    <div class="chain-theme">{theme}</div>
                    <div class="chain-body">{chain}</div>"""
                if bottleneck:
                    sections_html += f'<div class="chain-bottleneck">⚠ 瓶颈/关键节点：{bottleneck}</div>'
                if verdict:
                    sections_html += f'<div class="chain-verdict">{verdict}</div>'
                sections_html += """
                </div>"""

            items = section.get("items", [])
            if items:
                sections_html += '<div class="items-list">'
                for item in items:
                    title = item.get("title", "")
                    summary = item.get("analysis", item.get("summary", ""))
                    link = item.get("link", "")
                    source = item.get("source", "")
                    link_html = f'<a href="{link}" target="_blank" class="src-link" onclick="event.stopPropagation()">→</a>' if link else ""
                    source_html = f'<span class="src-tag">{source}</span>' if source else ""
                    sections_html += f"""
                    <div class="item" onclick="toggleDetail(this)">
                        <div class="item-hd">
                            <span class="item-tt">{title}</span>
                            <span class="item-meta">{source_html} {link_html}</span>
                        </div>
                        <div class="item-bd"><p>{summary}</p></div>
                    </div>"""
                sections_html += '</div>'

            sections_html += """
            </div>
        </div>"""
            continue

        # 其他板块
        sections_html += f"""
        <div class="section" data-section="{key}">
            <div class="section-hd">
                <h2>{section_title}</h2>
                <span class="section-toggle" onclick="toggleSection(this)">−</span>
            </div>
            <div class="section-bd">"""

        if section_summary and mode == "brief":
            sections_html += f'<p class="section-summary">{section_summary}</p>'

        items = section.get("items", [])
        if items:
            sections_html += '<div class="items-list">'
            for item in items:
                title = item.get("title", "")
                analysis = item.get("analysis", item.get("summary", ""))
                link = item.get("link", "")
                source = item.get("source", "")
                link_html = f'<a href="{link}" target="_blank" class="src-link" onclick="event.stopPropagation()">→</a>' if link else ""
                source_html = f'<span class="src-tag">{source}</span>' if source else ""

                sections_html += f"""
                <div class="item" onclick="toggleDetail(this)">
                    <div class="item-hd">
                        <span class="item-tt">{title}</span>
                        <span class="item-meta">{source_html} {link_html}</span>
                    </div>
                    <div class="item-bd"><p>{analysis}</p></div>
                </div>"""
            sections_html += '</div>'

        sections_html += """
            </div>
        </div>"""

    now = beijing_now().strftime("%Y-%m-%d %H:%M")
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

<div class="topbar">
    <div class="topbar-inner">
        <h1>📈 每日财经透视</h1>
        <span class="topbar-date">{display_date}</span>
        <div class="mode-group">
            <button class="mode-btn {brief_btn}" onclick="switchMode('brief')">简报</button>
            <button class="mode-btn {deep_btn}" onclick="switchMode('deep')">深度</button>
        </div>
        <span class="topbar-upd">{now} 更新</span>
    </div>
</div>

<div class="container">
    <div class="report" id="report-content">{sections_html}</div>
</div>

<div class="footer">
    <p>每日财经透视 · AI 自动生成 · 仅供学习参考，不构成投资建议</p>
</div>

<script src="script.js"></script>
</body>
</html>"""
    return html


def build_all(report_path: str, output_dir: str):
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_str = data.get("date", beijing_now().strftime("%Y-%m-%d"))
    os.makedirs(output_dir, exist_ok=True)

    brief_html = build_html(data, mode="brief")
    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(brief_html)
    print(f"✅ 简报版: {output_dir}/index.html")

    deep_html = build_html(data, mode="deep")
    with open(os.path.join(output_dir, "deep.html"), "w", encoding="utf-8") as f:
        f.write(deep_html)
    print(f"✅ 深度版: {output_dir}/deep.html")

    print(f"📊 {date_str}")


if __name__ == "__main__":
    files = sorted(glob.glob("data/report_*.json"), reverse=True)
    if not files:
        print("❌ 没有报告数据，请先运行 analyzer.py")
        exit(1)
    build_all(files[0], "site")
    print("💡 打开 site/index.html 预览")
