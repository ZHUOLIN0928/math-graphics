# -*- coding: utf-8 -*-
"""
math_graphics.core.renderer
原生超高清 300+ DPI 矢量光栅化渲染引擎
在 macOS 上直接调用系统原生 AppKit (NSImage / NSBitmapImageRep)，
零外部三方依赖（无需安装 librsvg、cairo 或 Inkscape）。
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, Union, List


def render_svg_to_png(
    svg_path: Union[str, Path],
    png_path: Optional[Union[str, Path]] = None,
    scale: float = 3.0,
) -> Path:
    """
    调用 macOS Swift/AppKit 将单个 SVG 渲染为 300+ DPI 超高清 PNG
    :param svg_path: 输入 SVG 路径
    :param png_path: 输出 PNG 路径，默认同名 .png
    :param scale: 超采样倍率（3.0 对应 300+ DPI 试卷印刷级标准）
    :return: 渲染后的 PNG 路径
    """
    svg_p = Path(svg_path).resolve()
    if not svg_p.exists():
        raise FileNotFoundError(f"SVG 文件不存在: {svg_p}")

    if png_path is None:
        png_p = svg_p.with_suffix(".png")
    else:
        png_p = Path(png_path).resolve()
    png_p.parent.mkdir(parents=True, exist_ok=True)

    swift_script = f'''
import AppKit
import Foundation

let svgUrl = URL(fileURLWithPath: "{svg_p}")
let pngUrl = URL(fileURLWithPath: "{png_p}")

guard let svgData = try? Data(contentsOf: svgUrl),
      let image = NSImage(data: svgData) else {{
    fputs("Error loading SVG data\\n", stderr)
    exit(1)
}}

let scale: CGFloat = {scale}
let w = Int(image.size.width * scale)
let h = Int(image.size.height * scale)

guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: w,
    pixelsHigh: h,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .calibratedRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
) else {{
    fputs("Error creating NSBitmapImageRep\\n", stderr)
    exit(2)
}}

NSGraphicsContext.saveGraphicsState()
let ctx = NSGraphicsContext(bitmapImageRep: rep)
NSGraphicsContext.current = ctx

NSColor.white.setFill()
NSRect(x: 0, y: 0, width: w, height: h).fill()
image.draw(in: NSRect(x: 0, y: 0, width: w, height: h))
NSGraphicsContext.restoreGraphicsState()

guard let pngData = rep.representation(using: .png, properties: [:]) else {{
    fputs("Error generating PNG data\\n", stderr)
    exit(3)
}}

do {{
    try pngData.write(to: pngUrl)
}} catch {{
    fputs("Error writing PNG file\\n", stderr)
    exit(4)
}}
'''
    res = subprocess.run(["swift", "-e", swift_script], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Swift 渲染 PNG 失败: {res.stderr.strip() or res.stdout.strip()}")

    return png_p


def batch_render_directory(
    directory: Union[str, Path],
    scale: float = 3.0,
) -> List[Path]:
    """批量渲染目录下的所有 .svg 文件为高清 .png"""
    dir_p = Path(directory).resolve()
    rendered = []
    for svg_file in sorted(dir_p.glob("*.svg")):
        out_png = render_svg_to_png(svg_file, scale=scale)
        rendered.append(out_png)
    return rendered
