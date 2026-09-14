#!/usr/bin/env python3
"""Render the financial research Agent workflow as a polished one-page PDF."""

from __future__ import annotations

import argparse
from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas


PAGE_W, PAGE_H = 1680, 950


def color(value: str):
    from reportlab.lib.colors import HexColor
    return HexColor(value)


INK = color("#172033")
MUTED = color("#687386")
LINE = color("#AAB4C5")
PURPLE = color("#6750E6")
PURPLE_SOFT = color("#F0EEFF")
ORANGE = color("#E87924")
ORANGE_SOFT = color("#FFF3E8")
GREEN = color("#168A62")
GREEN_SOFT = color("#EAF8F2")
RED = color("#C74747")
RED_SOFT = color("#FDEEEE")
BLUE_SOFT = color("#EDF5FF")
PAPER = color("#F7F8FC")
WHITE = color("#FFFFFF")


def arrow(c: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, *, stroke=LINE, width=2.2) -> None:
    c.setStrokeColor(stroke)
    c.setFillColor(stroke)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)
    size = 8
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        c.line(x2, y2, x2 - direction * size, y2 + size * 0.55)
        c.line(x2, y2, x2 - direction * size, y2 - size * 0.55)
    else:
        direction = 1 if y2 >= y1 else -1
        c.line(x2, y2, x2 + size * 0.55, y2 - direction * size)
        c.line(x2, y2, x2 - size * 0.55, y2 - direction * size)


def node(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    number: str,
    title: str,
    english: str,
    io_text: str,
    fill=PURPLE_SOFT,
    stroke=PURPLE,
) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(color("#DDE2EB"))
    c.setLineWidth(1)
    c.roundRect(x + 4, y - 5, w, h, 16, fill=1, stroke=0)
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(2)
    c.roundRect(x, y, w, h, 16, fill=1, stroke=1)
    c.setFillColor(stroke)
    c.circle(x + 23, y + h - 23, 13, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x + 23, y + h - 27, number)
    c.setFillColor(INK)
    c.setFont("STSong-Light", 16)
    c.drawString(x + 16, y + h - 57, title)
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 16, y + h - 77, english.upper())
    c.setStrokeColor(color("#D9DEEA"))
    c.setLineWidth(0.8)
    c.line(x + 16, y + 51, x + w - 16, y + 51)
    c.setFillColor(MUTED)
    c.setFont("STSong-Light", 9.2)
    lines = io_text.split("\n")
    for index, line in enumerate(lines[:2]):
        c.drawString(x + 16, y + 34 - index * 15, line)


