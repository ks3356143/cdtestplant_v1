#!/usr/bin/env bash
# 从参考模板重建《测试管理平台软件需求规格说明》
# 用法：bash SRS/需求规格说明生成/rebuild.sh
set -e
cd "$(dirname "$0")/../.."
F="build/srs-work.docx"
STRIP="SRS/用例文档生成/strip.json"   # 与测试记录共用同一份清空模板正文的命令

officecli close "$F" >/dev/null 2>&1 || true
sleep 1
rm -f "$F"
cp "SRS/参考/参考记录.docx" "$F"
officecli batch "$F" --input "$STRIP" >/dev/null
officecli set "$F" "/header[44]/p[1]" --prop text="测试管理平台软件需求规格说明" >/dev/null

python SRS/需求规格说明生成/build_srs.py
officecli batch "$F" --input build/srs.json | tail -1

python - <<'PY'
import json, subprocess
F = "build/srs-work.docx"
def run(*a):
    return subprocess.run(["officecli", *a], capture_output=True, text=True, encoding="utf-8").stdout

# 表格行不跨页（表头重复已在生成时设置）
tables = json.loads(run("query", F, "table", "--json"))["data"]["results"]
ops = []
for i, t in enumerate(tables, start=1):
    for r in range(1, int(t["format"]["rows"]) + 1):
        ops.append({"command": "set", "path": f"/body/tbl[{i}]/tr[{r}]", "props": {"cantSplit": "true"}})
ops.append({"command": "set", "path": "/settings", "props": {"updateFields": "true"}})
json.dump(ops, open("build/srs-polish.json", "w", encoding="utf-8"), ensure_ascii=False)
print("polish ops:", len(ops))
PY
officecli batch "$F" --input build/srs-polish.json | tail -1

PAGES=$(officecli view "$F" stats --page-count 2>/dev/null | grep -i "^Pages:" | grep -oE "[0-9]+")
echo "页数：$PAGES"
P=$(officecli query "$F" 'p:contains("总页数")' --json 2>/dev/null |
    python -c "import sys,json;print([r['path'] for r in json.load(sys.stdin)['data']['results'] if r['type']=='paragraph'][0])")
officecli set "$F" "$P" --prop text="总页数：$PAGES" --prop align=center --prop size=16pt --prop font.ea=宋体 >/dev/null
officecli save "$F" >/dev/null
officecli close "$F" >/dev/null 2>&1 || true
python SRS/tools/clean_docx_parts.py "$F"
echo "完成：build/srs-work.docx"
