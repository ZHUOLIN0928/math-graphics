#!/usr/bin/env python3
"""
draw_full_geometry_library.py
高考数学全题型标准题图与核心模型全图库生成器
覆盖：
1. 平面向量四大核心法则与概念 (加法、减法、正交坐标分解、数量积几何意义)
2. 解三角形两大实际测量与定理模型 (外接圆正弦定理、仰角俯角测量)
3. 立体几何全部核心公理与判定/性质定理 (异面直线角、线面平行判定与性质、面面平行判定、线面垂直判定与性质、二面角平面角、面面垂直判定)
4. 典型立体几何构型 (正方体及截面、直三棱柱、正四棱锥)
5. 统计与概率 (频率分布直方图、样本空间树状图)

生成标准 SVG 并调用 macOS 原生 AppKit 渲染为 300+ DPI 印刷级 PNG。
"""

import math
import os
import subprocess
from pathlib import Path

OUTPUT_DIR = Path("/Volumes/ZHUOLIN/Project/INBOX/math_graphics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DESKTOP_DIR = Path("/Users/laizhuolin/Desktop/math_images")
DESKTOP_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 基础矢量绘图画布基类
# -------------------------------------------------------------
class SVGCanvas:
    def __init__(self, width=460, height=340, bg="#ffffff"):
        self.width = width
        self.height = height
        self.bg = bg
        self.elements = []
        self.defs = []
        self._init_defs()

    def _init_defs(self):
        self.defs.append('''
    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#000000" />
      </marker>
      <marker id="arrow-blue" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#2563eb" />
      </marker>
      <marker id="arrow-red" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#dc2626" />
      </marker>
    </defs>
''')

    def add_line(self, p1, p2, dashed=False, stroke="#000000", width=1.6, arrow=False, arrow_color=""):
        dash = 'stroke-dasharray="5,4"' if dashed else ''
        marker = f'marker-end="url(#{arrow_color if arrow_color else "arrow"})"' if arrow else ''
        self.elements.append(
            f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" stroke="{stroke}" stroke-width="{width}" {dash} {marker} stroke-linecap="round" />'
        )

    def add_polygon(self, pts, fill="rgba(240, 240, 240, 0.5)", stroke="#000000", width=1.5):
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in pts])
        self.elements.append(
            f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" />'
        )

    def add_circle(self, p, r=3.0, fill="#000000", stroke="none"):
        self.elements.append(
            f'<circle cx="{p[0]}" cy="{p[1]}" r="{r}" fill="{fill}" stroke="{stroke}" />'
        )

    def add_text(self, p, text, offset=(0, 0), size=15, italic=True, bold=True, anchor="middle", fill="#000000"):
        tx = p[0] + offset[0]
        ty = p[1] + offset[1]
        it = 'font-style="italic"' if italic else ''
        bd = 'font-weight="bold"' if bold else ''
        self.elements.append(
            f'<text x="{tx}" y="{ty}" font-size="{size}" {it} {bd} font-family="Times New Roman, STSong, serif" fill="{fill}" text-anchor="{anchor}">{text}</text>'
        )

    def add_arc(self, center, r, start_ang, end_ang, stroke="#000000", width=1.2, dashed=False):
        """圆弧角标记"""
        x1 = center[0] + r * math.cos(math.radians(start_ang))
        y1 = center[1] + r * math.sin(math.radians(start_ang))
        x2 = center[0] + r * math.cos(math.radians(end_ang))
        y2 = center[1] + r * math.sin(math.radians(end_ang))
        dash = 'stroke-dasharray="3,3"' if dashed else ''
        d = f"M {x1} {y1} A {r} {r} 0 0 1 {x2} {y2}"
        self.elements.append(f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" fill="none" {dash} />')

    def save(self, filename):
        defs_str = "".join(self.defs)
        elems_str = "\n  ".join(self.elements)
        svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" width="{self.width}" height="{self.height}" style="background-color: {self.bg};">
{defs_str}
  {elems_str}
</svg>'''
        fpath = OUTPUT_DIR / filename
        fpath.write_text(svg_content, encoding="utf-8")
        return fpath


# -------------------------------------------------------------
# 立体几何斜二测投影引擎
# -------------------------------------------------------------
class StereoEngine:
    def __init__(self, origin=(200, 240), scale=75, angle_deg=45, ratio=0.5):
        self.ox, self.oy = origin
        self.scale = scale
        self.angle = math.radians(angle_deg)
        self.ratio = ratio

    def p(self, x, y, z):
        u = self.ox + y * self.scale - x * self.scale * self.ratio * math.cos(self.angle)
        v = self.oy - z * self.scale + x * self.scale * self.ratio * math.sin(self.angle)
        return round(u, 2), round(v, 2)


# =============================================================
# 一、平面向量板块矢量图 (4 张)
# =============================================================
def gen_vector_diagrams():
    # 1. 向量加法 (平行四边形法则与三角形法则对比)
    cv = SVGCanvas(width=480, height=260)
    # 左图: 平行四边形法则
    O = (60, 180)
    A = (180, 180)
    B = (120, 90)
    C = (240, 90)
    cv.add_line(O, A, arrow=True, width=2.0)
    cv.add_line(O, B, arrow=True, width=2.0)
    cv.add_line(B, C, dashed=True, stroke="#666666")
    cv.add_line(A, C, dashed=True, stroke="#666666")
    cv.add_line(O, C, arrow=True, stroke="#dc2626", width=2.2, arrow_color="arrow-red")
    cv.add_text(O, "O", offset=(-12, 16))
    cv.add_text(A, "A", offset=(12, 16))
    cv.add_text(B, "B", offset=(-12, -8))
    cv.add_text(C, "C", offset=(12, -8))
    cv.add_text(((O[0]+A[0])/2, O[1]), "a", offset=(0, 18))
    cv.add_text(((O[0]+B[0])/2, (O[1]+B[1])/2), "b", offset=(-16, -6))
    cv.add_text(((O[0]+C[0])/2, (O[1]+C[1])/2), "a + b", offset=(-10, -14), fill="#dc2626")
    cv.add_text((150, 235), "平行四边形法则 (共起点)", size=14, italic=False, bold=False)

    # 右图: 三角形法则 (首尾相连)
    P = (290, 180)
    Q = (390, 180)
    R = (430, 90)
    cv.add_line(P, Q, arrow=True, width=2.0)
    cv.add_line(Q, R, arrow=True, width=2.0)
    cv.add_line(P, R, arrow=True, stroke="#dc2626", width=2.2, arrow_color="arrow-red")
    cv.add_text(P, "A", offset=(-12, 16))
    cv.add_text(Q, "B", offset=(0, 18))
    cv.add_text(R, "C", offset=(12, -8))
    cv.add_text(((P[0]+Q[0])/2, P[1]), "a", offset=(0, 18))
    cv.add_text(((Q[0]+R[0])/2, (Q[1]+R[1])/2), "b", offset=(16, 0))
    cv.add_text(((P[0]+R[0])/2, (P[1]+R[1])/2), "a + b", offset=(-18, -10), fill="#dc2626")
    cv.add_text((370, 235), "三角形法则 (首尾接)", size=14, italic=False, bold=False)
    cv.save("vec_01_addition.svg")

    # 2. 向量减法 (共起点指向被减)
    cv = SVGCanvas(width=380, height=260)
    O = (80, 180)
    A = (240, 180)
    B = (180, 70)
    cv.add_line(O, A, arrow=True, width=2.0)
    cv.add_line(O, B, arrow=True, width=2.0)
    cv.add_line(B, A, arrow=True, stroke="#2563eb", width=2.2, arrow_color="arrow-blue")
    cv.add_text(O, "O", offset=(-14, 14))
    cv.add_text(A, "A", offset=(14, 14))
    cv.add_text(B, "B", offset=(0, -12))
    cv.add_text(((O[0]+A[0])/2, O[1]), "a", offset=(0, 18))
    cv.add_text(((O[0]+B[0])/2, (O[1]+B[1])/2), "b", offset=(-16, -6))
    cv.add_text(((B[0]+A[0])/2, (B[1]+A[1])/2), "a - b (指向被减数A)", offset=(45, -10), fill="#2563eb")
    cv.add_text((190, 235), "向量减法: OA - OB = BA", size=14, italic=False, bold=False)
    cv.save("vec_02_subtraction.svg")

    # 3. 向量正交坐标分解
    cv = SVGCanvas(width=380, height=280)
    O = (80, 200)
    X = (340, 200)
    Y = (80, 40)
    cv.add_line(O, X, arrow=True, width=1.5)
    cv.add_line(O, Y, arrow=True, width=1.5)
    cv.add_text(X, "x", offset=(14, 4))
    cv.add_text(Y, "y", offset=(-4, -14))
    cv.add_text(O, "O", offset=(-14, 16))

    P = (260, 90)
    Px = (260, 200)
    Py = (80, 90)
    cv.add_line(O, P, arrow=True, stroke="#dc2626", width=2.2, arrow_color="arrow-red")
    cv.add_line(P, Px, dashed=True, stroke="#666666")
    cv.add_line(P, Py, dashed=True, stroke="#666666")
    cv.add_text(Px, "x", offset=(0, 16))
    cv.add_text(Py, "y", offset=(-14, 4))
    cv.add_text(P, "P(x, y)", offset=(25, -6))
    cv.add_text(((O[0]+P[0])/2, (O[1]+P[1])/2), "a", offset=(-14, -10), fill="#dc2626")

    # 单位基底 i, j
    cv.add_line(O, (130, 200), arrow=True, stroke="#2563eb", width=2.4, arrow_color="arrow-blue")
    cv.add_line(O, (80, 150), arrow=True, stroke="#2563eb", width=2.4, arrow_color="arrow-blue")
    cv.add_text((115, 200), "i", offset=(0, 16), fill="#2563eb")
    cv.add_text((80, 175), "j", offset=(-14, 0), fill="#2563eb")
    cv.add_text((190, 255), "a = x i + y j = (x, y)", size=14, italic=False, bold=False)
    cv.save("vec_03_decomp_coord.svg")

    # 4. 向量数量积与投影
    cv = SVGCanvas(width=380, height=240)
    O = (70, 170)
    A = (310, 170)
    B = (220, 60)
    H = (220, 170)
    cv.add_line(O, A, arrow=True, width=2.0)
    cv.add_line(O, B, arrow=True, stroke="#dc2626", width=2.2, arrow_color="arrow-red")
    cv.add_line(B, H, dashed=True, stroke="#666666", width=1.5)
    # 直角标记
    cv.add_line((208, 170), (208, 158), stroke="#666666")
    cv.add_line((208, 158), (220, 158), stroke="#666666")
    cv.add_text(O, "O", offset=(-14, 14))
    cv.add_text(A, "b", offset=(14, 0))
    cv.add_text(B, "a", offset=(0, -12), fill="#dc2626")
    cv.add_text(H, "H", offset=(0, 18))
    cv.add_arc(O, 32, -37, 0)
    cv.add_text(O, "θ", offset=(42, -10))
    # 投影线段标注
    cv.add_line(O, H, stroke="#2563eb", width=3.0)
    cv.add_text(((O[0]+H[0])/2, 170), "|a|cosθ (投影)", offset=(0, 22), fill="#2563eb", size=13)
    cv.add_text((190, 225), "a · b = |a||b|cosθ = |b| · 投影", size=14, italic=False, bold=False)
    cv.save("vec_04_dot_product.svg")


# =============================================================
# 二、解三角形板块矢量图 (2 张)
# =============================================================
def gen_triangle_diagrams():
    # 1. 正弦定理与外接圆模型
    cv = SVGCanvas(width=380, height=320)
    O = (190, 160)
    R = 110
    cv.add_circle(O, r=R, fill="none", stroke="#94a3b8")
    cv.add_circle(O, r=3.0, fill="#000000")
    cv.add_text(O, "O", offset=(12, 14))

    # 三角形 ABC，A在顶部，B在左下，C在右下
    A = (190, 50)
    B = (95, 215)
    C = (285, 215)
    cv.add_polygon([A, B, C], fill="rgba(240, 240, 240, 0.4)", stroke="#000000", width=1.8)
    cv.add_text(A, "A", offset=(0, -12))
    cv.add_text(B, "B", offset=(-14, 14))
    cv.add_text(C, "C", offset=(14, 14))
    cv.add_text(((B[0]+C[0])/2, B[1]), "a", offset=(0, 18))
    cv.add_text(((A[0]+C[0])/2, (A[1]+C[1])/2), "b", offset=(14, -6))
    cv.add_text(((A[0]+B[0])/2, (A[1]+B[1])/2), "c", offset=(-14, -6))

    # 直径 CD' 辅助线
    D = (190, 270) # 底部
    # 直径 BD'
    # 连接半径
    cv.add_line(O, A, dashed=True, stroke="#2563eb", width=1.5)
    cv.add_text(((O[0]+A[0])/2, (O[1]+A[1])/2), "R", offset=(12, 0), fill="#2563eb")
    cv.add_text((190, 300), "正弦定理: a/sinA = b/sinB = c/sinC = 2R", size=14, italic=False, bold=False)
    cv.save("tri_01_sine_circumcircle.svg")

    # 2. 仰角、俯角与方位角实际测量模型
    cv = SVGCanvas(width=420, height=280)
    # 塔/山
    T_top = (320, 60)
    T_bot = (320, 210)
    cv.add_line(T_top, T_bot, stroke="#000000", width=2.4)
    cv.add_text(T_top, "目标点 P", offset=(10, -10))
    cv.add_text(T_bot, "基底 Q", offset=(10, 16))

    # 观测点 A
    A = (80, 210)
    cv.add_line(A, T_bot, stroke="#000000", width=1.8) # 地面水平线
    cv.add_line(A, T_top, stroke="#dc2626", width=2.0) # 仰角视线
    cv.add_arc(A, 45, -32, 0)
    cv.add_text(A, "仰角 α", offset=(70, -10), fill="#dc2626")
    cv.add_text(A, "观测点 A", offset=(-20, 18))

    # 俯角: 从目标点看水平线
    cv.add_line(T_top, (180, 60), dashed=True, stroke="#666666")
    cv.add_arc(T_top, 45, 148, 180)
    cv.add_text(T_top, "俯角 β", offset=(-65, 16), fill="#2563eb")

    # 直角
    cv.add_line((305, 210), (305, 195), stroke="#000000")
    cv.add_line((305, 195), (320, 195), stroke="#000000")
    cv.add_text((200, 260), "测高模型: PQ = d · tan α", size=14, italic=False, bold=False)
    cv.save("tri_02_survey_angles.svg")


# =============================================================
# 三、立体几何公理与判定/性质定理板块 (8 张)
# =============================================================
def gen_stereometry_theorems():
    eng = StereoEngine(origin=(160, 220), scale=75)

    # 1. 异面直线所成角模型 (平移法)
    cv = SVGCanvas(width=380, height=280)
    # 直线 a 和 b
    cv.add_line((60, 180), (280, 60), stroke="#000000", width=2.0)
    cv.add_text((290, 60), "a", offset=(10, 0))
    cv.add_line((80, 60), (300, 220), stroke="#000000", width=2.0)
    cv.add_text((310, 220), "b", offset=(10, 0))

    # 平移 a 到 O 使得与 b 相交
    O = (190, 140)
    cv.add_circle(O, r=3.5, fill="#dc2626")
    cv.add_text(O, "O", offset=(-12, -10), fill="#dc2626")
    # 平移后的 a'
    cv.add_line((80, 200), (300, 80), dashed=True, stroke="#dc2626", width=2.0)
    cv.add_text((310, 80), "a' // a", offset=(25, 0), fill="#dc2626")
    cv.add_arc(O, 28, -28, 36)
    cv.add_text(O, "θ", offset=(38, 4))
    cv.add_text((190, 255), "平移求异面直线夹角: θ ∈ (0, 90°]", size=14, italic=False, bold=False)
    cv.save("geo_01_skew_lines_angle.svg")

    # 2. 线面平行判定定理模型 (面外线平行面内线)
    cv = SVGCanvas(width=420, height=290)
    # 平面 alpha
    P1 = (80, 230)
    P2 = (280, 230)
    P3 = (360, 130)
    P4 = (160, 130)
    cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
    cv.add_text(P4, "α", offset=(18, 20))

    # 面内线 m
    M1 = (140, 200)
    M2 = (300, 160)
    cv.add_line(M1, M2, stroke="#000000", width=2.0)
    cv.add_text(M2, "m ⊂ α", offset=(35, 0))

    # 面外线 l
    L1 = (140, 90)
    L2 = (300, 50)
    cv.add_line(L1, L2, stroke="#dc2626", width=2.2)
    cv.add_text(L2, "l ⊄ α", offset=(30, 0), fill="#dc2626")

    # 平行标志
    cv.add_text((220, 75), "//", offset=(0, 0), fill="#2563eb", size=13)
    cv.add_text((220, 185), "//", offset=(0, 0), fill="#2563eb", size=13)
    cv.add_text((210, 265), "判定定理: l ⊄ α, m ⊂ α, l // m  ⇒  l // α", size=14, italic=False, bold=False)
    cv.save("geo_02_line_plane_parallel_judgement.svg")

    # 3. 线面平行性质定理模型 (过线的面与已知面相交，则线线平行)
    cv = SVGCanvas(width=440, height=310)
    # 平面 alpha (底面)
    P1 = (60, 250)
    P2 = (270, 250)
    P3 = (370, 160)
    P4 = (160, 160)
    cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
    cv.add_text(P4, "α", offset=(18, 20))

    # 平面 beta (相交面)
    B1 = (120, 220)
    B2 = (310, 180) # 交线 m = B1-B2
    B3 = (310, 60)
    B4 = (120, 100) # 上面直线 l = B4-B3
    cv.add_polygon([B1, B2, B3, B4], fill="rgba(219, 234, 254, 0.4)", stroke="#2563eb", width=1.4)
    cv.add_text(B4, "β", offset=(-14, 16), fill="#2563eb")

    cv.add_line(B4, B3, stroke="#dc2626", width=2.2)
    cv.add_text(B3, "l // α", offset=(30, 0), fill="#dc2626")

    cv.add_line(B1, B2, stroke="#000000", width=2.2)
    cv.add_text(B2, "m = α ∩ β", offset=(45, 4))
    cv.add_text((220, 285), "性质定理: l // α, l ⊂ β, α ∩ β = m  ⇒  l // m", size=14, italic=False, bold=False)
    cv.save("geo_03_line_plane_parallel_property.svg")

    # 4. 面面平行判定定理模型 (面内两相交线分别平行另一平面)
    cv = SVGCanvas(width=420, height=320)
    # 平面 beta (上方)
    P1 = (80, 140)
    P2 = (280, 140)
    P3 = (360, 50)
    P4 = (160, 50)
    cv.add_polygon([P1, P2, P3, P4], fill="rgba(219, 234, 254, 0.5)", stroke="#2563eb", width=1.5)
    cv.add_text(P4, "β", offset=(18, 20), fill="#2563eb")

    # 平面 alpha (下方)
    Q1 = (80, 270)
    Q2 = (280, 270)
    Q3 = (360, 180)
    Q4 = (160, 180)
    cv.add_polygon([Q1, Q2, Q3, Q4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
    cv.add_text(Q4, "α", offset=(18, 20))

    # 在 beta 中作两相交线 a, b
    cv.add_line((120, 100), (320, 90), stroke="#dc2626", width=2.0)
    cv.add_text((330, 90), "a", offset=(8, 0), fill="#dc2626")
    cv.add_line((180, 130), (270, 60), stroke="#dc2626", width=2.0)
    cv.add_text((280, 60), "b", offset=(8, 0), fill="#dc2626")
    cv.add_circle((233, 95), r=3.0, fill="#000000")
    cv.add_text((233, 95), "P", offset=(0, -10))
    cv.add_text((210, 300), "判定定理: a ⊂ β, b ⊂ β, a ∩ b = P, a//α, b//α ⇒ α // β", size=13, italic=False, bold=False)
    cv.save("geo_04_plane_plane_parallel_judgement.svg")

    # 5. 线面垂直判定定理模型 (垂直于面内两条相交线)
    cv = SVGCanvas(width=420, height=310)
    P1 = (80, 260)
    P2 = (280, 260)
    P3 = (360, 160)
    P4 = (160, 160)
    cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
    cv.add_text(P4, "α", offset=(18, 20))

    # 相交线 m, n
    O = (220, 210)
    cv.add_line((120, 210), (320, 210), stroke="#000000", width=1.8)
    cv.add_text((330, 210), "m", offset=(8, 4))
    cv.add_line((170, 245), (270, 175), stroke="#000000", width=1.8)
    cv.add_text((280, 175), "n", offset=(8, 4))
    cv.add_circle(O, r=3.5, fill="#000000")
    cv.add_text(O, "P", offset=(12, 14))

    # 垂线 l
    cv.add_line((220, 50), (220, 210), stroke="#dc2626", width=2.4)
    cv.add_line((220, 210), (220, 270), dashed=True, stroke="#dc2626", width=2.0)
    cv.add_text((220, 50), "l", offset=(14, 0), fill="#dc2626")

    # 双直角符号
    cv.add_line((208, 210), (208, 198), stroke="#dc2626")
    cv.add_line((208, 198), (220, 198), stroke="#dc2626")

    cv.add_line((210, 203), (210, 191), stroke="#dc2626")
    cv.add_line((210, 191), (220, 198), stroke="#dc2626")

    cv.add_text((210, 290), "判定定理: m ⊂ α, n ⊂ α, m ∩ n = P, l ⊥ m, l ⊥ n ⇒ l ⊥ α", size=13, italic=False, bold=False)
    cv.save("geo_05_line_plane_perp_judgement.svg")

    # 6. 线面垂直性质定理模型 (垂直于同一平面的两直线平行)
    cv = SVGCanvas(width=420, height=290)
    P1 = (80, 240)
    P2 = (280, 240)
    P3 = (360, 150)
    P4 = (160, 150)
    cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
    cv.add_text(P4, "α", offset=(18, 20))

    # 直线 a 垂直于 alpha
    A1 = (170, 60)
    A0 = (170, 195)
    cv.add_line(A1, A0, stroke="#000000", width=2.2)
    cv.add_line(A0, (170, 240), dashed=True, stroke="#000000", width=1.8)
    cv.add_text(A1, "a", offset=(-12, 0))
    cv.add_line((158, 195), (158, 183), stroke="#000000")
    cv.add_line((158, 183), (170, 183), stroke="#000000")

    # 直线 b 垂直于 alpha
    B1 = (270, 60)
    B0 = (270, 195)
    cv.add_line(B1, B0, stroke="#000000", width=2.2)
    cv.add_line(B0, (270, 240), dashed=True, stroke="#000000", width=1.8)
    cv.add_text(B1, "b", offset=(12, 0))
    cv.add_line((258, 195), (258, 183), stroke="#000000")
    cv.add_line((258, 183), (270, 183), stroke="#000000")

    cv.add_text((220, 100), "//", offset=(0, 0), fill="#2563eb", size=15)
    cv.add_text((210, 270), "性质定理: a ⊥ α, b ⊥ α  ⇒  a // b", size=14, italic=False, bold=False)
    cv.save("geo_06_line_plane_perp_property.svg")

    # 7. 二面角的平面角定义模型
    cv = SVGCanvas(width=420, height=310)
    # 半平面 alpha (左侧向上倾斜)
    # 棱 l = L1-L2
    L1 = (80, 220)
    L2 = (280, 140)
    # alpha 面
    cv.add_polygon([L1, L2, (240, 50), (40, 130)], fill="rgba(219, 234, 254, 0.4)", stroke="#2563eb", width=1.5)
    cv.add_text((40, 130), "α", offset=(14, 14), fill="#2563eb")
    # beta 面 (右侧水平伸展)
    cv.add_polygon([L1, L2, (370, 180), (170, 260)], fill="rgba(241, 245, 249, 0.6)", stroke="#334155", width=1.5)
    cv.add_text((170, 260), "β", offset=(14, -14))

    # 棱 l
    cv.add_line(L1, L2, stroke="#000000", width=2.4)
    cv.add_text(L2, "棱 l", offset=(25, 0))

    # 棱上点 O
    O = (180, 180)
    cv.add_circle(O, r=3.5, fill="#dc2626")
    cv.add_text(O, "O", offset=(4, 18), fill="#dc2626")

    # OA 垂直于 l 在 alpha 内
    A = (120, 110)
    cv.add_line(O, A, stroke="#dc2626", width=2.0)
    cv.add_text(A, "A", offset=(-12, 0), fill="#dc2626")

    # OB 垂直于 l 在 beta 内
    B = (270, 220)
    cv.add_line(O, B, stroke="#dc2626", width=2.0)
    cv.add_text(B, "B", offset=(14, 0), fill="#dc2626")

    cv.add_arc(O, 32, -135, 25)
    cv.add_text(O, "θ", offset=(20, -18), fill="#dc2626")
    cv.add_text((210, 290), "二面角平面角: OA ⊂ α, OB ⊂ β, OA ⊥ l, OB ⊥ l ⇒ ∠AOB", size=13, italic=False, bold=False)
    cv.save("geo_07_dihedral_angle.svg")

    # 8. 面面垂直判定定理模型 (一个平面过另一个平面的垂线)
    cv = SVGCanvas(width=420, height=310)
    # 底面 alpha
    P1 = (60, 250)
    P2 = (280, 250)
    P3 = (380, 160)
    P4 = (160, 160)
    cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
    cv.add_text(P4, "α", offset=(18, 20))

    # 竖直平面 beta
    B1 = (130, 230)
    B2 = (310, 180) # 交线
    B3 = (310, 60)
    B4 = (130, 110)
    cv.add_polygon([B1, B2, B3, B4], fill="rgba(219, 234, 254, 0.5)", stroke="#2563eb", width=1.5)
    cv.add_text(B4, "β", offset=(-14, 16), fill="#2563eb")

    # 垂线 l 属于 beta 且 l 垂直 alpha
    L_top = (210, 85)
    L_bot = (210, 208)
    cv.add_line(L_top, L_bot, stroke="#dc2626", width=2.2)
    cv.add_text(L_top, "l ⊂ β", offset=(22, 0), fill="#dc2626")
    cv.add_circle(L_bot, r=3.0, fill="#000000")

    # 直角
    cv.add_line((198, 208), (198, 196), stroke="#dc2626")
    cv.add_line((198, 196), (210, 196), stroke="#dc2626")
    cv.add_text((210, 285), "判定定理: l ⊂ β, l ⊥ α  ⇒  β ⊥ α", size=14, italic=False, bold=False)
    cv.save("geo_08_plane_plane_perp_judgement.svg")


# =============================================================
# 四、典型立体几何空间构型板块 (3 张)
# =============================================================
def gen_standard_solids():
    eng = StereoEngine(origin=(160, 250), scale=85)

    # 1. 正方体 ABCD-A1B1C1D1 (带截面与体对角线)
    cv = SVGCanvas(width=440, height=360)
    # 空间坐标
    # 底面 A(1, 0, 0), B(1, 1.5, 0), C(0, 1.5, 0), D(0, 0, 0)
    # 顶面 A1(1, 0, 1.5), B1(1, 1.5, 1.5), C1(0, 1.5, 1.5), D1(0, 0, 1.5)
    A = eng.p(1.5, 0.0, 0.0) # 前左
    B = eng.p(1.5, 1.8, 0.0) # 前右
    C = eng.p(0.0, 1.8, 0.0) # 后右
    D = eng.p(0.0, 0.0, 0.0) # 后左 (原点被遮挡)

    A1 = eng.p(1.5, 0.0, 1.8)
    B1 = eng.p(1.5, 1.8, 1.8)
    C1 = eng.p(0.0, 1.8, 1.8)
    D1 = eng.p(0.0, 0.0, 1.8)

    # 绘制对角面 ACC1A1
    cv.add_polygon([A, C, C1, A1], fill="rgba(254, 215, 170, 0.4)", stroke="none")

    # 棱 (实虚线判定: 涉及 D 的都是虚线)
    cv.add_line(D, A, dashed=True)
    cv.add_line(D, C, dashed=True)
    cv.add_line(D, D1, dashed=True)

    cv.add_line(A, B, dashed=False)
    cv.add_line(B, C, dashed=False)
    cv.add_line(A1, B1, dashed=False)
    cv.add_line(B1, C1, dashed=False)
    cv.add_line(C1, D1, dashed=False)
    cv.add_line(D1, A1, dashed=False)

    cv.add_line(A, A1, dashed=False)
    cv.add_line(B, B1, dashed=False)
    cv.add_line(C, C1, dashed=False)

    # 体对角线 A1C 与 底面对角线 AC
    cv.add_line(A, C, dashed=True, stroke="#dc2626", width=1.6)
    cv.add_line(A1, C, dashed=True, stroke="#2563eb", width=1.8)

    # 顶点标注
    for pt, txt, off in [
        (A, "A", (-14, 14)), (B, "B", (14, 14)), (C, "C", (16, -2)), (D, "D", (-16, -4)),
        (A1, "A1", (-16, -6)), (B1, "B1", (16, -4)), (C1, "C1", (14, -8)), (D1, "D1", (-16, -8))
    ]:
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, txt, offset=off)

    cv.add_text((220, 340), "正方体模型: 对角面 ACC1A1 与体对角线 A1C", size=14, italic=False, bold=False)
    cv.save("solid_01_cube_section.svg")

    # 2. 直三棱柱 ABC-A1B1C1
    cv = SVGCanvas(width=420, height=340)
    # 底面三角形 A(1.2, 0, 0), B(1.2, 1.8, 0), C(0, 0.8, 0) (C在后方)
    A = eng.p(1.4, 0.0, 0.0)
    B = eng.p(1.4, 2.0, 0.0)
    C = eng.p(0.0, 1.0, 0.0) # 后方被遮挡

    A1 = eng.p(1.4, 0.0, 2.0)
    B1 = eng.p(1.4, 2.0, 2.0)
    C1 = eng.p(0.0, 1.0, 2.0)

    # 虚线: 涉及 C 的棱全部虚线
    cv.add_line(A, C, dashed=True)
    cv.add_line(B, C, dashed=True)
    cv.add_line(C, C1, dashed=True)

    cv.add_line(A, B, dashed=False)
    cv.add_line(A1, B1, dashed=False)
    cv.add_line(B1, C1, dashed=False)
    cv.add_line(C1, A1, dashed=False)

    cv.add_line(A, A1, dashed=False)
    cv.add_line(B, B1, dashed=False)

    for pt, txt, off in [
        (A, "A", (-14, 14)), (B, "B", (14, 14)), (C, "C", (0, -10)),
        (A1, "A1", (-16, -6)), (B1, "B1", (16, -4)), (C1, "C1", (0, -12))
    ]:
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, txt, offset=off)

    cv.add_text((210, 320), "直三棱柱模型: 侧棱垂直于底面", size=14, italic=False, bold=False)
    cv.save("solid_02_tri_prism.svg")

    # 3. 正四棱锥 P-ABCD
    cv = SVGCanvas(width=420, height=340)
    A = eng.p(0.0, 0.0, 0.0) # 后左 (虚)
    D = eng.p(0.0, 2.0, 0.0) # 后右 (虚)
    B = eng.p(1.6, 0.0, 0.0) # 前左
    C = eng.p(1.6, 2.0, 0.0) # 前右
    P = eng.p(0.8, 1.0, 2.4) # 顶点
    O = eng.p(0.8, 1.0, 0.0) # 底面中心

    cv.add_line(A, D, dashed=True)
    cv.add_line(A, B, dashed=False)
    cv.add_line(B, C, dashed=False)
    cv.add_line(C, D, dashed=False)

    cv.add_line(P, A, dashed=True)
    cv.add_line(P, B, dashed=False)
    cv.add_line(P, C, dashed=False)
    cv.add_line(P, D, dashed=False)

    # 高线 PO 与 底面对角线 AC, BD
    cv.add_line(A, C, dashed=True, stroke="#666666", width=1.2)
    cv.add_line(B, D, dashed=True, stroke="#666666", width=1.2)
    cv.add_line(P, O, dashed=True, stroke="#dc2626", width=1.8)
    cv.add_circle(O, r=2.5, fill="#dc2626")

    for pt, txt, off in [
        (P, "P", (0, -12)), (A, "A", (-14, 2)), (B, "B", (-12, 14)),
        (C, "C", (14, 14)), (D, "D", (14, 0)), (O, "O", (12, 4))
    ]:
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, txt, offset=off)

    cv.add_text((210, 320), "正四棱锥模型: 高线 PO 垂直底面中心", size=14, italic=False, bold=False)
    cv.save("solid_03_sq_pyramid.svg")


# =============================================================
# 五、统计与概率板块高考试卷图 (2 张，Python + Matplotlib 生成)
# =============================================================
def gen_stat_prob_diagrams():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams["font.sans-serif"] = ["Songti SC", "SimSun", "Arial"]
    plt.rcParams["axes.unicode_minus"] = False

    # 1. 频率分布直方图与数字特征 (中位数分割线 + 众数顶峰)
    fig, ax = plt.subplots(figsize=(6.5, 4.2), dpi=300)
    bins = [50, 60, 70, 80, 90, 100]
    heights = [0.005, 0.015, 0.035, 0.030, 0.015]
    widths = [10] * 5
    centers = [55, 65, 75, 85, 95]

    bars = ax.bar(centers, heights, width=widths, edgecolor="black", facecolor="#f8fafc", linewidth=1.5)
    for bar, h in zip(bars, heights):
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.001, f"{h:.3f}", ha="center", va="bottom", fontsize=10, family="Times New Roman")

    # 标注众数
    ax.annotate("众数 (最高峰中点 = 75)", xy=(75, 0.035), xytext=(65, 0.041),
                arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5), fontsize=10, color="#dc2626")

    # 标注中位数竖线 (面积=0.5处，在70~80区间内: 前两项面积0.05+0.15=0.20，还差0.30，0.30/0.035=8.57，中位数约78.57)
    med_x = 78.57
    ax.axvline(med_x, color="#2563eb", linestyle="--", linewidth=1.8)
    ax.text(med_x + 1, 0.025, f"中位数 ≈ {med_x:.1f}\n(左右面积各占50%)", color="#2563eb", fontsize=9)

    ax.set_xlim(45, 105)
    ax.set_ylim(0, 0.046)
    ax.set_xticks(bins)
    ax.set_xlabel("数据区间 [a, b)", fontsize=11, labelpad=6)
    ax.set_ylabel("频率 / 组距", fontsize=11, labelpad=6)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "stat_01_histogram.png", dpi=300)
    plt.close()

    # 2. 古典概型样本空间树状图 (抛硬币/摸球两步试验)
    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=300)
    ax.axis("off")

    # 根节点
    ax.text(0.1, 0.5, "试验开始", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.3", fc="#e2e8f0", ec="#64748b"), fontsize=11)
    # 第一步分支: A, B
    ax.annotate("", xy=(0.35, 0.75), xytext=(0.17, 0.53), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.annotate("", xy=(0.35, 0.25), xytext=(0.17, 0.47), arrowprops=dict(arrowstyle="->", lw=1.5))
    ax.text(0.38, 0.75, "第一步: 事件 A", va="center", fontsize=10, weight="bold")
    ax.text(0.38, 0.25, "第一步: 事件 B", va="center", fontsize=10, weight="bold")

    # 第二步分支
    for y_step, label in [(0.87, "A1 (结果1)"), (0.63, "A2 (结果2)"), (0.37, "B1 (结果3)"), (0.13, "B2 (结果4)")]:
        source_y = 0.75 if y_step > 0.5 else 0.25
        ax.annotate("", xy=(0.68, y_step), xytext=(0.54, source_y), arrowprops=dict(arrowstyle="->", lw=1.2, color="#2563eb"))
        ax.text(0.70, y_step, f"第二步: {label}", va="center", fontsize=9, color="#1e293b")
        # 结果与概率
        ax.text(0.92, y_step, "P = 1/4", va="center", fontsize=9, color="#dc2626", family="Times New Roman")

    ax.text(0.5, 0.02, "古典概型全树状图列举法: P(E) = m / n", ha="center", fontsize=11, weight="bold")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "prob_01_tree_diagram.png", dpi=300)
    plt.close()


# =============================================================
# 六、调用 macOS 原生 AppKit 批量高清渲染所有 SVG -> PNG
# =============================================================
def batch_render_svgs():
    swift_script = f'''
import AppKit

let outDir = URL(fileURLWithPath: "{OUTPUT_DIR}")
let fileManager = FileManager.default
let files = (try? fileManager.contentsOfDirectory(atPath: outDir.path)) ?? []

for file in files where file.hasSuffix(".svg") {{
    let svgUrl = outDir.appendingPathComponent(file)
    let pngUrl = svgUrl.deletingPathExtension().appendingPathExtension("png")
    
    guard let svgData = try? Data(contentsOf: svgUrl),
          let image = NSImage(data: svgData) else {{
        continue
    }}
    
    let scale: CGFloat = 3.0 // 300+ DPI 超采样印刷级
    let w = Int(image.size.width * scale)
    let h = Int(image.size.height * scale)
    
    let rep = NSBitmapImageRep(
        bitmapDataPlanes: nil,
        pixelsWide: w,
        pixelsHigh: h,
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
    
    NSColor.white.setFill()
    NSRect(x: 0, y: 0, width: w, height: h).fill()
    image.draw(in: NSRect(x: 0, y: 0, width: w, height: h))
    NSGraphicsContext.restoreGraphicsState()
    
    if let pngData = rep.representation(using: .png, properties: [:]) {{
        try? pngData.write(to: pngUrl)
        print("RENDERED: \\(file) -> \\(pngUrl.lastPathComponent)")
    }}
}}
'''
    res = subprocess.run(["swift", "-e", swift_script], capture_output=True, text=True)
    print(res.stdout)


def sync_to_desktop():
    """将所有生成的 PNG 镜像同步至桌面 math_images/"""
    cmd = f"cp {OUTPUT_DIR}/*.png {DESKTOP_DIR}/"
    subprocess.run(cmd, shell=True, check=True)
    print(f"✅ 已全部同步至桌面目录: {DESKTOP_DIR}")


if __name__ == "__main__":
    print("🚀 开始全量生成高考数学题图库...")
    gen_vector_diagrams()
    gen_triangle_diagrams()
    gen_stereometry_theorems()
    gen_standard_solids()
    gen_stat_prob_diagrams()
    print("🎨 开始原生高清渲染 SVG -> PNG...")
    batch_render_svgs()
    sync_to_desktop()
    print("🏆 全套 19 张高考标准题图库生成并同步完毕！")
