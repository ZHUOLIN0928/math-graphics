# -*- coding: utf-8 -*-
"""
math_graphics.models.solids
高考常见多面体与立体几何模型构造器
包含：正方体/长方体（支持任意截面与体对角线）、直三棱柱、正四棱锥、以及通用自定义多面体构造器。
"""

from typing import List, Dict, Tuple, Optional
from ..core.canvas import SVGCanvas
from ..core.projection import StereoEngine


def build_cube(
    a: float = 1.5,
    b: float = 1.8,
    c: float = 1.8,
    section: Optional[List[str]] = None,
    section_color: str = "rgba(254, 215, 170, 0.4)",
    diagonals: Optional[List[Tuple[str, str, str]]] = None,
    title: str = "正方体/长方体模型",
    canvas_size: Tuple[int, int] = (440, 360),
    origin: Tuple[float, float] = (160, 250),
    scale: float = 85.0,
) -> SVGCanvas:
    """
    构造长方体/正方体 ABCD-A1B1C1D1
    :param a, b, c: 尺寸 (x长, y宽, z高)
    :param section: 截面顶点列表，如 ['A', 'C', 'C1', 'A1'] 或 ['A1', 'B', 'D']
    :param section_color: 截面填充颜色
    :param diagonals: 额外线段列表 [(v1, v2, color)]
    :param title: 底部标题文字
    """
    eng = StereoEngine(origin=origin, scale=scale)
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])

    # 3D 坐标空间
    coords_3d = {
        "A": (a, 0.0, 0.0),      # 前左
        "B": (a, b, 0.0),        # 前右
        "C": (0.0, b, 0.0),      # 后右
        "D": (0.0, 0.0, 0.0),    # 后左 (原点，被遮挡)
        "A1": (a, 0.0, c),
        "B1": (a, b, c),
        "C1": (0.0, b, c),
        "D1": (0.0, 0.0, c),
    }
    pts_2d = {k: eng.p(*v) for k, v in coords_3d.items()}

    # 1. 绘制截面 (若指定)
    if section and len(section) >= 3:
        sec_pts = [pts_2d[name] for name in section if name in pts_2d]
        if len(sec_pts) >= 3:
            cv.add_polygon(sec_pts, fill=section_color, stroke="none")

    # 2. 棱边绘制（涉及 D 的棱为虚线）
    dashed_edges = [("D", "A"), ("D", "C"), ("D", "D1")]
    solid_edges = [
        ("A", "B"), ("B", "C"),
        ("A1", "B1"), ("B1", "C1"), ("C1", "D1"), ("D1", "A1"),
        ("A", "A1"), ("B", "B1"), ("C", "C1"),
    ]

    for v1, v2 in dashed_edges:
        cv.add_line(pts_2d[v1], pts_2d[v2], dashed=True, stroke="#000000", width=1.6)

    for v1, v2 in solid_edges:
        cv.add_line(pts_2d[v1], pts_2d[v2], dashed=False, stroke="#000000", width=1.6)

    # 3. 辅助线/对角线
    if diagonals:
        for v1, v2, col in diagonals:
            if v1 in pts_2d and v2 in pts_2d:
                cv.add_line(pts_2d[v1], pts_2d[v2], dashed=True, stroke=col, width=1.8)

    # 4. 顶点标注
    offsets = {
        "A": (-14, 14), "B": (14, 14), "C": (16, -2), "D": (-16, -4),
        "A1": (-16, -6), "B1": (16, -4), "C1": (14, -8), "D1": (-16, -8),
    }
    for k, pt in pts_2d.items():
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, k, offset=offsets.get(k, (0, 0)))

    if title:
        cv.add_text((canvas_size[0] // 2, canvas_size[1] - 20), title, size=14, italic=False, bold=False)

    return cv


def build_triangular_prism(
    a: float = 1.4,
    b: float = 2.0,
    h: float = 2.0,
    title: str = "直三棱柱模型: 侧棱垂直于底面",
    canvas_size: Tuple[int, int] = (420, 340),
    origin: Tuple[float, float] = (160, 250),
    scale: float = 85.0,
) -> SVGCanvas:
    """构造直三棱柱 ABC-A1B1C1"""
    eng = StereoEngine(origin=origin, scale=scale)
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])

    coords_3d = {
        "A": (a, 0.0, 0.0),
        "B": (a, b, 0.0),
        "C": (0.0, b / 2, 0.0),  # 后方遮挡
        "A1": (a, 0.0, h),
        "B1": (a, b, h),
        "C1": (0.0, b / 2, h),
    }
    pts_2d = {k: eng.p(*v) for k, v in coords_3d.items()}

    # 虚线: 涉及 C 的棱
    for v1, v2 in [("A", "C"), ("B", "C"), ("C", "C1")]:
        cv.add_line(pts_2d[v1], pts_2d[v2], dashed=True)

    # 实线
    for v1, v2 in [
        ("A", "B"), ("A1", "B1"), ("B1", "C1"), ("C1", "A1"),
        ("A", "A1"), ("B", "B1")
    ]:
        cv.add_line(pts_2d[v1], pts_2d[v2], dashed=False)

    offsets = {
        "A": (-14, 14), "B": (14, 14), "C": (0, -10),
        "A1": (-16, -6), "B1": (16, -4), "C1": (0, -12),
    }
    for k, pt in pts_2d.items():
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, k, offset=offsets[k])

    if title:
        cv.add_text((canvas_size[0] // 2, canvas_size[1] - 20), title, size=14, italic=False, bold=False)

    return cv


def build_square_pyramid(
    base_x: float = 1.6,
    base_y: float = 2.0,
    h: float = 2.4,
    show_height_line: bool = True,
    title: str = "正四棱锥模型: 高线 PO 垂直底面中心",
    canvas_size: Tuple[int, int] = (420, 340),
    origin: Tuple[float, float] = (160, 250),
    scale: float = 85.0,
) -> SVGCanvas:
    """构造正四棱锥 P-ABCD"""
    eng = StereoEngine(origin=origin, scale=scale)
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])

    coords_3d = {
        "A": (0.0, 0.0, 0.0),       # 后左 (虚)
        "D": (0.0, base_y, 0.0),    # 后右 (虚)
        "B": (base_x, 0.0, 0.0),    # 前左
        "C": (base_x, base_y, 0.0), # 前右
        "P": (base_x / 2, base_y / 2, h),
        "O": (base_x / 2, base_y / 2, 0.0),
    }
    pts_2d = {k: eng.p(*v) for k, v in coords_3d.items()}

    # 底面棱
    cv.add_line(pts_2d["A"], pts_2d["D"], dashed=True)
    cv.add_line(pts_2d["A"], pts_2d["B"], dashed=False)
    cv.add_line(pts_2d["B"], pts_2d["C"], dashed=False)
    cv.add_line(pts_2d["C"], pts_2d["D"], dashed=False)

    # 侧棱
    cv.add_line(pts_2d["P"], pts_2d["A"], dashed=True)
    cv.add_line(pts_2d["P"], pts_2d["B"], dashed=False)
    cv.add_line(pts_2d["P"], pts_2d["C"], dashed=False)
    cv.add_line(pts_2d["P"], pts_2d["D"], dashed=False)

    # 高线与底面对角线
    if show_height_line:
        cv.add_line(pts_2d["A"], pts_2d["C"], dashed=True, stroke="#666666", width=1.2)
        cv.add_line(pts_2d["B"], pts_2d["D"], dashed=True, stroke="#666666", width=1.2)
        cv.add_line(pts_2d["P"], pts_2d["O"], dashed=True, stroke="#dc2626", width=1.8)
        cv.add_circle(pts_2d["O"], r=2.5, fill="#dc2626")

    offsets = {
        "P": (0, -12), "A": (-14, 2), "B": (-12, 14),
        "C": (14, 14), "D": (14, 0), "O": (12, 4),
    }
    for k, pt in pts_2d.items():
        if k == "O" and not show_height_line:
            continue
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, k, offset=offsets.get(k, (0, 0)))

    if title:
        cv.add_text((canvas_size[0] // 2, canvas_size[1] - 20), title, size=14, italic=False, bold=False)

    return cv


def build_custom_polyhedron(
    vertices: Dict[str, Tuple[float, float, float]],
    edges: List[Dict],
    faces: Optional[List[Dict]] = None,
    title: str = "",
    canvas_size: Tuple[int, int] = (460, 360),
    origin: Tuple[float, float] = (180, 260),
    scale: float = 80.0,
) -> SVGCanvas:
    """
    通用自定义多面体构造器（供 AI Agent 或配置文件输入）
    :param vertices: 顶点坐标映射 {"A": (x,y,z), "B": ...}
    :param edges: 边定义列表 [{"from": "A", "to": "B", "dashed": False, "stroke": "#000", "width": 1.6}]
    :param faces: 表面/截面多边形定义 [{"vertices": ["A","B","C"], "fill": "rgba(...)"}]
    """
    eng = StereoEngine(origin=origin, scale=scale)
    cv = SVGCanvas(width=canvas_size[0], height=canvas_size[1])

    pts_2d = {k: eng.p(*v) for k, v in vertices.items()}

    # 1. 绘制面
    if faces:
        for face in faces:
            f_pts = [pts_2d[v] for v in face.get("vertices", []) if v in pts_2d]
            if len(f_pts) >= 3:
                cv.add_polygon(
                    f_pts,
                    fill=face.get("fill", "rgba(240, 240, 240, 0.4)"),
                    stroke=face.get("stroke", "none"),
                )

    # 2. 绘制边
    for edge in edges:
        v1, v2 = edge["from"], edge["to"]
        if v1 in pts_2d and v2 in pts_2d:
            cv.add_line(
                pts_2d[v1],
                pts_2d[v2],
                dashed=edge.get("dashed", False),
                stroke=edge.get("stroke", "#000000"),
                width=edge.get("width", 1.6),
                arrow=edge.get("arrow", False),
            )

    # 3. 标注顶点
    for k, pt in pts_2d.items():
        cv.add_circle(pt, r=3.0)
        cv.add_text(pt, k, offset=(10, -8))

    if title:
        cv.add_text((canvas_size[0] // 2, canvas_size[1] - 20), title, size=14, italic=False, bold=False)

    return cv
