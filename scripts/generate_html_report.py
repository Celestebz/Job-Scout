#!/usr/bin/env python3
"""
生成 Job Scout HTML 报告
从 xlsx 文件读取数据并生成可在 GitHub Pages 显示的 HTML
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# 尝试导入 openpyxl，如果失败则生成简单的 HTML
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


def generate_simple_html_report(project_root: Path) -> str:
    """生成简单的 HTML 报告"""
    result_dir = project_root / "result"
    logs_dir = project_root / "logs"

    # 获取最新的 xlsx 文件
    xlsx_files = list(result_dir.glob("*.xlsx"))
    if not xlsx_files:
        return None

    latest_xlsx = max(xlsx_files, key=lambda p: p.stat().st_mtime)
    xlsx_filename = latest_xlsx.name

    # 读取执行摘要
    summary_text = ""
    summary_file = logs_dir / "last-run-summary.txt"
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_text = f.read()

    # 读取数据库统计
    db_stats = {"total_jobs": 0, "last_updated": "N/A"}
    job_history_file = project_root / "job_history.json"
    if job_history_file.exists():
        try:
            with open(job_history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                db_stats["total_jobs"] = data.get("total_jobs", 0)
                db_stats["last_updated"] = data.get("last_updated", "N/A")
        except:
            pass

    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Scout 职位侦察报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
        }}
        .stat-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary pre {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .download-btn {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .download-btn:hover {{
            background: #45a049;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Job Scout 职位侦察报告</h1>
        <p>更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <h3>📊 数据库总岗位数</h3>
            <div class="value">{db_stats['total_jobs']}</div>
        </div>
        <div class="stat-card">
            <h3>🕐 最后更新</h3>
            <div class="value">{db_stats['last_updated'][:10] if db_stats['last_updated'] != 'N/A' else 'N/A'}</div>
        </div>
        <div class="stat-card">
            <h3>📁 报告文件</h3>
            <div class="value"><a href="result/{xlsx_filename}" style="color: #667eea; text-decoration: none;">下载 XLSX</a></div>
        </div>
    </div>

    <div class="summary">
        <h2>📋 执行摘要</h2>
        <pre>{summary_text}</pre>
    </div>

    <div class="footer">
        <p>🤖 由 GitHub Actions 自动生成 | <a href="https://github.com/Celestebz/Job-Scout">查看项目</a></p>
    </div>
</body>
</html>
"""
    return html


def main():
    """主函数"""
    project_root = Path(__file__).parent.parent
    result_dir = project_root / "result"

    # 生成 HTML 报告
    html = generate_simple_html_report(project_root)

    if html:
        # 保存 HTML 文件
        html_file = result_dir / "index.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ HTML 报告已生成: {html_file}")

        # 同时保存到 docs 目录（用于 GitHub Pages）
        docs_dir = project_root / "docs"
        docs_dir.mkdir(exist_ok=True)
        docs_html = docs_dir / "index.html"
        with open(docs_html, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ GitHub Pages 报告已生成: {docs_html}")
    else:
        print("⚠️ 没有找到 XLSX 文件，跳过 HTML 生成")
        sys.exit(1)


if __name__ == "__main__":
    main()
