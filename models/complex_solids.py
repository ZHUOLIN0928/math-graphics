# -*- coding: utf-8 -*-
"""
math_graphics.models.complex_solids
高考压轴立体几何“异形体”与非标模型生成器 (真卷黑白出版风格)
顶点标注严格遵循数学制图规范，放置在多边形外侧绝对空白区，零压线零重叠。
"""

from typing import Tuple, Optional
from ..core.canvas import SVGCanvas
from ..core.projection import StereoEngine


def build_folded_tetrahedron(
    canvas_size: Tuple[int, int] = (460, 360),
    origin: Tuple[float, float] = (160, 260),
    scale: float = 85.0,
    title: str = "翻折模型: 矩形 ABCD 沿对角线 AC 折起使面 ABC ⊥ 面 ACD",
) -> SVGCanvas:
    """
    高考经典翻折题：
    矩形 ABCD 沿 AC 折起形成四面体 B-ACD，满足面 ABC ⊥ 面 ACD。
    作 BH ⊥ AC 于 H，则 BH ⊥ 面 ACD。
    """
    eng = StereoEngine(origin=origin, scale=scale)
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])

    coords = {
        "A": (0.0, 0.0, 0.0),       # 后左
        "C": (0.0, 2.4, 0.0),       # 后右
        "D": (1.4, 1.2, 0.0),       # 前方
        "H": (0.0, 0.8, 0.0),       # 垂足
        "B": (0.0, 0.8, 1.8),       # 空间顶点
    }
    p = {k: eng.p(*v) for k, v in coords.items()}

    # 1. 底面淡灰填充
    cv.add_polygon([p["A"], p["D"], p["C"]], fill="rgba(0, 0, 0, 0.04)", stroke="none")

    # 2. 内部遮挡虚线
    cv.add_line(p["A"], p["C"], dashed=True, stroke="#000000", width=1.5)
    cv.add_line(p["B"], p["H"], dashed=True, stroke="#000000", width=1.8)
    cv.add_line(p["D"], p["H"], dashed=True, stroke="#64748b", width=1.2)

    # 外部实线
    for v1, v2 in [("A", "D"), ("C", "D"), ("B", "A"), ("B", "C"), ("B", "D")]:
        cv.add_line(p[v1], p[v2], dashed=False, stroke="#000000", width=1.8)

    # 3. 空间直角符号
    ra_pts = eng.get_right_angle_3d_points(coords["H"], coords["B"], coords["C"], size=0.22)
    if ra_pts:
        cv.elements.append(
            f'<polyline points="{ra_pts[0][0]},{ra_pts[0][1]} {ra_pts[1][0]},{ra_pts[1][1]} {ra_pts[2][0]},{ra_pts[2][1]}" '
            f'fill="none" stroke="#000000" stroke-width="1.2" stroke-linecap="square" />'
        )

    # 4. 顶点实体黑点与纯净外围标注 (严格在几何体外部空白区，绝不压线)
    labels_layout = {
        "B": ((0, -12), "middle"),       # 顶部正上方空白
        "A": ((-16, 4), "end"),          # 底部最左侧空白
        "C": ((16, 4), "start"),         # 底部最右侧空白
        "D": ((0, 18), "middle"),        # 前方正下方空白
        "H": ((-12, -8), "end"),         # 垂足左上方空白
    }

    for k, pt in p.items():
        cv.add_circle(pt, r=2.8, fill="#000000")
        offset, anchor = labels_layout[k]
        cv.add_text(pt, k, offset=offset, size=15, italic=True, bold=True, anchor=anchor, fill="#000000")

    if title:
        cv.add_text((canvas_size[0] // 2, canvas_size[1] - 16), title, size=12, italic=False, bold=False)

    return cv


def build_corner_cut_cube(
    canvas_size: Tuple[int, int] = (460, 360),
    origin: Tuple[float, float] = (160, 250),
    scale: float = 85.0,
    title: str = "截割异形体: 正方体截去一角 (三棱锥 A1-EFG)",
) -> SVGCanvas:
    """
    正方体在左上方顶点 A1 处截去角 A1-EFG，
    留下三角形截面 EFG，侧面与顶面重构为五边形。
    """
    eng = StereoEngine(origin=origin, scale=scale)
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])

    a, b, c = 1.5, 1.8, 1.8

    v = {
        "A": (a, 0.0, 0.0),
        "B": (a, b, 0.0),
        "C": (0.0, b, 0.0),
        "D": (0.0, 0.0, 0.0),
        "B1": (a, b, c),
        "C1": (0.0, b, c),
        "D1": (0.0, 0.0, c),
        "E": (a, 0.6, c),       # A1B1 上
        "F": (0.6, 0.0, c),     # A1D1 上
        "G": (a, 0.0, 1.1),     # AA1 上
    }
    p = {k: eng.p(*coord) for k, coord in v.items()}

    # 1. 截面 EFG 阴影填充 (学术淡灰)
    cv.add_polygon([p["E"], p["F"], p["G"]], fill="rgba(0, 0, 0, 0.08)", stroke="#000000", width=1.8)

    # 2. 内部遮挡虚线 (涉及 D 的棱)
    for v1, v2 in [("D", "A"), ("D", "C"), ("D", "D1")]:
        cv.add_line(p[v1], p[v2], dashed=True, stroke="#000000", width=1.4)

    # 3. 实体棱线
    solid_edges = [
        ("A", "B"), ("B", "C"),
        ("A", "G"),
        ("G", "E"), ("E", "F"), ("F", "G"),
        ("E", "B1"), ("F", "D1"),
        ("B1", "C1"), ("C1", "D1"),
        ("B", "B1"), ("C", "C1"),
    ]
    for v1, v2 in solid_edges:
        cv.add_line(p[v1], p[v2], dashed=False, stroke="#000000", width=1.8)

    # 4. 原被截除顶点 A1 的空间延伸虚线
    p_A1 = eng.p(a, 0.0, c)
    cv.add_line(p["G"], p_A1, dashed=True, stroke="#94a3b8", width=1.2)
    cv.add_line(p["E"], p_A1, dashed=True, stroke="#94a3b8", width=1.2)
    cv.add_line(p["F"], p_A1, dashed=True, stroke="#94a3b8", width=1.2)
    cv.add_text(p_A1, "A₁", offset=(-14, -6), size=12, fill="#64748b", italic=True, anchor="end")

    # 5. 各顶点精准外推布局 (零压线)
    labels_layout = {
        "A": ((-14, 14), "end"),
        "B": ((14, 14), "start"),
        "C": ((14, -2), "start"),
        "D": ((-14, -2), "end"),
        "B1": ((14, -4), "start"),
        "C1": ((14, -6), "start"),
        "D1": ((-14, -6), "end"),
        "E": ((0, -12), "middle"),
        "F": ((-12, -8), "end"),
        "G": ((-14, 4), "end"),
    }

    for k, pt in p.items():
        cv.add_circle(pt, r=2.8, fill="#000000")
        offset, anchor = labels_layout[k]
        cv.add_text(pt, k, offset=offset, size=15, italic=True, bold=True, anchor=anchor, fill="#000000")

    if title:
        cv.add_text((canvas_size[0] // 2, canvas_size[1] - 16), title, size=12, italic=False, bold=False)

    return cv
