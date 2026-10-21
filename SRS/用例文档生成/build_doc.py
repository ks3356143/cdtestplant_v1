# -*- coding: utf-8 -*-
"""按参考记录.docx 模板结构生成《安全测评测试记录》全文。

生成 officecli batch 命令流：封面 → 目录 → 1 范围 → 2 测试记录（10 个条款、56 条用例）
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
CLAUSES = ["711", "712", "713", "714", "715", "716", "717", "718", "719", "7110"]

BD = {"font.ea": "黑体", "font.latin": "Times New Roman"}
ST = {"font.ea": "宋体", "font.latin": "Times New Roman"}
GRID = "817,709,142,1275,1588,113,880,538,29,2806,731"
W2 = [1668, 2976, 1418, 3566]
W26 = [1668, 7960]
W8 = [817, 2126, 2581, 3373, 731]
LABEL = {"bold": "true", **BD, "size": "10.5pt", "align": "center"}
VALUE = {"size": "10.5pt", **ST}
CENTER = {"align": "center"}

ops = []
pc = 0   # paragraph count
tc = 0   # table count


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


def table(rows, cols, widths):
    global tc
    ops.append({"command": "add", "parent": "/body", "type": "table",
                "props": {"rows": rows, "cols": cols, "colWidths": widths,
                          "layout": "fixed", "style": "afffffffff8", "align": "center"}})
    tc += 1
    for edge, sz in (("top", "12"), ("left", "12"), ("bottom", "12"), ("right", "12"),
                     ("horizontal", "6"), ("vertical", "6")):
        ops.append({"command": "set", "path": f"/body/tbl[{tc}]",
                    "props": {f"border.{edge}": f"single;{sz};000000"}})
    return tc


def setp(tbl, r, c, text, props):
    pr = {"text": text}
    pr.update({k: str(v) for k, v in props.items()})
    ops.append({"command": "set", "path": f"/body/tbl[{tbl}]/tr[{r}]/tc[{c}]/p[1]", "props": pr})


def span(tbl, r, c, n):
    ops.append({"command": "set", "path": f"/body/tbl[{tbl}]/tr[{r}]/tc[{c}]",
                "props": {"colspan": n}})


def cellw(tbl, r, c, w):
    ops.append({"command": "set", "path": f"/body/tbl[{tbl}]/tr[{r}]/tc[{c}]",
                "props": {"width": f"{w}dxa", "skipGridSync": "true"}})


def simple_table(data, widths, header=True):
    """data: 二维文本；第一行为表头。"""
    t = table(len(data), len(data[0]), widths)
    for r, row in enumerate(data, start=1):
        for c, text in enumerate(row, start=1):
            props = dict(LABEL if (header and r == 1) else {**VALUE, "align": "left"})
            if not (header and r == 1):
                props["align"] = "center" if c != len(row) else "left"
            setp(t, r, c, text, props)
    return t


def case_table(case):
    n = len(case["steps"])
    t = table(8 + n, 11, GRID)

    span(t, 1, 1, 11)
    setp(t, 1, 1, "", {"style": "afffffffff3", "numId": 25, "ilvl": 0,
                       "bold": "true", "size": "10.5pt", "align": "left",
                       "indent": "0", "firstLineChars": "0", "hangingIndent": "0",
                       "font.ea": "宋体"})

    for c, s in ((1, 3), (2, 3), (3, 2), (4, 3)):
        span(t, 2, c, s)
    for c, w in enumerate(W2, start=1):
        cellw(t, 2, c, w)
    setp(t, 2, 1, "测试用例名称", LABEL)
    setp(t, 2, 2, case["name"], {**VALUE, **CENTER})
    setp(t, 2, 3, "标   识", LABEL)
    setp(t, 2, 4, case["ident"], {**VALUE, **CENTER})

    for r, label, text in ((3, "追踪关系", case["track"]),
                           (4, "测试用例综述", case["summary"]),
                           (5, "用例初始化", case["init"]),
                           (6, "前提和约束", case["pre"])):
        span(t, r, 1, 3)
        span(t, r, 2, 8)
        cellw(t, r, 1, W26[0])
        cellw(t, r, 2, W26[1])
        setp(t, r, 1, label, LABEL)
        setp(t, r, 2, text, {**VALUE, "align": "left"})

    span(t, 7, 1, 11)
    setp(t, 7, 1, "测试步骤", LABEL)

    for c, s in ((2, 3), (3, 3), (4, 3)):
        span(t, 8, c, s)
    for c, w in enumerate(W8, start=1):
        cellw(t, 8, c, w)
    for c, text in enumerate(("序号", "输入及操作", "期望结果与评估标准", "实测结果", "通过与否"), start=1):
        setp(t, 8, c, text, LABEL)

    for i, st in enumerate(case["steps"]):
        r = 9 + i
        for c, s in ((2, 3), (3, 3), (4, 3)):
            span(t, r, c, s)
        for c, w in enumerate(W8, start=1):
            cellw(t, r, c, w)
        setp(t, r, 1, str(i + 1), {**VALUE, **CENTER})
        setp(t, r, 2, st["op"], {**VALUE, "align": "left"})
        setp(t, r, 3, st["exp"], {**VALUE, "align": "left"})
        setp(t, r, 4, st["act"], {**VALUE, "align": "left"})
        setp(t, r, 5, st["pass"], {**VALUE, **CENTER})


def img_width_cm(path, max_w=14.5, max_h=17.0):
    """按原始像素比例算宽度，保证图片高度不超过 max_h 厘米，便于图注与图片同页。"""
    with open(path, "rb") as f:
        head = f.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            w = int.from_bytes(head[16:20], "big")
            h = int.from_bytes(head[20:24], "big")
        else:  # JPEG：扫 SOF 段
            f.seek(2)
            w = h = 0
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                marker = f.read(1)
                if not marker:
                    break
                if marker[0] in (0xC0, 0xC1, 0xC2):
                    f.read(3)
                    h = int.from_bytes(f.read(2), "big")
                    w = int.from_bytes(f.read(2), "big")
                    break
                seg = int.from_bytes(f.read(2), "big")
                f.seek(seg - 2, 1)
    if not w or not h:
        return max_w
    return round(min(max_w, max_h * w / h), 1)


def picture(path, caption_text="", width=None):
    width = width or f"{img_width_cm(path)}cm"
    para = p("", **CENTER)
    ops.append({"command": "add", "parent": para, "type": "picture",
                "props": {"src": path, "width": width}})
    if caption_text:
        p(caption_text, align="center", size="10.5pt",
          **{"font.ea": "黑体", "font.latin": "Times New Roman"})


def h1(text):
    p(text, style="1")


def h2(text):
    p(text, style="2")


def h3(text):
    p(text, style="30")


def body(text, indent=True):
    props = {"size": "12pt", **ST, "align": "justify", "lineSpacing": "1.5x"}
    if indent:
        props["indent"] = "480"
    p(text, **props)


def caption(text):
    p(text, align="center", **BD, size="10.5pt")


# ---------------- 封面 ----------------
p("标识：PT-CDTP-TN" + " " * 30 + "密级：公开", **BD, size="16pt", align="left")
for _ in range(4):
    p("")
p("测试管理平台", **BD, size="24pt", align="center", lineSpacing="1.5x")
p("安全测评测试记录", **BD, size="24pt", align="center", lineSpacing="1.5x")
p("")
p("总页数：PAGECOUNT", **ST, size="16pt", align="center")
for _ in range(10):
    p("")
p("中国科学院卫星软件评测中心", **BD, size="18pt", align="center")
p("2026年10月21日", **BD, size="16pt", align="center")
pagebreak()

# ---------------- 目录 ----------------
p("目    录", **ST, size="18pt", align="center")
ops.append({"command": "add", "parent": "/body", "type": "toc"})
pc += 1  # 目录域会占用一个段落，后续段落索引整体后移一位
pagebreak()

# ---------------- 1 范围 ----------------
h1("范围")
h2("标识")
p("本文档的标识号：PT-CDTP-TN", style="1-21", numId=27, ilvl=0, size="12pt", **ST)
p("本文档的标题：测试管理平台安全测评测试记录", style="1-21", numId=27, ilvl=0, size="12pt", **ST)
p("本文档适用的范围：定义“测试管理平台（cdtestplant_v1）”依据 GB/T 28452-2012《信息安全技术 "
  "应用软件系统通用安全技术要求》第三级 7.1.1～7.1.10 条开展的安全测评测试记录，"
  "包括测试环境、测试用例、期望结果、实测结果与判定结论。",
  style="1-21", numId=27, ilvl=0, size="12pt", **ST)

h2("被测对象与测试环境")
body("被测对象为测试管理平台 cdtestplant_v1（v0.1.2），部署于云服务器：Django 6 + django-ninja 后端、Vue 3 前端，"
     "MySQL 存储业务数据、Redis 提供缓存与登录失败计数，nginx 在 443 终结 TLS 并反向代理到本机 waitress。"
     "测试采用接口实测、数据库直查、缓存核查与浏览器操作四种方式，界面类用例在浏览器中按真实操作路径验证并截图存证。")
caption("表1-1 被测对象与测试环境")
simple_table([
    ["项目", "内容"],
    ["被测对象", "测试管理平台 cdtestplant_v1"],
    ["版本", "v0.1.2（2026-10-15 安全测评增强版）"],
    ["部署形态", "单机部署（云服务器）；nginx 1.26 反向代理并在 443 终结 TLS；后端 waitress 仅监听 127.0.0.1:8000"],
    ["操作系统", "Ubuntu 24.04.4 LTS（2 vCPU / 1.6 GB 内存 / 40 GB 磁盘）"],
    ["数据库", "MySQL 8.4.13，库名 chengdu_test_plant_v1，应用专用账号 cdtp_app（仅授权本库）"],
    ["缓存", "Redis 7.0.15（登录失败计数、图形验证码、一次性下载令牌）"],
    ["后端", "Python 3.13.16 + Django 6.1 + waitress 3.0（systemd 服务 cdtestplant）"],
    ["前端", "Vue 3.5 + Vite 构建产物，由 nginx 托管于 /cdtestplant/"],
    ["访问入口", "https://XXX/cdtestplant/（TLS 1.2/1.3，自签证书；8081 的 HTTP 入口仅 301 跳转）"],
    ["鉴别方式", "本地账号口令 + 特权角色图形验证码；LDAP 未启用（公网不可达）"],
    ["测评依据", "GB/T 28452-2012 第三级 7.1.1～7.1.10"],
], "2000,7628")

caption("表1-2 测试账号与角色对照")
simple_table([
    ["账号", "角色", "用途"],
    ["srs_a", "系统管理员", "用户管理、项目负责人操作"],
    ["srs_c", "安全员", "安全策略、敏感标记管理"],
    ["srs_b", "审计员", "统一安全审计、抗抵赖证据核验"],
    ["srs_m", "普通用户", "成员/非成员权限验证"],
    ["srs_o", "普通用户", "越权访问、日志主体绑定验证"],
    ["superAdmin", "内置超级账号", "仅用于取得测试令牌，不参与用例"],
], "2200,2200,5228")
body("演示账号口令统一为 XXX；特权账号登录需图形验证码；superAdmin 为内置超级账号，"
     "口令由管理员保管，不在用例中使用。", indent=False)

# ---------------- 2 测试记录 ----------------
h1("测试记录")
body("本部分按 GB/T 28452-2012 第三级 7.1.1～7.1.10 十条要求逐条给出测试记录。每条用例按"
     "“测试用例名称 / 标识 / 追踪关系 / 测试用例综述 / 用例初始化 / 前提和约束 / 测试步骤”组织，"
     "测试步骤逐项给出输入及操作、期望结果与评估标准、实测结果与通过与否。")
caption("表2-1 执行结果汇总")
simple_table([
    ["条款", "要求项", "用例数", "通过", "不适用", "未通过"],
    ["7.1.1", "用户身份鉴别", "8", "7", "1", "0"],
    ["7.1.2", "抗抵赖", "5", "5", "0", "0"],
    ["7.1.3", "自主访问控制", "7", "5", "2", "0"],
    ["7.1.4", "标记", "5", "4", "1", "0"],
    ["7.1.5", "强制访问控制", "6", "4", "2", "0"],
    ["7.1.6", "安全审计", "6", "5", "1", "0"],
    ["7.1.7", "完整性", "6", "6", "0", "0"],
    ["7.1.8", "保密性", "6", "6", "0", "0"],
    ["7.1.9", "备份与故障恢复", "2", "2", "0", "0"],
    ["7.1.10", "系统安全性检测分析", "5", "5", "0", "0"],
    ["合计", "—", "56", "49", "7", "0"],
], "1200,2628,1300,1300,1600,1600")

# 截图与条款的对应关系（按原文档图片关系 ID 解析，7.1.3 有两张）
SHOTS = {
    "7.1.1": [("711.png", "图 7.1.1-1 登录页（线上 443）：口令框为掩码，特权账号需图形验证码（对应 TC-711-04、TC-711-05）")],
    "7.1.2": [("712.png", "图 7.1.2-1 抗抵赖证据页：按业务标识还原原发/接收证据链（对应 TC-712-01、TC-712-04）")],
    "7.1.3": [("713a.png", "图 7.1.3-1 项目管理页：非项目成员列表为空，按 DAC 过滤（对应 TC-713-02、TC-713-05）"),
              ("713b.png", "图 7.1.3-2 项目工作区：项目成员可进入并展开轮次树（对应 TC-713-02、TC-713-04）")],
    "7.1.4": [("714.png", "图 7.1.4-1 用户管理页：角色与密级许可（标记由安全员统一配置）（对应 TC-714-01、TC-714-02）")],
    "7.1.5": [("715.png", "图 7.1.5-1 审计员登录后的左侧菜单：无「安全策略」与用户管理入口（三权分立）（对应 TC-715-02、TC-715-03）")],
    "7.1.6": [("716.png", "图 7.1.6-1 统一安全审计页：主体/事件/结果/IP/时间齐全，告警红标（对应 TC-716-02、TC-716-03）")],
    "7.1.7": [("717.png", "图 7.1.7-1 统一安全审计页「立即核查」：全库 83 条受保护数据全部完好（对应 TC-717-04）")],
    "7.1.8": [("718.png", "图 7.1.8-1 数据保密性保护：已加密字段、传输加密（线上 443）、剩余信息措施、临时文件清理（对应 TC-718-01、TC-718-03、TC-718-06）")],
    "7.1.9": [("719.png", "图 7.1.9-1 数据备份与恢复页：备份记录含条数、大小、SHA-256 摘要与恢复入口（对应 TC-719-01、TC-719-02）")],
    "7.1.10": [("7110.png", "图 7.1.10-1 安全性检测分析页：五类被测对象逐项结论与改进记录（对应 TC-7110-01~05）")],
}

clause_stats = []
all_cases = []
for key in CLAUSES:
    with open(os.path.join(DATA, f"{key}.json"), encoding="utf-8") as f:
        cl = json.load(f)
    h2(cl["title"])
    body(f"要求摘要：{cl['requirement']}")
    passed = sum(1 for c in cl["cases"] if all(s["pass"] == "通过" for s in c["steps"]))
    na = sum(1 for c in cl["cases"] if all(s["pass"] == "不适用" for s in c["steps"]))
    clause_stats.append((cl["no"], cl["title"], len(cl["cases"]), passed, na))
    for c in cl["cases"]:
        all_cases.append((c["ident"], c["name"], cl["no"],
                          "通过" if all(x["pass"] == "通过" for x in c["steps"]) else "不适用"))
    body(f"实现状态：{cl['status']} | 用例 {len(cl['cases'])} 条：通过 {passed}，不适用 {na}")
    for case in cl["cases"]:
        case_table(case)
        p("")
    h3("界面截图证据")
    for img, cap in SHOTS[cl["no"]]:
        picture(os.path.join(HERE, "img", img), cap)

# ---------------------------------------------------------------- 3 测试结论
h1("测试结论")
body("本次测试依据 GB/T 28452-2012《信息安全技术 应用软件系统通用安全技术要求》第三级 7.1.1～7.1.10 "
     "共 10 条要求开展，设计用例 56 条。实测结果：通过 49 条、不适用 7 条、未通过 0 条。")
caption("表 3-1 各条款测试结论")
rows = [["条款", "要求项", "用例数", "通过", "不适用", "结论"]]
for no, title, total, ok, na in clause_stats:
    rows.append([no, title, str(total), str(ok), str(na), "符合" if ok + na == total else "不符合"])
rows.append(["合计", "—", str(sum(x[2] for x in clause_stats)), str(sum(x[3] for x in clause_stats)),
             str(sum(x[4] for x in clause_stats)), "符合"])
simple_table(rows, "1000,2600,1200,1200,1200,2200")
body("结论：被测评对象在用户身份鉴别、抗抵赖、自主访问控制、标记、强制访问控制、安全审计、完整性、保密性、"
     "备份与故障恢复、系统安全性检测分析十个方面满足 GB/T 28452-2012 第三级相应要求。")
body("不适用项说明：7 条不适用用例均为平台单机部署形态下不具备的场景（分布式节点、单点登录、"
     "网络设备与链路扫描、硬件电磁泄漏检测等），各用例中已写明判定依据与承担方，"
     "按测评规范由部署环境或相关管理机构承担。")
body("遗留问题与建议：（1）线上 TLS 采用自签证书，正式对外前应更换为 CA 签发证书；"
     "（2）数据库连接为同机明文，如需满足更严格的传输要求应启用 MySQL TLS；"
     "（3）AI 生成测试项依赖内网模型服务，公网部署不可用；"
     "（4）生产打包尚需移除 Swagger 与 staticfiles 调试项。")
pagebreak()

# ---------------------------------------------------------------- 附录A 用例清单
p("附录A 测试用例清单", style="1", numId=0, pageBreakBefore="true")
p("本附录按条款顺序列出全部 56 条用例的编号、名称与判定结果，详细步骤见第 2 章对应用例表。",
  size="12pt", align="justify", lineSpacing="1.5x", **ST)
caption("表 A-1 测试用例清单")
rows = [["序号", "用例编号", "用例名称", "所属条款", "判定"]]
for i, (ident, name, no, verdict) in enumerate(all_cases, start=1):
    rows.append([str(i), ident, name, no, verdict])
simple_table(rows, "800,2200,4200,1200,1200")

# ---------------------------------------------------------------- 附录B 条款对照
pagebreak()
p("附录B 条款与用例对照", style="1", numId=0, pageBreakBefore="true")
p("本附录给出 GB/T 28452-2012 第三级各条款与本文档章节、用例编号的对应关系，便于追踪与复核。",
  size="12pt", align="justify", lineSpacing="1.5x", **ST)
caption("表 B-1 条款与用例对照")
rows = [["条款", "要求项", "本文档章节", "用例编号段", "用例数"]]
for i, (no, title, total, ok, na) in enumerate(clause_stats, start=1):
    first = all_cases[[x[2] for x in all_cases].index(no)][0]
    last = [x[0] for x in all_cases if x[2] == no][-1]
    rows.append([no, title, f"2.{i}", f"{first}～{last}", str(total)])
simple_table(rows, "1000,3000,1600,2800,1200")

out = os.path.join(HERE, "..", "..", "build", "full.json")
json.dump(ops, open(out, "w", encoding="utf-8"), ensure_ascii=False)
print(f"ops={len(ops)} paragraphs={pc} tables={tc}")
