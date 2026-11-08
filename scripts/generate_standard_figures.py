#!/usr/bin/env python3
"""
generate_standard_figures.py
高考数学标准题图自动化生成与渲染引擎
1. 斜二测 3D 立体几何图生成 (四棱锥 P-ABCD, 严格遵循中国高考试卷虚实线与直角规范)
2. 高考黑白风格 统计频率分布直方图
3. 本地无头无依赖渲染管道: SVG -> 300 DPI 印刷级 PNG 固化
"""

import math
import os
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("/Volumes/ZHUOLIN/Project/INBOX/math_graphics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ==========================================
# 1. 立体几何矢量引擎 (斜二测画法 Axonometric)
# ==========================================
class StereometrySVG:
    def __init__(self, width=500, height=400, origin=(180, 280), scale=75, angle_deg=45, ratio=0.5):
        self.width = width
        self.height = height
        self.ox, self.oy = origin
        self.scale = scale
        self.angle = math.radians(angle_deg)
        self.ratio = ratio
        self.elements = []

    def project(self, x, y, z):
        """
        斜二测画法投影:
        x 轴: 倾斜 45 度向前偏左
        y 轴: 水平向右
        z 轴: 竖直向上
        """
        u = self.ox + y * self.scale - x * self.scale * self.ratio * math.cos(self.angle)
        v = self.oy - z * self.scale + x * self.scale * self.ratio * math.sin(self.angle)
        return round(u, 2), round(v, 2)

    def draw_line(self, p1, p2, dashed=False, stroke="#000000", stroke_width=1.8):
        u1, v1 = self.project(*p1)
        u2, v2 = self.project(*p2)
        dash = 'stroke-dasharray="5,4"' if dashed else ''
        self.elements.append(
            f'<line x1="{u1}" y1="{v1}" x2="{u2}" y2="{v2}" stroke="{stroke}" stroke-width="{stroke_width}" {dash} stroke-linecap="round" />'
        )

    def draw_right_angle(self, o, p1, p2, size=0.25, dashed=False, stroke="#000000"):
        """绘制空间折角直角符号"""
        v1 = [p1[i] - o[i] for i in range(3)]
        v2 = [p2[i] - o[i] for i in range(3)]
        l1 = math.sqrt(sum(x**2 for x in v1))
        l2 = math.sqrt(sum(x**2 for x in v2))
        if l1 == 0 or l2 == 0: return
        u1 = [x / l1 * size for x in v1]
        u2 = [x / l2 * size for x in v2]
        
        pt1 = [o[i] + u1[i] for i in range(3)]
        pt2 = [o[i] + u1[i] + u2[i] for i in range(3)]
        pt3 = [o[i] + u2[i] for i in range(3)]
        
        self.draw_line(pt1, pt2, dashed=dashed, stroke=stroke, stroke_width=1.2)
        self.draw_line(pt2, pt3, dashed=dashed, stroke=stroke, stroke_width=1.2)

    def draw_point(self, p, r=3.2, fill="#000000"):
        u, v = self.project(*p)
        self.elements.append(f'<circle cx="{u}" cy="{v}" r="{r}" fill="{fill}" />')

    def draw_label(self, p, text, offset=(0, 0), font_size=16, font_family="Times New Roman, STSong, serif"):
        u, v = self.project(*p)
        tx = u + offset[0]
        ty = v + offset[1]
        self.elements.append(
            f'<text x="{tx}" y="{ty}" font-size="{font_size}" font-style="italic" font-weight="bold" font-family="{font_family}" fill="#000000" text-anchor="middle">{text}</text>'
        )

    def render_svg(self):
        svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}" style="background-color: #ffffff;">\n'
        svg_content = "\n  ".join(self.elements)
        svg_footer = "\n</svg>"
        return svg_header + "  " + svg_content + svg_footer


