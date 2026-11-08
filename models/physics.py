# -*- coding: utf-8 -*-
"""
math_graphics.models.physics
高中物理试卷级标准题图与状态趋势图生成器 (真卷黑白出版风格)
严格按照高考真卷排版规范：
- 坐标轴带标准刻度与变量单位
- 纯净黑色墨迹，杜绝任何多余描边与白斑
- 标签精准布局在图形与线段外围空白区，零压线零重合
"""

import math
from pathlib import Path
from typing import Tuple, Optional, Union
from ..core.canvas import SVGCanvas


def build_vt_diagram(
    canvas_size: Tuple[int, int] = (480, 320),
    title: str = "运动学 v-t 过程分析图 (斜率对应加速度，面积对应位移)",
) -> SVGCanvas:
    """高中物理运动学 v-t 阶段趋势图 (真实高考试卷规范)"""
    w, h = canvas_size
    cv = SVGCanvas(width=w, height=h)

    # 坐标系原点与边界
    ox, oy = 60, 240
    right = w - 40
    top = 40

    # 运动节点数据: 梯形匀加速 -> 匀速 -> 匀减速
    p_O = (ox, oy)
    p_A = (150, 90)   # 达到最大速度
    p_B = (270, 90)   # 匀速结束
    p_C = (380, oy)   # 停止

    # 1. 位移面积阴影 (极浅学术灰，透明度 0.05)
    cv.add_polygon([p_O, p_A, p_B, p_C], fill="rgba(0, 0, 0, 0.05)", stroke="none")

    # 2. 坐标轴
    # t 轴
    cv.add_line((ox, oy), (right, oy), arrow=True, stroke="#000000", width=1.8)
    cv.add_text((right + 8, oy + 4), "t / s", size=13, italic=True, bold=False, anchor="start")
    # v 轴
    cv.add_line((ox, oy), (ox, top), arrow=True, stroke="#000000", width=1.8)
    cv.add_text((ox, top - 14), "v / (m·s⁻¹)", size=13, italic=True, bold=False, anchor="middle")
    # 原点 O
    cv.add_text((ox - 10, oy + 16), "O", size=13, italic=True)

    # 3. v-t 运动曲线 (加粗实黑线 2.2px)
    cv.add_line(p_O, p_A, stroke="#000000", width=2.2)
    cv.add_line(p_A, p_B, stroke="#000000", width=2.2)
    cv.add_line(p_B, p_C, stroke="#000000", width=2.2)

    # 4. 辅助投影虚线 (细黑虚线 1.2px)
    cv.add_line(p_A, (p_A[0], oy), dashed=True, stroke="#000000", width=1.2)
    cv.add_line(p_B, (p_B[0], oy), dashed=True, stroke="#000000", width=1.2)
    cv.add_line(p_A, (ox, p_A[1]), dashed=True, stroke="#000000", width=1.2)

    # 5. 坐标轴刻度与数值标注 (严格放置在坐标轴外侧空白区)
    # v 轴刻度
    cv.add_line((ox - 4, p_A[1]), (ox, p_A[1]), stroke="#000000", width=1.4)
    cv.add_text((ox - 8, p_A[1] + 4), "v_m", size=13, italic=True, bold=True, anchor="end")

    # t 轴刻度
    for tx, tlabel in [(p_A[0], "t₁"), (p_B[0], "t₂"), (p_C[0], "t₃")]:
        cv.add_line((tx, oy), (tx, oy + 4), stroke="#000000", width=1.4)
        cv.add_text((tx, oy + 18), tlabel, size=13, italic=True, bold=True, anchor="middle")

    # 6. 图内说明与物理意义标注 (居中于空白区，绝不压线)
    cv.add_text((210, 160), "位移 x = 梯形面积 S", size=12, fill="#000000", bold=True, italic=False)

    # 加速度引线标注 (放在图像外部上方，带指引线)
    # 匀加速段指引线
    cv.add_line((105, 165), (85, 125), stroke="#64748b", width=1.0)
    cv.add_line((85, 125), (45, 125), stroke="#64748b", width=1.0)
    cv.add_text((42, 120), "a₁ > 0 (匀加速)", size=11, fill="#000000", anchor="end")

    # 匀减速段指引线
    cv.add_line((325, 165), (345, 125), stroke="#64748b", width=1.0)
    cv.add_line((345, 125), (395, 125), stroke="#64748b", width=1.0)
    cv.add_text((398, 120), "a₂ < 0 (匀减速)", size=11, fill="#000000", anchor="start")

    # 顶部匀速标注
    cv.add_text((210, 78), "a = 0 (匀速)", size=11, fill="#000000")

    if title:
        cv.add_text((w // 2, h - 14), title, size=12, italic=False, bold=False)

    return cv


def build_ui_characteristics_diagram(
    canvas_size: Tuple[int, int] = (480, 320),
    title: str = "闭合电路 U-I 特性综合图: 电源外特性与小灯泡伏安特性",
) -> SVGCanvas:
    """闭合电路 U-I 特性综合分析图 (黑白真卷风格)"""
    w, h = canvas_size
    cv = SVGCanvas(width=w, height=h)

    ox, oy = 60, 240
    right = w - 40
    top = 40

    cv.add_line((ox, oy), (right, oy), arrow=True, stroke="#000000", width=1.8)
    cv.add_text((right + 8, oy + 4), "I / A", size=13, italic=True, bold=False, anchor="start")
    cv.add_line((ox, oy), (ox, top), arrow=True, stroke="#000000", width=1.8)
    cv.add_text((ox, top - 14), "U / V", size=13, italic=True, bold=False, anchor="middle")
    cv.add_text((ox - 10, oy + 16), "O", size=13, italic=True)

    # 1. 电源外特性直线: U = E - Ir (加粗黑实线 2.2px)
    p_E = (ox, 70)
    p_Ishort = (360, oy)
    cv.add_line(p_E, p_Ishort, stroke="#000000", width=2.2)

    # 轴截距标注
    cv.add_line((ox - 4, p_E[1]), (ox, p_E[1]), stroke="#000000", width=1.4)
    cv.add_text((ox - 8, p_E[1] + 4), "E", size=13, fill="#000000", bold=True, italic=True, anchor="end")

    cv.add_line((p_Ishort[0], oy), (p_Ishort[0], oy + 4), stroke="#000000", width=1.4)
    cv.add_text((p_Ishort[0], oy + 18), "I_短", size=12, fill="#000000", bold=True, italic=True)

    # 2. 小灯泡非线性伏安特性曲线 (黑实线，向上凸起)
    p_bulb_start = (ox, oy)
    p_control1 = (ox + 120, oy - 130)
    p_control2 = (ox + 190, oy - 150)
    p_bulb_end = (330, 80)
    path_d = f"M {p_bulb_start[0]} {p_bulb_start[1]} C {p_control1[0]} {p_control1[1]}, {p_control2[0]} {p_control2[1]}, {p_bulb_end[0]} {p_bulb_end[1]}"
    cv.elements.append(
        f'<path d="{path_d}" fill="none" stroke="#000000" stroke-width="2.2" stroke-linecap="round" />'
    )

    # 3. 实际工作点 P(I0, U0) 交点
    p_work = (205, 145)
    cv.add_circle(p_work, r=3.5, fill="#000000")
    cv.add_line(p_work, (ox, p_work[1]), dashed=True, stroke="#000000", width=1.2)
    cv.add_line(p_work, (p_work[0], oy), dashed=True, stroke="#000000", width=1.2)

    cv.add_text((ox - 8, p_work[1] + 4), "U₀", size=12, fill="#000000", bold=True, italic=True, anchor="end")
    cv.add_text((p_work[0], oy + 18), "I₀", size=12, fill="#000000", bold=True, italic=True)
    cv.add_text((p_work[0] + 10, p_work[1] - 8), "P (工作点)", size=12, fill="#000000", bold=True, italic=False)

    # 曲线名称与公式
    cv.add_text((310, 64), "灯泡: 电阻随温度增大", size=11, fill="#000000", italic=False)
    cv.add_text((305, 120), "电源: U = E - Ir", size=11, fill="#000000", italic=False)

    if title:
        cv.add_text((w // 2, h - 14), title, size=12, italic=False, bold=False)

    return cv


def build_particle_deflection_diagram(
    canvas_size: Tuple[int, int] = (500, 320),
    title: str = "静电场模型: 带电粒子在平行极板电场中的偏转轨迹",
) -> SVGCanvas:
    """高二物理电磁学：带电粒子在平行偏转电场中偏转模型 (黑白试卷风格)"""
    w, h = canvas_size
    cv = SVGCanvas(width=w, height=h)

    plate_x1, plate_x2 = 120, 340
    top_y = 80
    bot_y = 200

    # 1. 金属极板 (黑边灰色填充)
    cv.add_polygon(
        [(plate_x1, top_y - 8), (plate_x2, top_y - 8), (plate_x2, top_y), (plate_x1, top_y)],
        fill="#f1f5f9", stroke="#000000", width=1.5
    )
    cv.add_text((plate_x1 - 18, top_y - 1), "+ + + +", size=12, fill="#000000", bold=True)
    cv.add_text((plate_x2 + 25, top_y - 1), "上极板 (+)", size=11, fill="#000000")

    cv.add_polygon(
        [(plate_x1, bot_y), (plate_x2, bot_y), (plate_x2, bot_y + 8), (plate_x1, bot_y + 8)],
        fill="#f1f5f9", stroke="#000000", width=1.5
    )
    cv.add_text((plate_x1 - 18, bot_y + 7), "- - - -", size=13, fill="#000000", bold=True)
    cv.add_text((plate_x2 + 25, bot_y + 7), "下极板 (-)", size=11, fill="#000000")

    # 尺寸标注 (L 与 d)
    cv.add_line((plate_x1, 230), (plate_x2, 230), stroke="#000000", width=1.2)
    cv.add_line((plate_x1, 226), (plate_x1, 234), stroke="#000000", width=1.2)
    cv.add_line((plate_x2, 226), (plate_x2, 234), stroke="#000000", width=1.2)
    cv.add_text(((plate_x1 + plate_x2) / 2, 246), "极板长度 L", size=11, fill="#000000")

    # 板间距 d 标注
    cv.add_line((plate_x1 - 32, top_y), (plate_x1 - 32, bot_y), stroke="#000000", width=1.2)
    cv.add_line((plate_x1 - 36, top_y), (plate_x1 - 28, top_y), stroke="#000000", width=1.2)
    cv.add_line((plate_x1 - 36, bot_y), (plate_x1 - 28, bot_y), stroke="#000000", width=1.2)
    cv.add_text((plate_x1 - 44, (top_y + bot_y) / 2 + 4), "d", size=12, italic=True, fill="#000000")

    # 电场线向下细黑箭头
    for ex in [160, 200, 240, 280, 320]:
        cv.add_line((ex, top_y + 2), (ex, bot_y - 2), arrow=True, stroke="#64748b", width=1.0)
    cv.add_text((240, 115), "匀强电场 E", size=11, fill="#64748b")

    # 2. 中线
    mid_y = (top_y + bot_y) / 2
    cv.add_line((40, mid_y), (440, mid_y), dashed=True, stroke="#64748b", width=1.2)

    # 粒子初速度
    cv.add_circle((60, mid_y), r=4.0, fill="#000000")
    cv.add_text((60, mid_y - 12), "+q, m", size=12, fill="#000000", bold=True)
    cv.add_line((60, mid_y), (110, mid_y), arrow=True, stroke="#000000", width=1.8)
    cv.add_text((85, mid_y - 8), "v₀", size=13, fill="#000000", bold=True, italic=True)

    # 3. 偏转抛物线轨迹 (加粗实黑线)
    traj_pts = []
    samples = 30
    for s in range(samples + 1):
        curr_x = plate_x1 + s * ((plate_x2 - plate_x1) / samples)
        norm_x = s / samples
        curr_y = mid_y + norm_x ** 2 * 45.0
        traj_pts.append((round(curr_x, 2), round(curr_y, 2)))

    traj_d = f"M {traj_pts[0][0]} {traj_pts[0][1]}"
    for pt in traj_pts[1:]:
        traj_d += f" L {pt[0]} {pt[1]}"
    cv.elements.append(
        f'<path d="{traj_d}" fill="none" stroke="#000000" stroke-width="2.2" stroke-linecap="round" />'
    )

    # 4. 出射点与速度偏转角
    exit_p = traj_pts[-1]
    cv.add_circle(exit_p, r=3.0, fill="#000000")

    # 侧移距离 y 标注
    cv.add_line((plate_x2 + 8, mid_y), (plate_x2 + 8, exit_p[1]), stroke="#000000", width=1.4)
    cv.add_line((plate_x2 + 4, mid_y), (plate_x2 + 12, mid_y), stroke="#000000", width=1.4)
    cv.add_line((plate_x2 + 4, exit_p[1]), (plate_x2 + 12, exit_p[1]), stroke="#000000", width=1.4)
    cv.add_text((plate_x2 + 16, (mid_y + exit_p[1]) / 2 + 4), "侧移 y", size=11, fill="#000000", bold=True)

    # 射出速度矢量
    cv.add_line(exit_p, (exit_p[0] + 55, exit_p[1] + 25), arrow=True, stroke="#000000", width=1.8)
    cv.add_text((exit_p[0] + 62, exit_p[1] + 25), "v", size=13, fill="#000000", bold=True, italic=True)

    # 角度 θ
    cv.add_line(exit_p, (exit_p[0] + 50, exit_p[1]), dashed=True, stroke="#64748b", width=1.2)
    cv.add_arc(exit_p, 26, 0, 24, stroke="#000000")
    cv.add_text(exit_p, "θ", offset=(32, 14), fill="#000000", size=13)

    if title:
        cv.add_text((w // 2, h - 14), title, size=12, italic=False, bold=False)

    return cv
