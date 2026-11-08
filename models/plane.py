# -*- coding: utf-8 -*-
"""
math_graphics.models.plane
平面向量、解三角形与立体几何核心公理/判定/性质定理图库生成器
"""

from typing import Tuple, Optional
from ..core.canvas import SVGCanvas
from ..core.projection import StereoEngine


# =============================================================
# 一、平面向量板块
# =============================================================
def build_vector_addition(canvas_size: Tuple[int, int] = (480, 260)) -> SVGCanvas:
    """向量加法: 平行四边形法则与三角形法则"""
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])
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

    # 右图: 三角形法则 (首尾相接)
    P = (290, 180)
    Q = (410, 180)
    R = (370, 90)
    cv.add_line(P, Q, arrow=True, width=2.0)
    cv.add_line(Q, R, arrow=True, width=2.0)
    cv.add_line(P, R, arrow=True, stroke="#dc2626", width=2.2, arrow_color="arrow-red")
    cv.add_text(P, "P", offset=(-12, 16))
    cv.add_text(Q, "Q", offset=(12, 16))
    cv.add_text(R, "R", offset=(10, -8))
    cv.add_text(((P[0]+Q[0])/2, P[1]), "a", offset=(0, 18))
    cv.add_text(((Q[0]+R[0])/2, (Q[1]+R[1])/2), "b", offset=(16, 0))
    cv.add_text(((P[0]+R[0])/2, (P[1]+R[1])/2), "a + b", offset=(-18, -10), fill="#dc2626")

    cv.add_text((canvas_size[0]//2, canvas_size[1]-15), "向量加法: 平行四边形法则 (共起点) 与 三角形法则 (首尾接)", size=14, italic=False, bold=False)
    return cv


def build_vector_subtraction(canvas_size: Tuple[int, int] = (420, 260)) -> SVGCanvas:
    """向量减法: 指向被减向量"""
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])
    O = (100, 190)
    A = (280, 190)
    B = (190, 80)
    cv.add_line(O, A, arrow=True, width=2.0)
    cv.add_line(O, B, arrow=True, width=2.0)
    cv.add_line(B, A, arrow=True, stroke="#dc2626", width=2.2, arrow_color="arrow-red")
    cv.add_text(O, "O", offset=(-14, 14))
    cv.add_text(A, "A", offset=(14, 14))
    cv.add_text(B, "B", offset=(0, -12))
    cv.add_text(((O[0]+A[0])/2, O[1]), "a", offset=(0, 18))
    cv.add_text(((O[0]+B[0])/2, (O[1]+B[1])/2), "b", offset=(-18, -6))
    cv.add_text(((B[0]+A[0])/2, (B[1]+A[1])/2), "a - b = BA", offset=(25, -6), fill="#dc2626")
    cv.add_text((canvas_size[0]//2, canvas_size[1]-15), "向量减法法则: 共起点，指向被减向量 (BA = OA - OB)", size=14, italic=False, bold=False)
    return cv


def build_vector_coordinates(canvas_size: Tuple[int, int] = (380, 300)) -> SVGCanvas:
    """平面直角坐标系中的正交分解"""
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])
    O = (70, 230)
    cv.add_line((40, 230), (340, 230), arrow=True, width=1.8)
    cv.add_text((345, 235), "x", offset=(0, 0))
    cv.add_line((70, 260), (70, 40), arrow=True, width=1.8)
    cv.add_text((70, 30), "y", offset=(0, 0))
    cv.add_text(O, "O", offset=(-12, 16))

    A = (270, 90)
    Ax = (270, 230)
    Ay = (70, 90)
    cv.add_line(O, A, arrow=True, stroke="#dc2626", width=2.4, arrow_color="arrow-red")
    cv.add_line(A, Ax, dashed=True, stroke="#64748b")
    cv.add_line(A, Ay, dashed=True, stroke="#64748b")
    cv.add_text(Ax, "x", offset=(0, 18), fill="#64748b")
    cv.add_text(Ay, "y", offset=(-16, 4), fill="#64748b")
    cv.add_text(A, "A(x, y)", offset=(15, -10))
    cv.add_text(((O[0]+A[0])/2, (O[1]+A[1])/2), "a = xi + yj", offset=(-20, -14), fill="#dc2626")
    cv.add_text((canvas_size[0]//2, canvas_size[1]-15), "平面向量坐标表示: 模长 |a| = √(x² + y²)", size=14, italic=False, bold=False)
    return cv


def build_vector_dot_product(canvas_size: Tuple[int, int] = (380, 280)) -> SVGCanvas:
    """向量数量积的几何意义 (投影)"""
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])
    O = (70, 200)
    A = (290, 200)
    B = (220, 90)
    B_proj = (220, 200)

    cv.add_line(O, A, arrow=True, width=2.0)
    cv.add_line(O, B, arrow=True, stroke="#2563eb", width=2.0, arrow_color="arrow-blue")
    cv.add_line(B, B_proj, dashed=True, stroke="#64748b", width=1.4)
    cv.add_line((220, 188), (208, 188), stroke="#64748b")
    cv.add_line((208, 188), (208, 200), stroke="#64748b")

    cv.add_arc(O, 38, -36, 0)
    cv.add_text(O, "θ", offset=(48, -8))
    cv.add_line((O[0], 215), (B_proj[0], 215), stroke="#dc2626", width=2.2)
    cv.add_text(((O[0]+B_proj[0])/2, 235), "|b|·cosθ (投影)", fill="#dc2626", size=13)
    cv.add_text(O, "O", offset=(-12, 16))
    cv.add_text(A, "a", offset=(14, 0))
    cv.add_text(B, "b", offset=(0, -12), fill="#2563eb")
    cv.add_text((canvas_size[0]//2, canvas_size[1]-15), "数量积几何意义: a · b = |a| · (|b| cosθ)", size=14, italic=False, bold=False)
    return cv


# =============================================================
# 二、解三角形板块
# =============================================================
def build_triangle_sine_circumcircle(canvas_size: Tuple[int, int] = (380, 320)) -> SVGCanvas:
    """正弦定理与外接圆"""
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])
    O = (190, 160)
    R = 110
    cv.add_circle(O, r=R, fill="none", stroke="#94a3b8")
    cv.add_circle(O, r=3.0, fill="#000000")
    cv.add_text(O, "O", offset=(12, 14))

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

    cv.add_line(O, A, dashed=True, stroke="#2563eb", width=1.5)
    cv.add_text(((O[0]+A[0])/2, (O[1]+A[1])/2), "R", offset=(12, 0), fill="#2563eb")
    cv.add_text((canvas_size[0]//2, canvas_size[1]-20), "正弦定理: a/sinA = b/sinB = c/sinC = 2R", size=14, italic=False, bold=False)
    return cv


def build_survey_angles(canvas_size: Tuple[int, int] = (420, 280)) -> SVGCanvas:
    """仰角、俯角与方位角测量模型"""
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])
    T_top = (320, 60)
    T_bot = (320, 210)
    cv.add_line(T_top, T_bot, stroke="#000000", width=2.4)
    cv.add_text(T_top, "目标点 P", offset=(10, -10))
    cv.add_text(T_bot, "基底 Q", offset=(10, 16))

    A = (80, 210)
    cv.add_line(A, T_bot, stroke="#000000", width=1.8)
    cv.add_line(A, T_top, stroke="#dc2626", width=2.0)
    cv.add_arc(A, 45, -32, 0)
    cv.add_text(A, "仰角 α", offset=(70, -10), fill="#dc2626")
    cv.add_text(A, "观测点 A", offset=(-20, 18))

    cv.add_line(T_top, (180, 60), dashed=True, stroke="#666666")
    cv.add_arc(T_top, 45, 148, 180)
    cv.add_text(T_top, "俯角 β", offset=(-65, 16), fill="#2563eb")

    cv.add_line((305, 210), (305, 195), stroke="#000000")
    cv.add_line((305, 195), (320, 195), stroke="#000000")
    cv.add_text((canvas_size[0]//2, canvas_size[1]-20), "测高模型: PQ = d · tan α", size=14, italic=False, bold=False)
    return cv


# =============================================================
# 三、立体几何公理与判定/性质定理板块 (8 张)
# =============================================================
def build_theorem_diagram(theorem_id: str) -> SVGCanvas:
    """
    根据标准编号生成立体几何定理图：
    - geo_01: 异面直线夹角
    - geo_02: 线面平行判定定理
    - geo_03: 线面平行性质定理
    - geo_04: 面面平行判定定理
    - geo_05: 线面垂直判定定理
    - geo_06: 线面垂直性质定理
    - geo_07: 二面角平面角
    - geo_08: 面面垂直判定定理
    """
    tid = theorem_id.lower().strip()
    if "01" in tid or "skew" in tid:
        cv = SVGCanvas(width=380, height=280)
        cv.add_line((60, 180), (280, 60), stroke="#000000", width=2.0)
        cv.add_text((290, 60), "a", offset=(10, 0))
        cv.add_line((80, 60), (300, 220), stroke="#000000", width=2.0)
        cv.add_text((310, 220), "b", offset=(10, 0))
        O = (190, 140)
        cv.add_circle(O, r=3.5, fill="#dc2626")
        cv.add_text(O, "O", offset=(-12, -10), fill="#dc2626")
        cv.add_line((80, 200), (300, 80), dashed=True, stroke="#dc2626", width=2.0)
        cv.add_text((310, 80), "a' // a", offset=(25, 0), fill="#dc2626")
        cv.add_arc(O, 28, -28, 36)
        cv.add_text(O, "θ", offset=(38, 4))
        cv.add_text((190, 255), "平移求异面直线夹角: θ ∈ (0, 90°]", size=14, italic=False, bold=False)
        return cv

    elif "02" in tid or "line_plane_parallel_judgement" in tid:
        cv = SVGCanvas(width=420, height=290)
        P1, P2, P3, P4 = (80, 230), (280, 230), (360, 130), (160, 130)
        cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(P4, "α", offset=(18, 20))
        cv.add_line((140, 200), (300, 160), stroke="#000000", width=2.0)
        cv.add_text((300, 160), "m ⊂ α", offset=(35, 0))
        cv.add_line((140, 90), (300, 50), stroke="#dc2626", width=2.2)
        cv.add_text((300, 50), "l ⊄ α", offset=(30, 0), fill="#dc2626")
        cv.add_text((220, 75), "//", offset=(0, 0), fill="#2563eb", size=13)
        cv.add_text((220, 185), "//", offset=(0, 0), fill="#2563eb", size=13)
        cv.add_text((210, 265), "判定定理: l ⊄ α, m ⊂ α, l // m  ⇒  l // α", size=14, italic=False, bold=False)
        return cv

    elif "03" in tid or "line_plane_parallel_property" in tid:
        cv = SVGCanvas(width=440, height=310)
        P1, P2, P3, P4 = (60, 250), (270, 250), (370, 160), (160, 160)
        cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(P4, "α", offset=(18, 20))
        B1, B2, B3, B4 = (120, 220), (310, 180), (310, 60), (120, 100)
        cv.add_polygon([B1, B2, B3, B4], fill="rgba(254, 243, 199, 0.6)", stroke="#b45309", width=1.5)
        cv.add_text(B4, "β", offset=(15, 20))
        cv.add_line(B1, B2, stroke="#2563eb", width=2.2)
        cv.add_text(B2, "m = α ∩ β", offset=(45, 0), fill="#2563eb")
        cv.add_line(B4, B3, stroke="#dc2626", width=2.2)
        cv.add_text(B3, "l ⊂ β", offset=(30, 0), fill="#dc2626")
        cv.add_text((220, 285), "性质定理: l // α, l ⊂ β, α ∩ β = m  ⇒  l // m", size=14, italic=False, bold=False)
        return cv

    elif "04" in tid or "plane_plane_parallel_judgement" in tid:
        cv = SVGCanvas(width=440, height=340)
        A1, A2, A3, A4 = (60, 150), (270, 150), (370, 60), (160, 60)
        cv.add_polygon([A1, A2, A3, A4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(A4, "β", offset=(18, 20))
        B1, B2, B3, B4 = (60, 280), (270, 280), (370, 190), (160, 190)
        cv.add_polygon([B1, B2, B3, B4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(B4, "α", offset=(18, 20))
        cv.add_line((120, 250), (300, 220), stroke="#000000", width=2.0)
        cv.add_text((300, 220), "a ⊂ α", offset=(30, 0))
        cv.add_line((160, 210), (260, 270), stroke="#000000", width=2.0)
        cv.add_text((260, 270), "b ⊂ α", offset=(30, 0))
        cv.add_circle((210, 240), r=3.0, fill="#dc2626")
        cv.add_text((210, 240), "P (交点)", offset=(0, -12), fill="#dc2626")
        cv.add_line((120, 120), (300, 90), stroke="#2563eb", width=2.0)
        cv.add_text((300, 90), "a' // a", offset=(30, 0), fill="#2563eb")
        cv.add_line((160, 80), (260, 140), stroke="#2563eb", width=2.0)
        cv.add_text((260, 140), "b' // b", offset=(30, 0), fill="#2563eb")
        cv.add_text((220, 320), "判定定理: a ⊂ α, b ⊂ α, a ∩ b = P, a // β, b // β ⇒ α // β", size=13, italic=False, bold=False)
        return cv

    elif "05" in tid or "line_plane_perp_judgement" in tid:
        cv = SVGCanvas(width=420, height=310)
        P1, P2, P3, P4 = (60, 250), (280, 250), (360, 150), (140, 150)
        cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(P4, "α", offset=(18, 20))
        O = (210, 200)
        cv.add_line((120, 215), (300, 185), stroke="#000000", width=1.8)
        cv.add_text((300, 185), "m ⊂ α", offset=(35, 0))
        cv.add_line((160, 165), (260, 235), stroke="#000000", width=1.8)
        cv.add_text((260, 235), "n ⊂ α", offset=(35, 0))
        cv.add_circle(O, r=3.0, fill="#000000")
        cv.add_text(O, "P", offset=(-12, 14))
        cv.add_line((210, 60), (210, 200), stroke="#dc2626", width=2.4)
        cv.add_text((210, 60), "l ⊥ α", offset=(0, -12), fill="#dc2626")
        cv.add_line((210, 185), (225, 182), stroke="#dc2626")
        cv.add_line((225, 182), (225, 197), stroke="#dc2626")
        cv.add_text((210, 285), "判定定理: m ⊂ α, n ⊂ α, m ∩ n = P, l ⊥ m, l ⊥ n ⇒ l ⊥ α", size=13, italic=False, bold=False)
        return cv

    elif "06" in tid or "line_plane_perp_property" in tid:
        cv = SVGCanvas(width=420, height=310)
        P1, P2, P3, P4 = (60, 250), (280, 250), (360, 150), (140, 150)
        cv.add_polygon([P1, P2, P3, P4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(P4, "α", offset=(18, 20))
        cv.add_line((150, 70), (150, 200), stroke="#dc2626", width=2.2)
        cv.add_text((150, 70), "a ⊥ α", offset=(0, -12), fill="#dc2626")
        cv.add_line((150, 188), (162, 188), stroke="#dc2626")
        cv.add_line((162, 188), (162, 200), stroke="#dc2626")
        cv.add_line((270, 70), (270, 200), stroke="#2563eb", width=2.2)
        cv.add_text((270, 70), "b ⊥ α", offset=(0, -12), fill="#2563eb")
        cv.add_line((270, 188), (282, 188), stroke="#2563eb")
        cv.add_line((282, 188), (282, 200), stroke="#2563eb")
        cv.add_text((210, 130), "//", offset=(0, 0), fill="#059669", size=15)
        cv.add_text((210, 285), "性质定理: a ⊥ α, b ⊥ α  ⇒  a // b (垂直同面的两线平行)", size=14, italic=False, bold=False)
        return cv

    elif "07" in tid or "dihedral" in tid:
        cv = SVGCanvas(width=440, height=320)
        eng = StereoEngine(origin=(160, 220), scale=75)
        L1 = (80, 230)
        L2 = (280, 170)
        cv.add_line(L1, L2, stroke="#000000", width=2.4)
        cv.add_text(L2, "棱 l", offset=(25, 0))
        cv.add_polygon([L1, L2, (340, 220), (140, 280)], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text((140, 280), "α", offset=(15, -10))
        cv.add_polygon([L1, L2, (280, 60), (80, 120)], fill="rgba(254, 243, 199, 0.6)", stroke="#b45309", width=1.5)
        cv.add_text((80, 120), "β", offset=(15, 20))
        O = (180, 200)
        cv.add_circle(O, r=3.0, fill="#dc2626")
        cv.add_text(O, "O", offset=(-12, 14), fill="#dc2626")
        cv.add_line(O, (180, 90), stroke="#dc2626", width=2.0)
        cv.add_text((180, 90), "OA ⊥ l", offset=(0, -10), fill="#dc2626")
        cv.add_line(O, (230, 240), stroke="#dc2626", width=2.0)
        cv.add_text((230, 240), "OB ⊥ l", offset=(15, 10), fill="#dc2626")
        cv.add_arc(O, 32, -90, 40)
        cv.add_text(O, "θ", offset=(24, -14), fill="#dc2626")
        cv.add_text((220, 305), "二面角平面角: OA ⊂ β, OB ⊂ α, OA ⊥ l, OB ⊥ l ⇒ ∠AOB 为二面角 α-l-β 的平面角", size=12, italic=False, bold=False)
        return cv

    elif "08" in tid or "plane_plane_perp_judgement" in tid:
        cv = SVGCanvas(width=440, height=320)
        A1, A2, A3, A4 = (60, 260), (300, 260), (380, 160), (140, 160)
        cv.add_polygon([A1, A2, A3, A4], fill="rgba(241, 245, 249, 0.7)", stroke="#334155", width=1.5)
        cv.add_text(A4, "α", offset=(18, 20))
        B1, B2, B3, B4 = (140, 240), (280, 200), (280, 60), (140, 100)
        cv.add_polygon([B1, B2, B3, B4], fill="rgba(254, 243, 199, 0.6)", stroke="#b45309", width=1.5)
        cv.add_text(B4, "β", offset=(15, 20))
        cv.add_line((210, 80), (210, 220), stroke="#dc2626", width=2.4)
        cv.add_text((210, 80), "l ⊂ β 且 l ⊥ α", offset=(0, -12), fill="#dc2626")
        cv.add_line((210, 205), (225, 202), stroke="#dc2626")
        cv.add_line((225, 202), (225, 217), stroke="#dc2626")
        cv.add_text((220, 295), "面面垂直判定定理: l ⊂ β, l ⊥ α  ⇒  β ⊥ α", size=14, italic=False, bold=False)
        return cv

    else:
        raise ValueError(f"未知的定理编号: {theorem_id} (有效范围: geo_01 ~ geo_08)")
