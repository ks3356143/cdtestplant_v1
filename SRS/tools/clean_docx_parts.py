# -*- coding: utf-8 -*-
"""清理 docx 中未被正文引用的页眉/页脚部件。

参考模板里保留了 40 多个页眉/页脚部件，重建文档时只有正文引用的那一两个生效，
其余都是模板残留：既增大文件，也把模板原项目的标题留在包里。
本脚本只删除 document.xml.rels 中未被 w:headerReference / w:footerReference
引用的页眉页脚及其关系，不影响正文、样式与已引用的页眉页脚。
"""
import re
import shutil
import sys
import zipfile


def clean(path):
    with zipfile.ZipFile(path) as z:
        doc = z.read("word/document.xml").decode()
        rels = z.read("word/_rels/document.xml.rels").decode()
        used = set(re.findall(r'<w:(?:header|footer)Reference[^>]*r:id="(rId\d+)"', doc))
        drop, keep = set(), []
        for entry in re.findall(r"<Relationship [^>]*/>", rels):
            rid = re.search(r'Id="([^"]+)"', entry).group(1)
            typ = re.search(r'Type="([^"]+)"', entry).group(1)
            tgt = re.search(r'Target="([^"]+)"', entry).group(1)
            if ("/header" in typ or "/footer" in typ) and rid not in used:
                drop.add("word/" + tgt.lstrip("/"))
            else:
                keep.append(entry)
        if not drop:
            print("无残留页眉页脚：", path)
            return 0
        new_rels = ('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    + "".join(keep) + "</Relationships>")
        tmp = path + ".tmp"
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for item in z.infolist():
                if item.filename in drop:
                    continue
                data = z.read(item.filename)
                if item.filename == "word/_rels/document.xml.rels":
                    data = new_rels.encode()
                zo.writestr(item, data)
    shutil.move(tmp, path)
    print(f"已清理 {len(drop)} 个残留页眉页脚部件：{path}")
    return len(drop)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("用法：python SRS/tools/clean_docx_parts.py <docx> [docx ...]")
    for p in sys.argv[1:]:
        clean(p)
