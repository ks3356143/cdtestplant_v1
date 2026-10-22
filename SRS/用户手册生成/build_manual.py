# -*- coding: utf-8 -*-
"""生成《测试管理平台软件需求规格说明》——基于参考模板的 officecli batch 命令流。"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from manual_content import BLOCKS   # noqa: E402

# ---- 表号统一重排：按出现顺序编号（插入新表后仍连续）----
import re as _re


def _renumber(blocks):
    """按出现顺序重排表号/图号（不依赖旧号映射），正文引用按首次出现的旧号对应。"""
    counters, mapping, caption_new = {}, {}, {}
    for i, blk in enumerate(blocks):
        kind = blk[0]
        if kind == "table":
            text, prefix = blk[1], "表"
        elif kind == "img":
            text, prefix = blk[2], "图"
        else:
            continue
        m = _re.match(rf"{prefix} (\d+)-(\d+)", text)
        if not m:
            continue
        chap = m.group(1)
        key = (prefix, chap)
        counters[key] = counters.get(key, 0) + 1
        new_label = f"{prefix} {chap}-{counters[key]}"
        old_label = f"{prefix} {chap}-{m.group(2)}"
        mapping.setdefault(old_label, new_label)
        caption_new[i] = new_label + text[len(old_label):]

    pattern = _re.compile(r"[表图] \d+-\d+")

    def rep(text):
        text = text.replace("　", " ")
        return pattern.sub(lambda mm: mapping.get(mm.group(0), mm.group(0)), text)

    out = []
    for i, blk in enumerate(blocks):
        if blk[0] == "table":
            cap = caption_new.get(i, blk[1]).replace("　", " ")
            out.append((blk[0], cap) + tuple(blk[2:]))
        elif blk[0] == "img":
            cap = caption_new.get(i, blk[2]).replace("　", " ")
            out.append((blk[0], blk[1], cap))
        elif blk[0] in ("p", "pn"):
            out.append((blk[0], rep(blk[1])))
        elif blk[0] == "bullet":
            out.append((blk[0], [rep(x) for x in blk[1]]))
        elif blk[0] in ("h1", "h1n", "h2", "h3", "h4"):
            out.append((blk[0], rep(blk[1])))
        else:
            out.append(blk)
    return out
BLOCKS = _renumber(BLOCKS)
TABLE_W = 9600           # 可用版心宽度（twips）
BD = {"font.ea": "黑体", "font.latin": "Times New Roman"}
ST = {"font.ea": "宋体", "font.latin": "Times New Roman"}

ops = []
pc = 0
tc = 0


def p(text="", **props):
    global pc
    pr = {"text": text}
    pr.update({k: str(v) for k, v in props.items()})
    ops.append({"command": "add", "parent": "/body", "type": "paragraph", "props": pr})
    pc += 1
    return f"/body/p[{pc}]"


def pagebreak():
    path = p("")
    ops.append({"command": "add", "parent": path, "type": "pagebreak"})


def h1(t):
    p(t, style="1")


def h2(t):
    p(t, style="2")


def h3(t):
    p(t, style="30")


def h4(t):
    p(t, style="4")


def body(text):
    p(text, size="12pt", align="justify", lineSpacing="1.5x", indent="480", **ST)


def bullet(items):
    for it in items:
        p("· " + it, size="12pt", align="justify", lineSpacing="1.5x", indent="480", **ST)


def table(caption, header, rows, widths):
    global tc
    w = [int(x) for x in widths.split(",")]
    scale = TABLE_W / sum(w)
    cols = ",".join(str(int(x * scale)) for x in w)
    n_r = len(rows) + 1
    p(caption, align="center", size="10.5pt", spaceBefore="6pt", spaceAfter="3pt", **BD)
    ops.append({"command": "add", "parent": "/body", "type": "table",
                "props": {"rows": n_r, "cols": len(w), "colWidths": cols,
                          "layout": "fixed", "style": "afffffffff8", "align": "center"}})
    tc += 1
    t = tc
    for edge, sz in (("top", "12"), ("left", "12"), ("bottom", "12"), ("right", "12"),
                     ("horizontal", "6"), ("vertical", "6")):
        ops.append({"command": "set", "path": f"/body/tbl[{t}]",
                    "props": {f"border.{edge}": f"single;{sz};000000"}})
    for c, text in enumerate(header, start=1):
        ops.append({"command": "set", "path": f"/body/tbl[{t}]/tr[1]/tc[{c}]/p[1]",
                    "props": {"text": text, "bold": "true", "size": "10.5pt",
                              "align": "center", **BD}})
    for r, row in enumerate(rows, start=2):
        for c, text in enumerate(row, start=1):
            ops.append({"command": "set", "path": f"/body/tbl[{t}]/tr[{r}]/tc[{c}]/p[1]",
                        "props": {"text": text, "size": "10.5pt",
                                  "align": "left" if c == len(row) else "center", **ST}})
    for r in range(1, n_r + 1):
        ops.append({"command": "set", "path": f"/body/tbl[{t}]/tr[{r}]",
                    "props": {"cantSplit": "true"}})
    ops.append({"command": "set", "path": f"/body/tbl[{t}]/tr[1]", "props": {"header": "true"}})
    p("")


# ---------------------------------------------------------------- 封面
p("标识：PT-CDTP-UM" + " " * 30 + "密级：公开", size="16pt", align="left", **BD)
for _ in range(4):
    p("")
p("测试管理平台", size="24pt", align="center", lineSpacing="1.5x", **BD)
p("软件用户手册", size="24pt", align="center", lineSpacing="1.5x", **BD)
p("")
p("总页数：PAGECOUNT", size="16pt", align="center", **ST)
for _ in range(10):
    p("")
p("中国科学院卫星软件评测中心", size="18pt", align="center", **BD)
p("2026年10月21日", size="16pt", align="center", **BD)
pagebreak()

# ---------------------------------------------------------------- 目录
p("目    录", size="18pt", align="center", **ST)
ops.append({"command": "add", "parent": "/body", "type": "toc"})
pc += 1
pagebreak()

# ---------------------------------------------------------------- 正文
for blk in BLOCKS:
    kind = blk[0]
    if kind == "h1":
        h1(blk[1])
    elif kind == "h1n":
        p(blk[1], style="1", numId=0)
    elif kind == "h2":
        h2(blk[1])
    elif kind == "h3":
        h3(blk[1])
    elif kind == "h4":
        h4(blk[1])
    elif kind == "p":
        body(blk[1])
    elif kind == "pn":
        p(blk[1], size="12pt", align="justify", lineSpacing="1.5x", **ST)
    elif kind == "bullet":
        bullet(blk[1])
    elif kind == "table":
        table(blk[1], blk[2], blk[3], blk[4])
    elif kind == "img":
        img_path = os.path.join(HERE, "..", "用例文档生成", "img", blk[1])
        para = p("", align="center")
        ops.append({"command": "add", "parent": para, "type": "picture",
                    "props": {"src": img_path, "width": "15cm"}})
        p(blk[2], align="center", size="10.5pt", **{"font.ea": "黑体", "font.latin": "Times New Roman"})
    else:
        raise ValueError(f"未知块类型：{kind}")

ops.append({"command": "set", "path": "/settings", "props": {"updateFields": "true"}})

out = os.path.join(HERE, "..", "..", "build", "manual.json")
json.dump(ops, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(f"ops={len(ops)} paragraphs={pc} tables={tc}")