def render(path: Path) -> None:
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    c = canvas.Canvas(str(path), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Financial Research Agent Workflow")

    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(PURPLE)
    c.roundRect(46, 872, 62, 8, 4, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 31)
    c.drawString(46, 818, "Financial Research Agent Workflow")
    c.setFillColor(MUTED)
    c.setFont("STSong-Light", 13)
    c.drawString(48, 788, "金融研究 Agent：从研究主题到有证据、可审计的结构化报告")
    c.setFont("Helvetica", 10)
    c.drawRightString(PAGE_W - 48, 815, "DEMO REFERENCE ARCHITECTURE  /  v1.0")

    xs = [45 + index * 200 for index in range(8)]
    y, w, h = 570, 170, 158
    nodes = [
        ("1", "接收研究主题", "Research Topic", "IN  自然语言主题\nOUT  ResearchRequest", BLUE_SOFT, color("#3975B8")),
        ("2", "任务拆解", "Plan", "IN  ResearchRequest\nOUT  PlanSpec / Queries", PURPLE_SOFT, PURPLE),
        ("3", "信息检索", "Retrieve", "IN  Queries / SourcePolicy\nOUT  Evidence Ledger", PURPLE_SOFT, PURPLE),
        ("4", "关键数据提取", "Extract", "IN  Evidence Cards\nOUT  Structured Facts", PURPLE_SOFT, PURPLE),
        ("5", "人工确认", "Human Review", "IN  Facts + Sources\nOUT  Approve / Reject", ORANGE_SOFT, ORANGE),
        ("6", "报告生成", "Report", "IN  Approved Facts\nOUT  Markdown Draft", PURPLE_SOFT, PURPLE),
        ("7", "质量验证", "Verify", "IN  Draft + Evidence\nOUT  Contract Verdict", ORANGE_SOFT, ORANGE),
        ("8", "结构化交付", "Deliver", "IN  Verified Report\nOUT  Markdown + Trace", GREEN_SOFT, GREEN),
    ]
    for index, (number, title, english, io_text, fill, stroke) in enumerate(nodes):
        node(c, xs[index], y, w, h, number=number, title=title, english=english, io_text=io_text, fill=fill, stroke=stroke)
        if index < len(nodes) - 1:
            arrow(c, xs[index] + w + 6, y + h / 2, xs[index + 1] - 7, y + h / 2, stroke=color("#7E89A0"))

    # Failure handling and feedback loops.
    c.setFillColor(RED_SOFT)
    c.setStrokeColor(color("#E4A7A7"))
    c.setLineWidth(1.2)
    c.roundRect(245, 382, 365, 92, 14, fill=1, stroke=1)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(262, 445, "RETRIEVAL / EXTRACTION FAILURE")
    c.setFillColor(INK)
    c.setFont("STSong-Light", 12)
    c.drawString(262, 420, "超时重试 -> 扩展检索式 -> 仍不足则诚实失败")
    c.setFillColor(MUTED)
    c.setFont("STSong-Light", 9.5)
    c.drawString(262, 399, "所有失败、重试次数与错误分类写入 Trace")
    arrow(c, xs[2] + w / 2, y - 2, xs[2] + w / 2, 474, stroke=RED)
    arrow(c, 610, 428, xs[1] + w / 2, 515, stroke=RED)

    c.setFillColor(ORANGE_SOFT)
    c.setStrokeColor(color("#F0B889"))
    c.roundRect(820, 382, 270, 92, 14, fill=1, stroke=1)
    c.setFillColor(ORANGE)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(837, 445, "HUMAN REJECT")
    c.setFillColor(INK)
    c.setFont("STSong-Light", 12)
    c.drawString(837, 420, "携带批注意见返回任务拆解")
    c.setFillColor(MUTED)
    c.setFont("STSong-Light", 9.5)
    c.drawString(837, 399, "保持原证据与版本，不覆盖历史结果")
    arrow(c, xs[4] + w / 2, y - 2, xs[4] + w / 2, 474, stroke=ORANGE)
    arrow(c, 820, 428, xs[1] + w / 2, 515, stroke=ORANGE)

    c.setFillColor(RED_SOFT)
    c.setStrokeColor(color("#E4A7A7"))
    c.roundRect(1240, 382, 350, 92, 14, fill=1, stroke=1)
    c.setFillColor(RED)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(1257, 445, "CONTRACT FAIL")
    c.setFillColor(INK)
    c.setFont("STSong-Light", 12)
    c.drawString(1257, 420, "报告缺陷定向修复；证据缺口动态 Replan")
    c.setFillColor(MUTED)
    c.setFont("STSong-Light", 9.5)
    c.drawString(1257, 399, "预算耗尽或来源不足时输出明确失败原因")
    arrow(c, xs[6] + w / 2, y - 2, xs[6] + w / 2, 474, stroke=RED)
    arrow(c, 1240, 428, xs[5] + w / 2, 515, stroke=RED)

    # Durable platform layer.
    c.setFillColor(WHITE)
    c.setStrokeColor(color("#D9DEEA"))
    c.setLineWidth(1.2)
    c.roundRect(45, 150, PAGE_W - 90, 145, 18, fill=1, stroke=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(68, 261, "DURABLE AGENT HARNESS")
    stores = [
        ("Evidence Ledger", "原文、来源、稳定 evidence_id", PURPLE),
        ("Checkpoint", "阶段状态、预算、恢复位置", color("#3975B8")),
        ("Trace / Events", "输入输出、工具调用、错误", ORANGE),
        ("Context Manager", "压缩卡、章节路由、Map-Reduce", GREEN),
    ]
    store_w = 355
    for index, (title, detail, accent) in enumerate(stores):
        sx = 68 + index * 389
        c.setFillColor(color("#F7F8FC"))
        c.setStrokeColor(color("#E3E7EF"))
        c.roundRect(sx, 174, store_w, 65, 11, fill=1, stroke=1)
        c.setFillColor(accent)
        c.roundRect(sx + 12, 188, 7, 38, 3, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(sx + 31, 213, title)
        c.setFillColor(MUTED)
        c.setFont("STSong-Light", 9.5)
        c.drawString(sx + 31, 192, detail)

    c.setFillColor(MUTED)
    c.setFont("STSong-Light", 9.5)
    c.drawString(48, 77, "质量原则：来源白名单 · 数字就近引用 · 口径显式披露 · 中间结果可查看 · 长任务可恢复")
    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_W - 48, 77, "DeepResearch Agent Harness")
    c.showPage()
    c.save()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    render(args.output)


if __name__ == "__main__":
    main()

