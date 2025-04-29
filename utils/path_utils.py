from apps.project.models import Project

def project_path(id: int):
    """
    :param id:传入project_id获取其ident作为路径
    :return:
    """
    project = Project.objects.filter(id=id).first()
    if not project:
        return
    return project.ident
