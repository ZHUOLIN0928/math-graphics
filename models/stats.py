# -*- coding: utf-8 -*-
"""
math_graphics.models.stats
高考统计与概率标准图表生成器 (真卷黑白出版风格)
规范：
1. 试卷级黑白纯正排版，杜绝刺眼杂色
2. 正态总体密度曲线平滑覆盖 (黑实线) 与频率折线 (黑虚线)
3. 文本白底防遮挡光晕 (halo=True)，彻底避免与曲线/柱线重叠
"""

import math
from pathlib import Path
from typing import List, Optional, Union, Tuple
from ..core.canvas import SVGCanvas


def build_histogram_with_density_curve(
    bins: Optional[List[float]] = None,
    heights: Optional[List[float]] = None,
    output_path: Optional[Union[str, Path]] = None,
    show_curve: bool = True,
    show_polygon: bool = True,
    median: Optional[float] = 78.57,
    mode: Optional[float] = 75.0,
    title: str = "频率分布直方图与正态总体密度曲线",
    canvas_size: Tuple[int, int] = (520, 360),
) -> SVGCanvas:
    """
    绘制包含正态总体密度曲线与频率折线的高考标准直方图 (黑白试卷风格)
    """
    if bins is None:
        bins = [50, 60, 70, 80, 90, 100]
    if heights is None:
        heights = [0.005, 0.015, 0.035, 0.030, 0.015]

    w, h = canvas_size
    cv = SVGCanvas(width=w, height=h)

    left = 65
    right = w - 45
    bottom = h - 65
    top = 45

    plot_w = right - left
    plot_h = bottom - top

    min_x, max_x = min(bins), max(bins)
    max_y = max(heights) * 1.38

    def to_screen(x: float, y: float) -> Tuple[float, float]:
        sx = left + (x - min_x) / (max_x - min_x) * plot_w
        sy = bottom - (y / max_y) * plot_h
        return round(sx, 2), round(sy, 2)

    # 1. 矩形柱 (黑边极浅灰底)
    mid_points = []
    for i in range(len(bins) - 1):
        x1, x2 = bins[i], bins[i + 1]
        y_val = heights[i] if i < len(heights) else 0

        p_bl = to_screen(x1, 0)
        p_tl = to_screen(x1, y_val)
        p_tr = to_screen(x2, y_val)
        p_br = to_screen(x2, 0)

        cv.add_polygon([p_bl, p_tl, p_tr, p_br], fill="rgba(0, 0, 0, 0.04)", stroke="#000000", width=1.5)

        mid_x = (x1 + x2) / 2
        p_mid = to_screen(mid_x, y_val)
        mid_points.append((mid_x, y_val, p_mid))

        # 柱顶数值
        cv.add_text(p_mid, f"{y_val:.3f}", offset=(0, -7), size=11, italic=False, bold=True, halo=True)

    # 2. 频率分布折线图 (黑虚线连接各中点，首尾接地)
    if show_polygon and mid_points:
        poly_pts = [to_screen(bins[0] - (bins[1] - bins[0]) / 2, 0)]
        for _, _, pt in mid_points:
            poly_pts.append(pt)
        poly_pts.append(to_screen(bins[-1] + (bins[-1] - bins[-2]) / 2, 0))

        for j in range(len(poly_pts) - 1):
            cv.add_line(poly_pts[j], poly_pts[j + 1], dashed=True, stroke="#475569", width=1.3)
            if 0 < j < len(poly_pts) - 1:
                cv.add_circle(poly_pts[j], r=2.5, fill="#000000")

    # 3. 光滑正态分布密度曲线 (加粗黑实线 2.2px)
    if show_curve:
        total_freq = sum(h_val * (bins[i + 1] - bins[i]) for i, h_val in enumerate(heights))
        mu = sum(mid_points[i][0] * heights[i] * (bins[i + 1] - bins[i]) for i in range(len(heights))) / total_freq
        variance = sum(
            ((mid_points[i][0] - mu) ** 2) * heights[i] * (bins[i + 1] - bins[i]) for i in range(len(heights))
        ) / total_freq
        sigma = math.sqrt(variance)

        curve_screen_pts = []
        samples = 60
        for s in range(samples + 1):
            cx = min_x - 3 + s * ((max_x - min_x + 6) / samples)
            gauss_y = (1.0 / (math.sqrt(2 * math.pi) * sigma)) * math.exp(-((cx - mu) ** 2) / (2 * sigma ** 2))
            curve_screen_pts.append(to_screen(cx, gauss_y))

        d_path = f"M {curve_screen_pts[0][0]} {curve_screen_pts[0][1]}"
        for pt in curve_screen_pts[1:]:
            d_path += f" L {pt[0]} {pt[1]}"
        cv.elements.append(
            f'<path d="{d_path}" fill="none" stroke="#000000" stroke-width="2.2" stroke-linecap="round" />'
        )
        cv.add_text(
            to_screen(mu, 1.0 / (math.sqrt(2 * math.pi) * sigma)),
            "总体密度曲线 N(μ, σ²)",
            offset=(35, -12),
            size=11,
            fill="#000000",
            italic=False,
            bold=True,
            halo=True,
        )

    # 4. 坐标轴与刻度
    cv.add_line((left, bottom), (right + 18, bottom), arrow=True, stroke="#000000", width=1.6)
    cv.add_text((right + 22, bottom + 4), "区间", size=12, italic=False, bold=False, anchor="start", halo=True)
    cv.add_line((left, bottom), (left, top - 18), arrow=True, stroke="#000000", width=1.6)
    cv.add_text((left, top - 24), "频率/组距", size=12, italic=False, bold=False, anchor="middle", halo=True)

    for b in bins:
        pt = to_screen(b, 0)
        cv.add_line(pt, (pt[0], pt[1] + 5), stroke="#000000", width=1.4)
        cv.add_text(pt, str(int(b) if b == int(b) else b), offset=(0, 18), size=12, italic=False, halo=True)

    # 5. 中位数二等分垂直虚线 (实黑虚线)
    if median is not None:
        p_med_bot = to_screen(median, 0)
        p_med_top = to_screen(median, 0.035)
        cv.add_line(p_med_bot, p_med_top, dashed=True, stroke="#000000", width=1.8)
        cv.add_circle(p_med_top, r=2.5, fill="#000000")
        cv.add_text(p_med_top, f"中位数 ≈ {median:.1f}", offset=(15, -6), size=11, fill="#000000", italic=False, bold=True, anchor="start", halo=True)

    if title:
        cv.add_text((w // 2, h - 12), title, size=13, italic=False, bold=False, halo=False)

    if output_path:
        cv.save(Path(output_path))

    return cv


build_histogram = build_histogram_with_density_curve


def build_tree_diagram(
    output_path: Optional[Union[str, Path]] = None,
    title: str = "古典概型两步全树状图: P(E) = m / n",
    canvas_size: Tuple[int, int] = (480, 280),
) -> SVGCanvas:
    """纯矢量 SVG 绘制古典概型全树状图 (黑白试卷风格)"""
    w, h = canvas_size
    cv = SVGCanvas(width=w, height=h)
    root_p = (50, h // 2)
    cv.add_polygon(
        [(root_p[0] - 35, root_p[1] - 16), (root_p[0] + 35, root_p[1] - 16),
         (root_p[0] + 35, root_p[1] + 16), (root_p[0] - 35, root_p[1] + 16)],
        fill="#f8fafc", stroke="#000000", width=1.5
    )
    cv.add_text(root_p, "试验开始", offset=(0, 4), size=12, italic=False, bold=True, halo=True)
    step1_pts = [(180, 70), (180, 210)]
    labels_1 = ["事件 A (p=0.5)", "事件 B (p=0.5)"]
    for i, pt in enumerate(step1_pts):
        cv.add_line((root_p[0] + 35, root_p[1]), (pt[0] - 40, pt[1]), arrow=True, stroke="#000000", width=1.6)
        cv.add_polygon(
            [(pt[0] - 40, pt[1] - 14), (pt[0] + 40, pt[1] - 14),
             (pt[0] + 40, pt[1] + 14), (pt[0] - 40, pt[1] + 14)],
            fill="#ffffff", stroke="#000000", width=1.4
        )
        cv.add_text(pt, labels_1[i], offset=(0, 4), size=11, italic=False, bold=True, halo=True)
        step2_ys = [pt[1] - 35, pt[1] + 35]
        labels_2 = [f"结果 {i*2+1}", f"结果 {i*2+2}"]
        for j, y2 in enumerate(step2_ys):
            pt2 = (330, y2)
            cv.add_line((pt[0] + 40, pt[1]), (pt2[0] - 35, pt2[1]), arrow=True, stroke="#000000", width=1.4)
            cv.add_polygon(
                [(pt2[0] - 35, pt2[1] - 12), (pt2[0] + 35, pt2[1] - 12),
                 (pt2[0] + 35, pt2[1] + 12), (pt2[0] - 35, pt2[1] + 12)],
                fill="#ffffff", stroke="#000000", width=1.2
            )
            cv.add_text(pt2, labels_2[j], offset=(0, 4), size=11, fill="#000000", italic=False, halo=True)
            cv.add_text((pt2[0] + 65, pt2[1] + 4), "P = 1/4", size=12, fill="#000000", bold=True, italic=True, halo=True)
    if title:
        cv.add_text((w // 2, h - 14), title, size=13, italic=False, bold=False, halo=False)
    if output_path:
        cv.save(Path(output_path))
    return cv
