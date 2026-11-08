#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
math_graphics.mcp_server
高考数学矢量题图生成与高清渲染引擎 MCP 服务端 (Model Context Protocol)
遵循 MCP 规范 (JSON-RPC 2.0 over stdio)，支持 Antigravity / Claude Code / Cursor 等 Agent 体系即插即用。
纯标准库零外部网络依赖实现。
"""

import json
import sys
import os
import traceback
from pathlib import Path
from typing import Dict, Any, List

# 导入核心与模型
from .core.canvas import SVGCanvas
from .core.projection import StereoEngine
from .core.renderer import render_svg_to_png
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

SERVER_NAME = "math-graphics-mcp"
SERVER_VERSION = "1.0.0"

DEFAULT_OUTPUT_DIR = Path("/Volumes/ZHUOLIN/Project/INBOX/math_graphics")

TOOLS = [
    {
        "name": "render_solid_geometry",
        "description": "生成高考试卷级立体几何标准 3D 图 (正方体/棱柱/棱锥)，支持指定截面、尺寸与标题，并可一键渲染 300+ DPI PNG。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "shape": {
                    "type": "string",
                    "enum": ["cube", "prism", "pyramid"],
                    "description": "几何体形状：cube (正方体/长方体), prism (直三棱柱), pyramid (正四棱锥)",
                },
                "section": {
                    "type": "string",
                    "description": "可选截面顶点序列 (逗号分隔)，如 'A,C,C1,A1' 或 'A1,B,D'",
                },
                "size_x": {"type": "number", "default": 1.5, "description": "x 轴尺度"},
                "size_y": {"type": "number", "default": 1.8, "description": "y 轴尺度"},
                "size_z": {"type": "number", "default": 1.8, "description": "z 轴高度"},
                "title": {"type": "string", "description": "图形底部标题或说明"},
                "output_svg": {"type": "string", "description": "输出 SVG 文件完整路径或文件名"},
                "render_png": {"type": "boolean", "default": True, "description": "是否同时渲染 300+ DPI 印刷级 PNG"},
            },
            "required": ["shape"],
        },
    },
    {
        "name": "render_plane_geometry",
        "description": "生成高考平面向量与解三角形题图 (加法/减法/正交分解/数量积/正弦定理外接圆/仰角俯角测高)。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": [
                        "vector-add",
                        "vector-sub",
                        "vector-coord",
                        "vector-dot",
                        "triangle-sine",
                        "triangle-survey",
                    ],
                    "description": "平面题图类型",
                },
                "output_svg": {"type": "string", "description": "输出 SVG 文件路径"},
                "render_png": {"type": "boolean", "default": True, "description": "是否同时渲染 300+ DPI PNG"},
            },
            "required": ["type"],
        },
    },
    {
        "name": "render_theorem_diagram",
        "description": "生成高考立体几何核心判定与性质定理图 (geo_01 ~ geo_08)。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "theorem_id": {
                    "type": "string",
                    "enum": [
                        "geo_01_skew_lines_angle",
                        "geo_02_line_plane_parallel_judgement",
                        "geo_03_line_plane_parallel_property",
                        "geo_04_plane_plane_parallel_judgement",
                        "geo_05_line_plane_perp_judgement",
                        "geo_06_line_plane_perp_property",
                        "geo_07_dihedral_angle",
                        "geo_08_plane_plane_perp_judgement",
                    ],
                    "description": "定理标准 ID",
                },
                "output_svg": {"type": "string", "description": "输出 SVG 路径"},
                "render_png": {"type": "boolean", "default": True, "description": "是否同时渲染 300+ DPI PNG"},
            },
            "required": ["theorem_id"],
        },
    },
    {
        "name": "render_custom_polyhedron",
        "description": "自定义 3D 多面体绘图工具：供 Agent 根据题目参数传入任意 3D 顶点、边（实虚线）与表面/截面定义，自动基于斜二测投影渲染高清试卷图。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "vertices": {
                    "type": "object",
                    "description": "顶点字典，例如 {'A': [1.5, 0, 0], 'B': [1.5, 1.8, 0], 'P': [0.8, 0.9, 2.0]}",
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "dashed": {"type": "boolean", "default": False},
                            "stroke": {"type": "string", "default": "#000000"},
                            "width": {"type": "number", "default": 1.6},
                        },
                        "required": ["from", "to"],
                    },
                    "description": "边线列表（可设置 dashed 为 true 绘制隐藏虚线）",
                },
                "faces": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "vertices": {"type": "array", "items": {"type": "string"}},
                            "fill": {"type": "string", "default": "rgba(240, 240, 240, 0.4)"},
                        },
                        "required": ["vertices"],
                    },
                    "description": "截面或多边形表面列表",
                },
                "title": {"type": "string", "description": "图表说明"},
                "output_svg": {"type": "string", "description": "输出 SVG 路径"},
                "render_png": {"type": "boolean", "default": True, "description": "是否渲染 300+ DPI PNG"},
            },
            "required": ["vertices", "edges"],
        },
    },
    {
        "name": "render_histogram",
        "description": "生成高考频率分布直方图 (支持标注众数顶峰、中位数面积二等分虚线)。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "bins": {"type": "array", "items": {"type": "number"}, "description": "区间端点列表，如 [50, 60, 70, 80, 90, 100]"},
                "heights": {"type": "array", "items": {"type": "number"}, "description": "各组频率/组距列表"},
                "median": {"type": "number", "description": "中位数横坐标标注"},
                "mode": {"type": "number", "description": "众数横坐标标注"},
                "output_png": {"type": "string", "description": "输出 PNG 路径"},
            },
        },
    },
    {
        "name": "render_svg_to_png",
        "description": "将任意指定 SVG 文件通过 macOS 原生 AppKit 渲染为 300+ DPI 印刷级 PNG。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "svg_path": {"type": "string", "description": "输入 SVG 完整路径"},
                "png_path": {"type": "string", "description": "可选输出 PNG 路径"},
                "scale": {"type": "number", "default": 3.0, "description": "超采样比例 (默认 3.0)"},
            },
            "required": ["svg_path"],
        },
    },
]


def resolve_path(p: str, default_name: str, ext: str) -> Path:
    if not p:
        return DEFAULT_OUTPUT_DIR / f"{default_name}.{ext}"
    path = Path(p)
    if not path.is_absolute():
        path = DEFAULT_OUTPUT_DIR / path
    return path


def execute_tool(name: str, args: Dict[str, Any]) -> str:
    if name == "render_solid_geometry":
        shape = args["shape"].lower()
        title = args.get("title", "")
        sec_str = args.get("section", "")
        section = [s.strip() for s in sec_str.split(",") if s.strip()] if sec_str else None
        sx = args.get("size_x", 1.5)
        sy = args.get("size_y", 1.8)
        sz = args.get("size_z", 1.8)

        if shape == "cube":
            cv = build_cube(a=sx, b=sy, c=sz, section=section, title=title or "正方体/长方体模型")
        elif shape in ["prism", "tri-prism"]:
            cv = build_triangular_prism(a=sx, b=sy, h=sz, title=title or "直三棱柱模型")
        elif shape in ["pyramid", "sq-pyramid"]:
            cv = build_square_pyramid(base_x=sx, base_y=sy, h=sz, title=title or "正四棱锥模型")
        else:
            raise ValueError(f"未知几何体: {shape}")

        out_svg = resolve_path(args.get("output_svg"), f"solid_{shape}", "svg")
        cv.save(out_svg)
        res = f"SVG 矢量图已生成: {out_svg}\n"

        if args.get("render_png", True):
            out_png = render_svg_to_png(out_svg)
            res += f"300+ DPI 高清 PNG 渲染完成: {out_png}\n"
        return res

    elif name == "render_plane_geometry":
        t = args["type"].lower()
        mapping = {
            "vector-add": build_vector_addition,
            "vector-sub": build_vector_subtraction,
            "vector-coord": build_vector_coordinates,
            "vector-dot": build_vector_dot_product,
            "triangle-sine": build_triangle_sine_circumcircle,
            "triangle-survey": build_survey_angles,
        }
        if t not in mapping:
            raise ValueError(f"未知的平面图形类型: {t}")
        cv = mapping[t]()
        out_svg = resolve_path(args.get("output_svg"), f"plane_{t}", "svg")
        cv.save(out_svg)
        res = f"SVG 矢量图已生成: {out_svg}\n"
        if args.get("render_png", True):
            out_png = render_svg_to_png(out_svg)
            res += f"300+ DPI 高清 PNG 渲染完成: {out_png}\n"
        return res

    elif name == "render_theorem_diagram":
        tid = args["theorem_id"]
        cv = build_theorem_diagram(tid)
        out_svg = resolve_path(args.get("output_svg"), tid, "svg")
        cv.save(out_svg)
        res = f"立体几何定理 SVG 已生成: {out_svg}\n"
        if args.get("render_png", True):
            out_png = render_svg_to_png(out_svg)
            res += f"300+ DPI 高清 PNG 渲染完成: {out_png}\n"
        return res

    elif name == "render_custom_polyhedron":
        vertices = {k: tuple(v) for k, v in args["vertices"].items()}
        edges = args["edges"]
        faces = args.get("faces")
        title = args.get("title", "")
        cv = build_custom_polyhedron(vertices=vertices, edges=edges, faces=faces, title=title)
        out_svg = resolve_path(args.get("output_svg"), "custom_polyhedron", "svg")
        cv.save(out_svg)
        res = f"自定义多面体 SVG 已生成: {out_svg}\n"
        if args.get("render_png", True):
            out_png = render_svg_to_png(out_svg)
            res += f"300+ DPI 高清 PNG 渲染完成: {out_png}\n"
        return res

    elif name == "render_histogram":
        bins = args.get("bins")
        heights = args.get("heights")
        median = args.get("median", 78.57)
        mode = args.get("mode", 75.0)
        out_svg = resolve_path(args.get("output_svg"), "histogram", "svg")
        cv = build_histogram(bins=bins, heights=heights, median=median, mode=mode)
        cv.save(out_svg)
        res = f"频率分布直方图 SVG 已生成: {out_svg}\n"
        if args.get("render_png", True):
            out_png = render_svg_to_png(out_svg)
            res += f"300+ DPI 高清 PNG 渲染完成: {out_png}\n"
        return res

    elif name == "render_svg_to_png":
        svg_p = args["svg_path"]
        png_p = args.get("png_path")
        scale = args.get("scale", 3.0)
        p = render_svg_to_png(svg_p, png_path=png_p, scale=scale)
        return f"SVG -> PNG 渲染成功: {p}\n"

    else:
        raise ValueError(f"未知的工具名称: {name}")


def run_mcp_server():
    """主事件循环 (JSON-RPC 2.0 over stdin/stdout)"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                    "capabilities": {"tools": {}},
                },
            }
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            # 客户端通知，无需回复
            pass

        elif method == "ping":
            resp = {"jsonrpc": "2.0", "id": req_id, "result": {}}
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        elif method == "tools/list":
            resp = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS},
            }
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result_text = execute_tool(tool_name, tool_args)
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": result_text}],
                        "isError": False,
                    },
                }
            except Exception as e:
                err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [{"type": "text", "text": f"执行错误: {err_msg}"}],
                        "isError": True,
                    },
                }
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()

        else:
            if req_id is not None:
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
                sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    run_mcp_server()
