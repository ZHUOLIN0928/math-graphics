# -*- coding: utf-8 -*-
"""
math_graphics.core.canvas
高考标准试卷级矢量 SVG 画布引擎
零外部依赖，纯 Python 原生生成试卷黑白/彩色标注矢量图。
"""

import math
from pathlib import Path
from typing import List, Tuple, Optional, Union


class SVGCanvas:
    """标准试卷矢量绘图画布"""

    def __init__(self, width: int = 460, height: int = 340, bg: str = "#ffffff"):
        self.width = width
        self.height = height
        self.bg = bg
        self.elements: List[str] = []
        self.defs: List[str] = []
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

    def add_line(
        self,
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        dashed: bool = False,
        stroke: str = "#000000",
        width: float = 1.6,
        arrow: bool = False,
        arrow_color: str = "",
    ):
        """添加直线段（实线或虚线）"""
        dash = 'stroke-dasharray="5,4"' if dashed else ''
        marker = f'marker-end="url(#{arrow_color if arrow_color else "arrow"})"' if arrow else ''
        self.elements.append(
            f'<line x1="{p1[0]}" y1="{p1[1]}" x2="{p2[0]}" y2="{p2[1]}" '
            f'stroke="{stroke}" stroke-width="{width}" {dash} {marker} stroke-linecap="round" />'
        )

    def add_polygon(
        self,
        pts: List[Tuple[float, float]],
        fill: str = "rgba(240, 240, 240, 0.5)",
        stroke: str = "#000000",
        width: float = 1.5,
    ):
        """添加填充多边形（如几何体表面、截面）"""
        pts_str = " ".join([f"{p[0]},{p[1]}" for p in pts])
        self.elements.append(
            f'<polygon points="{pts_str}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round" />'
        )

    def add_circle(
        self,
        p: Tuple[float, float],
        r: float = 3.0,
        fill: str = "#000000",
        stroke: str = "none",
        width: float = 1.0,
    ):
        """添加圆或顶点实体圆点"""
        self.elements.append(
            f'<circle cx="{p[0]}" cy="{p[1]}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" />'
        )

    def add_text(
        self,
        p: Tuple[float, float],
        text: str,
        offset: Tuple[float, float] = (0, 0),
        size: int = 15,
        italic: bool = True,
        bold: bool = True,
        anchor: str = "middle",
        fill: str = "#000000",
        font_family: str = "Times New Roman, Songti SC, SimSun, serif",
        halo: bool = False,
        halo_color: str = "#ffffff",
        halo_width: float = 4.5,
    ):
        """添加数学试卷风格纯净矢量文本标注"""
        tx = round(p[0] + offset[0], 2)
        ty = round(p[1] + offset[1], 2)
        it = 'font-style="italic"' if italic else ''
        bd = 'font-weight="bold"' if bold else ''
        safe_text = str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.elements.append(
            f'<text x="{tx}" y="{ty}" font-size="{size}" {it} {bd} font-family="{font_family}" fill="{fill}" text-anchor="{anchor}">{safe_text}</text>'
        )

    def add_arc(
        self,
        center: Tuple[float, float],
        r: float,
        start_ang: float,
        end_ang: float,
        stroke: str = "#000000",
        width: float = 1.2,
        dashed: bool = False,
    ):
        """添加圆弧（用于平面角、二面角标注）"""
        x1 = center[0] + r * math.cos(math.radians(start_ang))
        y1 = center[1] + r * math.sin(math.radians(start_ang))
        x2 = center[0] + r * math.cos(math.radians(end_ang))
        y2 = center[1] + r * math.sin(math.radians(end_ang))
        dash = 'stroke-dasharray="3,3"' if dashed else ''
        d = f"M {round(x1, 2)} {round(y1, 2)} A {r} {r} 0 0 1 {round(x2, 2)} {round(y2, 2)}"
        self.elements.append(f'<path d="{d}" stroke="{stroke}" stroke-width="{width}" fill="none" {dash} />')

    def add_right_angle_2d(
        self,
        o: Tuple[float, float],
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        size: float = 12.0,
        stroke: str = "#000000",
        width: float = 1.2,
    ):
        """绘制 2D 直角符号折角"""
        v1 = (p1[0] - o[0], p1[1] - o[1])
        v2 = (p2[0] - o[0], p2[1] - o[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        if l1 == 0 or l2 == 0:
            return
        u1 = (v1[0] / l1 * size, v1[1] / l1 * size)
        u2 = (v2[0] / l2 * size, v2[1] / l2 * size)
        q1 = (o[0] + u1[0], o[1] + u1[1])
        q2 = (o[0] + u1[0] + u2[0], o[1] + u1[1] + u2[1])
        q3 = (o[0] + u2[0], o[1] + u2[1])
        self.elements.append(
            f'<polyline points="{round(q1[0],2)},{round(q1[1],2)} {round(q2[0],2)},{round(q2[1],2)} {round(q3[0],2)},{round(q3[1],2)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="square" />'
        )

    def to_svg(self) -> str:
        """输出完整 SVG 字符串"""
        defs_str = "".join(self.defs)
        elems_str = "\n  ".join(self.elements)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}" style="background-color: {self.bg};">\n'
            f'{defs_str}\n  {elems_str}\n</svg>'
        )

    def save(self, filepath: Union[str, Path]) -> Path:
        """保存为 SVG 文件"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_svg(), encoding="utf-8")
        return path
