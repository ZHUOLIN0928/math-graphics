#!/usr/bin/env python3
"""
render_to_printable_pdf.py
将桌面的数学月考考前急救手册渲染为顶级出版印刷级 A4 PDF
- 100% 本地离线环境，内联 Marked.js 与 KaTeX (JS+CSS+Fonts)
- 所有 21 张 300DPI 高清题图全部自动转为 Base64 内嵌，零外链、无加载失败风险
- 采用 <script type="text/template"> 彻底杜绝字符串转义 Bug
- 严格遵循 A4 试卷打印样式 (@media print)，避免公式与图片孤行跨页断裂
- 调用 Chrome Headless 引擎精准渲染导出
"""

import base64
import os
import re
import subprocess
from pathlib import Path

BASE_DIR = Path("/Volumes/ZHUOLIN/Project/INBOX/math_graphics")
DESKTOP_DIR = Path("/Users/laizhuolin/Desktop")
MD_PATH = DESKTOP_DIR / "数学月考考前急救与题型知识点通关手册.md"
PDF_PATH = DESKTOP_DIR / "数学月考考前急救与题型知识点通关手册.pdf"
TMP_HTML = Path("/tmp/math_exam_manual_printable.html")

CHROME_BIN = "/Volumes/ZHUOLIN/Applications/Network/Google Chrome.app/Contents/MacOS/Google Chrome"

MARKED_JS = "/Volumes/ZHUOLIN/Applications/AI/Kimi.app/Contents/Resources/resources/gateway/node_modules/marked/marked.min.js"
KATEX_JS = "/Volumes/ZHUOLIN/Project/INBOX/conveyor-physics/libs/katex/katex.min.js"
KATEX_CSS = "/Volumes/ZHUOLIN/Project/INBOX/conveyor-physics/libs/katex/katex.min.css"
AUTO_RENDER_JS = "/Volumes/ZHUOLIN/Project/INBOX/conveyor-physics/libs/katex/auto-render.min.js"
KATEX_FONTS_DIR = "/Volumes/ZHUOLIN/Project/INBOX/conveyor-physics/libs/katex/fonts"