def create_pyramid_diagram():
    """生成标准四棱锥 P-ABCD 题图 (PA 垂直底面 ABCD, 底面矩形)"""
    engine = StereometrySVG(width=480, height=420, origin=(200, 310), scale=85)
    
    # 空间顶点坐标 (x: 进深, y: 水平, z: 竖直)
    # A在原点后侧, B在原点前侧
    A = (0.0, 0.0, 0.0)      # 后左 (被遮挡)
    D = (0.0, 2.8, 0.0)      # 后右
    B = (2.0, 0.0, 0.0)      # 前左
    C = (2.0, 2.8, 0.0)      # 前右
    P = (0.0, 0.0, 3.2)      # 顶点 (PA 垂直底面)

    # 底面对角线交点 O
    O = (1.0, 1.4, 0.0)
    
    # 绘制棱 (遵循虚实线原则: 背后看不见的棱全画虚线)
    engine.draw_line(A, D, dashed=True)   # AD 背后棱 -> 虚线
    engine.draw_line(A, B, dashed=False)  # AB 侧边可见 -> 实线
    engine.draw_line(B, C, dashed=False)  # BC 前棱 -> 实线
    engine.draw_line(C, D, dashed=False)  # CD 右侧棱 -> 实线
    
    engine.draw_line(P, A, dashed=True)   # PA 高线在背后 -> 虚线
    engine.draw_line(P, B, dashed=False)  # PB 前棱 -> 实线
    engine.draw_line(P, C, dashed=False)  # PC 前棱 -> 实线
    engine.draw_line(P, D, dashed=False)  # PD 侧棱 -> 实线

    # 辅助线: 对角线 AC, BD
    engine.draw_line(A, C, dashed=True, stroke_width=1.2)
    engine.draw_line(B, D, dashed=True, stroke_width=1.2)
    engine.draw_line(P, O, dashed=True, stroke_width=1.2)

    # 直角标记: PA 垂直底面于 A
    engine.draw_right_angle(A, P, D, size=0.35, dashed=True)
    engine.draw_right_angle(A, P, B, size=0.35, dashed=True)

    # 标点
    for pt in [A, B, C, D, P, O]:
        engine.draw_point(pt)

    # 字母标签
    engine.draw_label(P, "P", offset=(0, -14))
    engine.draw_label(A, "A", offset=(-16, 2))
    engine.draw_label(B, "B", offset=(-14, 16))
    engine.draw_label(C, "C", offset=(14, 16))
    engine.draw_label(D, "D", offset=(18, -2))
    engine.draw_label(O, "O", offset=(4, 16))

    svg_str = engine.render_svg()
    svg_file = OUTPUT_DIR / "pyramid_P_ABCD.svg"
    svg_file.write_text(svg_str, encoding="utf-8")
    print(f"[OK] 生成立体几何 SVG: {svg_file}")
    return svg_file


# ==========================================
# 2. 统计直方图引擎 (Matplotlib 高考黑白风格)
# ==========================================
def create_histogram():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # 启用黑白试卷风格
    plt.rcParams["font.sans-serif"] = ["Songti SC", "SimSun", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(6, 4.2), dpi=300)
    
    bins = [50, 60, 70, 80, 90, 100]
    # 频率 / 组距
    heights = [0.005, 0.015, 0.035, 0.030, 0.015]
    # 频率验证: 10 * (0.005 + 0.015 + 0.035 + 0.030 + 0.015) = 10 * 0.100 = 1.0 (完美归一)

    widths = [10] * 5
    centers = [55, 65, 75, 85, 95]

    # 绘制矩形 (试卷标准细网纹/白底黑框)
    bars = ax.bar(centers, heights, width=widths, edgecolor="black", facecolor="#f3f4f6", linewidth=1.5)

    # 在各矩形上方标出高度数值
    for bar, h in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.001, f"{h:.3f}", ha="center", va="bottom", fontsize=10, family="Times New Roman")

    ax.set_xlim(45, 105)
    ax.set_ylim(0, 0.045)
    ax.set_xticks(bins)
    ax.set_xlabel("分数区间", fontsize=12, labelpad=8)
    ax.set_ylabel("频率 / 组距", fontsize=12, labelpad=8)

    # 模拟试卷坐标轴 (右上无框，左下实黑线)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)

    plt.tight_layout()
    hist_file = OUTPUT_DIR / "histogram_statistics.png"
    plt.savefig(hist_file, dpi=300)
    plt.close()
    print(f"[OK] 生成统计直方图 PNG: {hist_file}")
    return hist_file


# ==========================================
# 3. macOS 原生渲染管道 (SVG -> 高清 300DPI PNG)
# ==========================================
def render_svg_to_png(svg_path: Path):
    png_path = svg_path.with_suffix(".png")
    swift_script = f'''
import AppKit

let url = URL(fileURLWithPath: "{svg_path}")
guard let svgData = try? Data(contentsOf: url),
      let image = NSImage(data: svgData) else {{
    exit(1)
}}

let scale: CGFloat = 3.0 // 3倍高清超采样渲染 (达到 300+ DPI 印刷级)
let width = Int(image.size.width * scale)
let height = Int(image.size.height * scale)

let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: width,
    pixelsHigh: height,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .calibratedRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
)!

NSGraphicsContext.saveGraphicsState()
let ctx = NSGraphicsContext(bitmapImageRep: rep)
NSGraphicsContext.current = ctx

// 白色底板
NSColor.white.setFill()
NSRect(x: 0, y: 0, width: width, height: height).fill()

image.draw(in: NSRect(x: 0, y: 0, width: width, height: height))
NSGraphicsContext.restoreGraphicsState()

if let pngData = rep.representation(using: .png, properties: [:]) {{
    try? pngData.write(to: URL(fileURLWithPath: "{png_path}"))
    print("SUCCESS_RENDERED")
}}
'''
    res = subprocess.run(["swift", "-e", swift_script], capture_output=True, text=True)
    if "SUCCESS_RENDERED" in res.stdout:
        print(f"[OK] 原生极速固化为 PNG: {png_path}")
        return png_path
    else:
        print(f"[ERROR] 渲染失败: {res.stderr}")
        return None


if __name__ == "__main__":
    svg_f = create_pyramid_diagram()
    png_f = render_svg_to_png(svg_f)
    hist_f = create_histogram()
    print("\n✅ 所有标准图生成与渲染已全部闭环！")
