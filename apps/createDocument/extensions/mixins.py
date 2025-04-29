from abc import ABC
from apps.project.models import Project
from django.shortcuts import get_object_or_404
from apps.dict.models import Fragment
from apps.createDocument.extensions.parse_rich_text import RichParser

class FragementToolsMixin(ABC):
    """该混合主要给文档片段进行功能封装"""
    def _generate_frag(self, id: int, doc, doc_name: str):
        """传入项目id/"""
        project_qs = get_object_or_404(Project, id=id)
        replace = False  # 是否替换标志
        rich_text_list = []
        # [deprecated]判断是否有当前项目的文档片段
        fragments = project_qs.frag.all()
        # 传入'片段名称'和判断is_main
        frag: Fragment = fragments.filter(name=doc_name, is_main=True).first()
        if frag:
            replace = True
            rich_text_list = RichParser(frag.content).get_final_format_list(doc)
        return replace, frag, rich_text_list