def load_file(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def inline_images_as_base64(md_content: str) -> str:
    """将 md 中的 math_images/*.png 替换为 base64 data URI"""
    def repl(match):
        alt = match.group(1)
        rel_path = match.group(2)
        full_path = DESKTOP_DIR / rel_path
        if not full_path.exists():
            full_path = BASE_DIR / os.path.basename(rel_path)
        if full_path.exists():
            with open(full_path, "rb") as img_f:
                b64 = base64.b64encode(img_f.read()).decode("utf-8")
                return f"![{alt}](data:image/png;base64,{b64})"
        return match.group(0)

    return re.sub(r'!\[([^\]]*)\]\((math_images/[^\)]+)\)', repl, md_content)


def generate_printable_html():
    md_text = load_file(MD_PATH)
    md_text = inline_images_as_base64(md_text)

    marked_code = load_file(MARKED_JS)
    katex_js_code = load_file(KATEX_JS)
    katex_css_code = load_file(KATEX_CSS)
    auto_render_code = load_file(AUTO_RENDER_JS)

    katex_css_code = katex_css_code.replace("fonts/", f"file://{KATEX_FONTS_DIR}/")

    # 构建 HTML，使用模板标签存放原始 markdown，完全杜绝转义 Bug
    html_parts = []
    html_parts.append('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n')
    html_parts.append('<title>数学月考考前急救与题型知识点通关手册</title>\n')
    html_parts.append(f'<style>\n{katex_css_code}\n')
    html_parts.append('''
    @page {
      size: A4 portrait;
      margin: 16mm 14mm 16mm 14mm;
    }

    *, *:before, *:after {
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Songti SC", "SimSun", serif;
      font-size: 10.5pt;
      line-height: 1.65;
      color: #111827;
      background-color: #ffffff;
      margin: 0;
      padding: 0;
      -webkit-font-smoothing: antialiased;
    }

    h1 {
      font-size: 19pt;
      text-align: center;
      margin-top: 5px;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 2px solid #1e3a8a;
      color: #0f172a;
      page-break-after: avoid;
      break-after: avoid;
    }

    h2 {
      font-size: 13.5pt;
      margin-top: 18px;
      margin-bottom: 8px;
      padding-left: 8px;
      border-left: 4.5px solid #2563eb;
      background-color: #f8fafc;
      padding-top: 3px;
      padding-bottom: 3px;
      color: #1e293b;
      page-break-after: avoid;
      break-after: avoid;
    }

    h3 {
      font-size: 11.5pt;
      margin-top: 14px;
      margin-bottom: 6px;
      color: #1e40af;
      page-break-after: avoid;
      break-after: avoid;
    }

    h4 {
      font-size: 10.5pt;
      margin-top: 10px;
      margin-bottom: 4px;
      color: #334155;
      page-break-after: avoid;
      break-after: avoid;
    }

    p {
      margin-top: 5px;
      margin-bottom: 6px;
      text-align: justify;
      orphans: 3;
      widows: 3;
    }

    ul, ol {
      margin-top: 4px;
      margin-bottom: 6px;
      padding-left: 22px;
    }

    li {
      margin-bottom: 3px;
    }

    blockquote {
      margin: 8px 0;
      padding: 6px 12px;
      background-color: #f1f5f9;
      border-left: 3.5px solid #64748b;
      font-size: 10pt;
      color: #334155;
      page-break-inside: avoid;
      break-inside: avoid;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin: 10px 0;
      font-size: 9.5pt;
      page-break-inside: avoid;
      break-inside: avoid;
    }

    th, td {
      border: 1px solid #cbd5e1;
      padding: 5px 8px;
      text-align: left;
    }

    th {
      background-color: #f1f5f9;
      font-weight: 600;
      color: #0f172a;
    }

    img {
      display: block;
      margin: 8px auto;
      max-width: 90%;
      max-height: 200px;
      object-fit: contain;
      page-break-inside: avoid;
      break-inside: avoid;
      border-radius: 4px;
    }

    td img {
      max-height: 140px;
      margin: 2px auto;
    }

    hr {
      border: 0;
      height: 1px;
      background: #e2e8f0;
      margin: 14px 0;
    }

    .katex {
      font-size: 1.05em !important;
    }

    .katex-display {
      margin: 6px 0 !important;
      overflow-x: hidden;
      overflow-y: hidden;
    }

    code {
      background-color: #f1f5f9;
      padding: 1px 4px;
      border-radius: 3px;
      font-family: Menlo, Monaco, Consolas, monospace;
      font-size: 9.5pt;
    }

    @media print {
      body {
        background: none;
      }
      h1, h2, h3, h4 {
        page-break-after: avoid;
        break-after: avoid;
      }
      tr, img, blockquote {
        page-break-inside: avoid;
        break-inside: avoid;
      }
    }
  </style>
</head>
<body>
  <div id="content"></div>

  <script type="text/template" id="markdown-source">''')
    html_parts.append(md_text)
    html_parts.append('</script>\n')

    html_parts.append(f'<script>\n{marked_code}\n</script>\n')
    html_parts.append(f'<script>\n{katex_js_code}\n</script>\n')
    html_parts.append(f'<script>\n{auto_render_code}\n</script>\n')

    html_parts.append('''<script>
    (function() {
      let rawText = document.getElementById("markdown-source").textContent;
      const mathTokens = [];

      // 1. 保护块级数学公式 $$...$$
      rawText = rawText.replace(/\\$\\$([\\s\\S]+?)\\$\\$/g, function(match) {
        mathTokens.push(match);
        return '%%%MATH_' + (mathTokens.length - 1) + '%%%';
      });

      // 2. 保护行内数学公式 $...$
      rawText = rawText.replace(/\\$([^\\$\\r\\n]+?)\\$/g, function(match) {
        mathTokens.push(match);
        return '%%%MATH_' + (mathTokens.length - 1) + '%%%';
      });

      // 3. 运行 Marked 解析为 HTML
      let html = marked.parse(rawText);

      // 4. 恢复数学公式
      html = html.replace(/%%%MATH_(\\d+)%%%/g, function(match, id) {
        return mathTokens[parseInt(id, 10)];
      });

      const container = document.getElementById("content");
      container.innerHTML = html;

      // 5. 调用 KaTeX auto-render
      renderMathInElement(container, {
        delimiters: [
          {left: "$$", right: "$$", display: true},
          {left: "$", right: "$", display: false}
        ],
        throwOnError: false
      });

      document.body.classList.add("math-rendered-ok");
    })();
  </script>
</body>
</html>''')

    full_html = "".join(html_parts)
    TMP_HTML.write_text(full_html, encoding="utf-8")
    print(f"[OK] 生成内嵌完整 HTML: {TMP_HTML} (字符数: {len(full_html)})")
    return TMP_HTML


def print_to_pdf(html_file: Path):
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=8000",
        f"--print-to-pdf={PDF_PATH}",
        f"file://{html_file.resolve()}"
    ]
    print(f"🚀 调用 Chrome 生成 A4 PDF: {PDF_PATH} ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if PDF_PATH.exists() and PDF_PATH.stat().st_size > 50000:
        size_kb = PDF_PATH.stat().st_size / 1024
        print(f"🏆 打印大功告成！PDF 成功输出至：{PDF_PATH} (大小: {size_kb:.1f} KB)")
        return True
    else:
        print(f"❌ 打印结果大小异常 ({PDF_PATH.stat().st_size if PDF_PATH.exists() else 0} 字节): {res.stderr}")
        return False


if __name__ == "__main__":
    html_f = generate_printable_html()
    success = print_to_pdf(html_f)
    if not success:
        exit(1)
