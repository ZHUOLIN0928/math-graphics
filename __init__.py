# -*- coding: utf-8 -*-
"""
math_graphics
高考数学与物理试卷级标准题图生成与渲染工具链
包含：立体几何（标准几何体与异形翻折/截割体）、平面几何与定理、统计与正态密度曲线、高中物理核心趋势图与模型图。
"""

from .core.canvas import SVGCanvas
from .core.projection import StereoEngine
from .core.renderer import render_svg_to_png, batch_render_directory
from .models.solids import (
    build_cube,
    build_triangular_prism,
    build_square_pyramid,
    build_custom_polyhedron,
)
from .models.complex_solids import (
    build_folded_tetrahedron,
    build_corner_cut_cube,
)
from .models.plane import (
    build_vector_addition,
    build_vector_subtraction,
    build_vector_coordinates,
    build_vector_dot_product,
    build_triangle_sine_circumcircle,
    build_survey_angles,
    build_theorem_diagram,
)
from .models.stats import build_histogram_with_density_curve
from .models.physics import (
    build_vt_diagram,
    build_ui_characteristics_diagram,
    build_particle_deflection_diagram,
)

__version__ = "1.1.0"

__all__ = [
    "SVGCanvas",
    "StereoEngine",
    "render_svg_to_png",
    "batch_render_directory",
    "build_cube",
    "build_triangular_prism",
    "build_square_pyramid",
    "build_custom_polyhedron",
    "build_folded_tetrahedron",
    "build_corner_cut_cube",
    "build_vector_addition",
    "build_vector_subtraction",
    "build_vector_coordinates",
    "build_vector_dot_product",
    "build_triangle_sine_circumcircle",
    "build_survey_angles",
    "build_theorem_diagram",
    "build_histogram_with_density_curve",
    "build_vt_diagram",
    "build_ui_characteristics_diagram",
    "build_particle_deflection_diagram",
]
