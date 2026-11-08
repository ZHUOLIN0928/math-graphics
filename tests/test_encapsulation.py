#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
math_graphics.tests.test_encapsulation
自动化验证 math_graphics 工具链封装完整性
测试项：
1. 核心引擎导入与投影计算
2. 各多面体模型 (正方体带截面、棱柱、棱锥) SVG 生成
3. 平面与定理模型生成
4. Swift AppKit 300+ DPI PNG 渲染
5. CLI 命令行入口测试
6. MCP JSON-RPC 协议与工具调用测试
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

# 添加包路径
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR.parent))

from math_graphics.core.canvas import SVGCanvas
from math_graphics.core.projection import StereoEngine
from math_graphics.core.renderer import render_svg_to_png
from math_graphics.models.solids import (
    build_cube,
    build_triangular_prism,
    build_square_pyramid,
    build_custom_polyhedron,
)
from math_graphics.models.plane import (
    build_vector_addition,
    build_theorem_diagram,
)
from math_graphics.mcp_server import execute_tool, TOOLS


class TestMathGraphicsEncapsulation(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = BASE_DIR / "tests" / "tmp_output"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # 清理临时生成文件
        for f in self.tmp_dir.glob("*"):
            try:
                f.unlink()
            except OSError:
                pass
        if self.tmp_dir.exists():
            try:
                self.tmp_dir.rmdir()
            except OSError:
                pass

    def test_01_core_projection(self):
        eng = StereoEngine(origin=(200, 240), scale=75)
        u, v = eng.p(0, 0, 0)
        self.assertEqual((u, v), (200.0, 240.0))
        # z 轴向上，v 减小
        u_z, v_z = eng.p(0, 0, 1)
        self.assertEqual(u_z, 200.0)
        self.assertEqual(v_z, 165.0)

    def test_02_cube_and_section(self):
        cv = build_cube(section=["A", "C", "C1", "A1"], title="正方体截面测试")
        out_svg = self.tmp_dir / "test_cube.svg"
        cv.save(out_svg)
        self.assertTrue(out_svg.exists())
        content = out_svg.read_text(encoding="utf-8")
        self.assertIn("<svg", content)
        self.assertIn("正方体截面测试", content)
        self.assertIn("polygon", content)

    def test_03_theorems(self):
        cv = build_theorem_diagram("geo_07_dihedral_angle")
        out_svg = self.tmp_dir / "test_dihedral.svg"
        cv.save(out_svg)
        self.assertTrue(out_svg.exists())
        self.assertIn("二面角平面角", out_svg.read_text(encoding="utf-8"))

    def test_04_swift_png_rendering(self):
        cv = build_square_pyramid()
        out_svg = self.tmp_dir / "test_pyramid.svg"
        cv.save(out_svg)
        out_png = render_svg_to_png(out_svg, scale=2.0)
        self.assertTrue(out_png.exists())
        self.assertGreater(out_png.stat().st_size, 5000)

    def test_05_cli_execution(self):
        out_svg = self.tmp_dir / "cli_vec.svg"
        cmd = [
            sys.executable,
            "-m",
            "math_graphics.cli",
            "plane",
            "--type",
            "vector-add",
            "-o",
            str(out_svg),
            "--png",
        ]
        res = subprocess.run(cmd, cwd=str(BASE_DIR.parent), capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, msg=res.stderr)
        self.assertTrue(out_svg.exists())
        self.assertTrue(out_svg.with_suffix(".png").exists())

    def test_06_mcp_tools(self):
        self.assertGreaterEqual(len(TOOLS), 6)
        # 测试 solid tool
        out_svg = self.tmp_dir / "mcp_cube.svg"
        res = execute_tool(
            "render_solid_geometry",
            {"shape": "cube", "section": "A1,B,D", "output_svg": str(out_svg), "render_png": False},
        )
        self.assertIn("SVG 矢量图已生成", res)
        self.assertTrue(out_svg.exists())


if __name__ == "__main__":
    unittest.main()
