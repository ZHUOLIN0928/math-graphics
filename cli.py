#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
math_graphics.cli
高考数学标准题图统一命令行工具 (CLI)
用法示例：
  python3 -m math_graphics solid --shape cube --section A,C,C1,A1 --png -o cube_cut.svg
  python3 -m math_graphics plane --type vector-add --png -o vec_add.svg
  python3 -m math_graphics theorem --id geo_07 --png -o dihedral.svg
  python3 -m math_graphics stat --type histogram -o hist.png
  python3 -m math_graphics render input.svg -o output.png --scale 3.0
  python3 -m math_graphics batch-all -d ./figures
"""

import argparse
import sys
from pathlib import Path

from .core.canvas import SVGCanvas
from .core.renderer import render_svg_to_png, batch_render_directory
from .models.solids import (
    build_cube,
    build_triangular_prism,
    build_square_pyramid,
    build_custom_polyhedron,
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
from .models.stats import build_histogram, build_tree_diagram


def handle_solid(args):
    out_svg = Path(args.output).resolve()
    shape = args.shape.lower()

    if shape == "cube":
        section = [s.strip() for s in args.section.split(",")] if args.section else None
        cv = build_cube(
            a=args.size_x,
            b=args.size_y,
            c=args.size_z,
            section=section,
            title=args.title or "正方体/长方体模型",
        )
    elif shape in ["prism", "tri-prism"]:
        cv = build_triangular_prism(
            a=args.size_x,
            b=args.size_y,
            h=args.size_z,
            title=args.title or "直三棱柱模型",
        )
    elif shape in ["pyramid", "sq-pyramid"]:
        cv = build_square_pyramid(
            base_x=args.size_x,
            base_y=args.size_y,
            h=args.size_z,
            title=args.title or "正四棱锥模型",
        )
    else:
        print(f"❌ 不支持的立体几何类型: {shape} (支持: cube, prism, pyramid)", file=sys.stderr)
        sys.exit(1)

    cv.save(out_svg)
    print(f"✅ SVG 已生成: {out_svg}")

    if args.png:
        out_png = render_svg_to_png(out_svg, scale=args.scale)
        print(f"🎨 高清 PNG (300+ DPI) 渲染完成: {out_png}")


def handle_plane(args):
    out_svg = Path(args.output).resolve()
    t = args.type.lower()

    mapping = {
        "vector-add": build_vector_addition,
        "vector-sub": build_vector_subtraction,
        "vector-coord": build_vector_coordinates,
        "vector-dot": build_vector_dot_product,
        "triangle-sine": build_triangle_sine_circumcircle,
        "triangle-survey": build_survey_angles,
    }

    if t not in mapping:
        print(f"❌ 不支持的平面类型: {t} (支持: {', '.join(mapping.keys())})", file=sys.stderr)
        sys.exit(1)

    cv = mapping[t]()
    cv.save(out_svg)
    print(f"✅ SVG 已生成: {out_svg}")

    if args.png:
        out_png = render_svg_to_png(out_svg, scale=args.scale)
        print(f"🎨 高清 PNG (300+ DPI) 渲染完成: {out_png}")


def handle_theorem(args):
    out_svg = Path(args.output).resolve()
    try:
        cv = build_theorem_diagram(args.id)
        cv.save(out_svg)
        print(f"✅ 立体几何定理 SVG 已生成: {out_svg}")
        if args.png:
            out_png = render_svg_to_png(out_svg, scale=args.scale)
            print(f"🎨 高清 PNG (300+ DPI) 渲染完成: {out_png}")
    except ValueError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)


def handle_stat(args):
    out_path = Path(args.output).resolve()
    t = args.type.lower()
    if t == "histogram":
        cv = build_histogram()
    elif t == "tree":
        cv = build_tree_diagram()
    else:
        print(f"❌ 不支持的统计类型: {t} (支持: histogram, tree)", file=sys.stderr)
        sys.exit(1)

    if out_path.suffix.lower() == ".png":
        tmp_svg = out_path.with_suffix(".svg")
        cv.save(tmp_svg)
        render_svg_to_png(tmp_svg, png_path=out_path, scale=args.scale)
        print(f"✅ 统计图 PNG 已渲染: {out_path}")
    else:
        cv.save(out_path)
        print(f"✅ 统计图 SVG 已保存: {out_path}")
        if args.png:
            p = render_svg_to_png(out_path, scale=args.scale)
            print(f"🎨 高清 PNG 渲染完成: {p}")


def handle_render(args):
    in_svg = Path(args.input).resolve()
    out_png = Path(args.output).resolve() if args.output else in_svg.with_suffix(".png")
    p = render_svg_to_png(in_svg, png_path=out_png, scale=args.scale)
    print(f"✅ 渲染完成: {p}")


def handle_batch_all(args):
    out_dir = Path(args.dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"🚀 开始在 {out_dir} 批量生成全量 19 张高考题图...")

    # 1. 向量
    build_vector_addition().save(out_dir / "vec_01_addition.svg")
    build_vector_subtraction().save(out_dir / "vec_02_subtraction.svg")
    build_vector_coordinates().save(out_dir / "vec_03_decomp_coord.svg")
    build_vector_dot_product().save(out_dir / "vec_04_dot_product.svg")

    # 2. 三角形
    build_triangle_sine_circumcircle().save(out_dir / "tri_01_sine_circumcircle.svg")
    build_survey_angles().save(out_dir / "tri_02_survey_angles.svg")

    # 3. 定理
    theorems = [
        "geo_01_skew_lines_angle",
        "geo_02_line_plane_parallel_judgement",
        "geo_03_line_plane_parallel_property",
        "geo_04_plane_plane_parallel_judgement",
        "geo_05_line_plane_perp_judgement",
        "geo_06_line_plane_perp_property",
        "geo_07_dihedral_angle",
        "geo_08_plane_plane_perp_judgement",
    ]
    for tid in theorems:
        build_theorem_diagram(tid).save(out_dir / f"{tid}.svg")

    # 4. 立体几何
    build_cube(section=["A", "C", "C1", "A1"], diagonals=[("A", "C", "#dc2626"), ("A1", "C", "#2563eb")]).save(
        out_dir / "solid_01_cube_section.svg"
    )
    build_triangular_prism().save(out_dir / "solid_02_tri_prism.svg")
    build_square_pyramid().save(out_dir / "solid_03_sq_pyramid.svg")

    # 5. 渲染全部 SVG
    rendered = batch_render_directory(out_dir, scale=args.scale)
    print(f"🎨 已批量渲染 {len(rendered)} 张超高清 PNG")

    # 6. 统计图
    build_histogram(output_path=out_dir / "stat_01_histogram.png")
    build_tree_diagram(output_path=out_dir / "prob_01_tree_diagram.png")
    print(f"🏆 19 张标准题图全量闭环输出完毕！")


def main():
    parser = argparse.ArgumentParser(
        prog="math_graphics",
        description="高考数学高考试卷级标准题图自动化生成与渲染 CLI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="子命令")

    # solid
    p_solid = subparsers.add_parser("solid", help="生成立体几何多面体 (正方体/棱柱/棱锥)")
    p_solid.add_argument("--shape", default="cube", choices=["cube", "prism", "pyramid"], help="几何体类型")
    p_solid.add_argument("--size-x", type=float, default=1.5, help="x 尺寸")
    p_solid.add_argument("--size-y", type=float, default=1.8, help="y 尺寸")
    p_solid.add_argument("--size-z", type=float, default=1.8, help="z 高度")
    p_solid.add_argument("--section", default="", help="截面顶点列表，逗号分隔，如 A,C,C1,A1")
    p_solid.add_argument("--title", default="", help="图表说明标题")
    p_solid.add_argument("-o", "--output", required=True, help="输出 SVG 路径")
    p_solid.add_argument("--png", action="store_true", help="自动光栅化为 300+ DPI PNG")
    p_solid.add_argument("--scale", type=float, default=3.0, help="光栅化超采样倍率")

    # plane
    p_plane = subparsers.add_parser("plane", help="生成平面几何/向量/解三角形模型")
    p_plane.add_argument(
        "--type",
        required=True,
        choices=["vector-add", "vector-sub", "vector-coord", "vector-dot", "triangle-sine", "triangle-survey"],
        help="平面图形类型",
    )
    p_plane.add_argument("-o", "--output", required=True, help="输出 SVG 路径")
    p_plane.add_argument("--png", action="store_true", help="自动光栅化为 300+ DPI PNG")
    p_plane.add_argument("--scale", type=float, default=3.0, help="光栅化倍率")

    # theorem
    p_thm = subparsers.add_parser("theorem", help="生成立体几何判定与性质定理图")
    p_thm.add_argument("--id", required=True, help="定理编号 (geo_01 ~ geo_08)")
    p_thm.add_argument("-o", "--output", required=True, help="输出 SVG 路径")
    p_thm.add_argument("--png", action="store_true", help="自动光栅化为 300+ DPI PNG")
    p_thm.add_argument("--scale", type=float, default=3.0, help="光栅化倍率")

    # stat
    p_stat = subparsers.add_parser("stat", help="生成统计直方图与概率树状图")
    p_stat.add_argument("--type", required=True, choices=["histogram", "tree"], help="图表类型")
    p_stat.add_argument("-o", "--output", required=True, help="输出文件路径 (.svg 或 .png)")
    p_stat.add_argument("--png", action="store_true", help="若输出为 SVG 时同时渲染 PNG")
    p_stat.add_argument("--scale", type=float, default=3.0, help="超采样倍率")

    # render
    p_rnd = subparsers.add_parser("render", help="调用系统原生 AppKit 渲染任意 SVG 为高清 PNG")
    p_rnd.add_argument("input", help="输入 SVG 路径")
    p_rnd.add_argument("-o", "--output", help="输出 PNG 路径 (默认同名 .png)")
    p_rnd.add_argument("--scale", type=float, default=3.0, help="超采样倍率 (默认 3.0)")

    # batch-all
    p_all = subparsers.add_parser("batch-all", help="批量生成全套 19 张高考标准题图")
    p_all.add_argument("-d", "--dir", default="./figures", help="目标输出目录")
    p_all.add_argument("--scale", type=float, default=3.0, help="超采样倍率")

    args = parser.parse_args()
    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    if args.subcommand == "solid":
        handle_solid(args)
    elif args.subcommand == "plane":
        handle_plane(args)
    elif args.subcommand == "theorem":
        handle_theorem(args)
    elif args.subcommand == "stat":
        handle_stat(args)
    elif args.subcommand == "render":
        handle_render(args)
    elif args.subcommand == "batch-all":
        handle_batch_all(args)


if __name__ == "__main__":
    main()
