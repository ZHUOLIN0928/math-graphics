# -*- coding: utf-8 -*-
"""
math_graphics.core.projection
立体几何斜二测画法 (Axonometric / Cabinet-like Projection) 引擎
严格遵循中国高中数学与高考试卷制图标准：
- x 轴向前偏左倾斜 45°，长减半 (ratio = 0.5)
- y 轴水平向右，长度不变 (ratio = 1.0)
- z 轴竖直向上，长度不变 (ratio = 1.0)
"""

import math
from typing import Tuple, List, Union


class StereoEngine:
    """斜二测画法 3D -> 2D 投影与几何变换引擎"""

    def __init__(
        self,
        origin: Tuple[float, float] = (200, 240),
        scale: float = 75.0,
        angle_deg: float = 45.0,
        ratio: float = 0.5,
    ):
        """
        :param origin: 画布上 3D 原点 (0,0,0) 对应的 (px, py)
        :param scale: 缩放因子（每数学单位对应的像素数）
        :param angle_deg: x 轴倾斜角度（默认 45°）
        :param ratio: x 轴缩放比例（默认 0.5）
        """
        self.ox, self.oy = origin
        self.scale = scale
        self.angle = math.radians(angle_deg)
        self.ratio = ratio

    def project(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """将 3D 空间坐标 (x, y, z) 投影为 2D 屏幕坐标 (u, v)"""
        u = self.ox + y * self.scale - x * self.scale * self.ratio * math.cos(self.angle)
        v = self.oy - z * self.scale + x * self.scale * self.ratio * math.sin(self.angle)
        return round(u, 2), round(v, 2)

    def p(self, x: float, y: float, z: float) -> Tuple[float, float]:
        """project 的简写"""
        return self.project(x, y, z)

    def get_right_angle_3d_points(
        self,
        o: Tuple[float, float, float],
        p1: Tuple[float, float, float],
        p2: Tuple[float, float, float],
        size: float = 0.25,
    ) -> List[Tuple[float, float]]:
        """
        计算空间三点构成的直角符号折角折线点集 (投影到 2D 屏幕)
        :param o: 直角顶点 (x, y, z)
        :param p1: 直角边 1 上的点
        :param p2: 直角边 2 上的点
        :param size: 折角符号的空间尺寸
        :return: 投影后的折线 3 个 2D 点 [(u1, v1), (u2, v2), (u3, v3)]
        """
        v1 = [p1[i] - o[i] for i in range(3)]
        v2 = [p2[i] - o[i] for i in range(3)]
        l1 = math.sqrt(sum(x**2 for x in v1))
        l2 = math.sqrt(sum(x**2 for x in v2))
        if l1 == 0 or l2 == 0:
            return []
        u1 = [x / l1 * size for x in v1]
        u2 = [x / l2 * size for x in v2]

        pt1 = [o[i] + u1[i] for i in range(3)]
        pt2 = [o[i] + u1[i] + u2[i] for i in range(3)]
        pt3 = [o[i] + u2[i] for i in range(3)]

        return [self.p(*pt1), self.p(*pt2), self.p(*pt3)]


def compute_smart_label_offset(
    p0: Tuple[float, float],
    neighbors: List[Tuple[float, float]],
    dist: float = 16.0,
    fallback_dir: Tuple[float, float] = (0.0, -1.0),
) -> Tuple[Tuple[float, float], str]:
    """
    智能外推避让算法：
    根据与顶点相连的所有边线向量计算反向角平分线单位向量，
    将字母向外侧空白区推离，并自适应确定 text-anchor。
    :return: ((dx, dy), anchor)
    """
    if not neighbors:
        return ((0.0, -dist), "middle")

    sum_x, sum_y = 0.0, 0.0
    for pn in neighbors:
        vx = pn[0] - p0[0]
        vy = pn[1] - p0[1]
        length = math.hypot(vx, vy)
        if length > 1e-4:
            sum_x += vx / length
            sum_y += vy / length

    # 推离方向为邻接边向量和的反向
    push_x = -sum_x
    push_y = -sum_y
    push_len = math.hypot(push_x, push_y)

    if push_len < 0.15:
        # 对称或直线节点，使用回退方向
        push_x, push_y = fallback_dir
        push_len = math.hypot(push_x, push_y)

    ux = (push_x / push_len) * dist
    uy = (push_y / push_len) * dist

    # 垂直基线微调
    dy = uy + (4.0 if uy < 0 else 6.0)

    # 水平对齐自适应
    if ux > 4.0:
        anchor = "start"
        dx = ux + 2.0
    elif ux < -4.0:
        anchor = "end"
        dx = ux - 2.0
    else:
        anchor = "middle"
        dx = ux

    return ((round(dx, 2), round(dy, 2)), anchor)
