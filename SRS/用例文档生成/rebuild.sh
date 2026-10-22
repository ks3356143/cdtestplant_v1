#!/usr/bin/env bash
# 从模板重建《安全测评测试记录》：清空模板正文 → 填内容 → 排版收尾 → 回填总页数
set -e
cd "$(dirname "$0")/../.."
F="build/工作副本.docx"

officecli close "$F" >/dev/null 2>&1 || true
sleep 1
rm -f "$F"
cp "SRS/参考/参考记录.docx" "$F"
officecli batch "$F" --input SRS/用例文档生成/strip.json >/dev/null
officecli set "$F" "/header[44]/p[1]" --prop text="测试管理平台安全测评测试记录" >/dev/null

python SRS/用例文档生成/build_doc.py
officecli batch "$F" --input build/full.json | tail -1

python - <<'PY'
import json, subprocess
F = "build/工作副本.docx"
def run(*a):
    return subprocess.run(["officecli", *a], capture_output=True, text=True, encoding="utf-8").stdout

# 行不跨页 + 用例表表头重复 + 封面标识行
tables = json.loads(run("query", F, "table", "--json"))["data"]["results"]
ops = [{"command": "set", "path": "/body/p[1]", "props": {
    "text": "标识：PT-CDTP-TN" + " " * 30 + "密级：公开",
    "font.ea": "黑体", "size": "16pt", "align": "left"}}]
for i, t in enumerate(tables, start=1):
    for r in range(1, int(t["format"]["rows"]) + 1):
        ops.append({"command": "set", "path": f"/body/tbl[{i}]/tr[{r}]", "props": {"cantSplit": "true"}})
    if i >= 4:
        ops.append({"command": "set", "path": f"/body/tbl[{i}]/tr[8]", "props": {"header": "true"}})
ops.append({"command": "set", "path": "/settings", "props": {"updateFields": "true"}})
json.dump(ops, open("build/polish.json", "w", encoding="utf-8"), ensure_ascii=False)

h3 = json.loads(run("query", F, 'p:contains("界面截图证据")', "--json"))["data"]["results"]
json.dump([{"command": "set", "path": r["path"], "props": {"align": "left"}}
           for r in h3 if r["type"] == "paragraph"],
          open("build/fix_h3.json", "w", encoding="utf-8"), ensure_ascii=False)
print("polish ops:", len(ops))
PY

officecli batch "$F" --input build/polish.json | tail -1
officecli batch "$F" --input build/fix_h3.json | tail -1

PAGES=$(officecli view "$F" stats --page-count 2>/dev/null | grep -i "^Pages:" | grep -oE "[0-9]+")
echo "页数：$PAGES"
P=$(officecli query "$F" 'p:contains("总页数")' --json 2>/dev/null |
    python -c "import sys,json;print([r['path'] for r in json.load(sys.stdin)['data']['results'] if r['type']=='paragraph'][0])")
officecli set "$F" "$P" --prop text="总页数：$PAGES" --prop align=center --prop size=16pt --prop font.ea=宋体 >/dev/null
officecli save "$F" >/dev/null
officecli close "$F" >/dev/null 2>&1 || true
python SRS/tools/clean_docx_parts.py "$F"
# 清理后再量一次页数：残留页眉页脚会轻微影响分页，封面总页数以最终文件为准
PAGES=$(officecli view "$F" stats --page-count 2>/dev/null | grep -i "^Pages:" | grep -oE "[0-9]+")
echo "最终页数：$PAGES"
P=$(officecli query "$F" 'p:contains("总页数")' --json 2>/dev/null |
    python -c "import sys,json;print([r['path'] for r in json.load(sys.stdin)['data']['results'] if r['type']=='paragraph'][0])")
officecli set "$F" "$P" --prop text="总页数：$PAGES" --prop align=center --prop size=16pt --prop font.ea=宋体 >/dev/null
officecli save "$F" >/dev/null
officecli close "$F" >/dev/null 2>&1 || true
echo "完成"
