from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from typing import List

from utils.chen_pagination import MyPagination
from ninja.pagination import paginate
from ninja import Query
from utils.chen_response import ChenResponse
from utils.chen_crud import create,multi_delete
from apps.project.models import Project,Round
from apps.project.schemas.project import ProjectRetrieveSchema, ProjectFilterSchema, ProjectCreateInput, DeleteSchema

@api_controller("/testmanage/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['项目表相关'])
class ProjectController(ControllerBase):
    @route.get("index", response=List[ProjectRetrieveSchema])
    @paginate(MyPagination)
    def list_project(self, filters: ProjectFilterSchema = Query(...)):
        for attr, value in filters.__dict__.items():
            if getattr(filters, attr) is None:
                setattr(filters, attr, '')
        # 处理时间范围
        start_time = self.context.request.GET.get('searchOnlyTimeRange[0]')
        if start_time is None:
            start_time = "2000-01-01"
        end_time = self.context.request.GET.get('searchOnlyTimeRange[1]')
        if end_time is None:
            end_time = '5000-01-01'
        date_list = [start_time, end_time]
        # 前端返回的member
        member_list = []
        for key, value in self.context.request.GET.items():
            if key.find('member') != -1:
                member_list.append(self.context.request.GET[key])
        qs = Project.objects.filter(ident__icontains=filters.ident, name__icontains=filters.name,
                                    beginTime__range=date_list, duty_person__icontains=filters.duty_person,
                                    security_level__icontains=filters.security_level,
                                    report_type__icontains=filters.report_type, step__icontains=filters.step,
                                    member__contains=member_list).order_by("-create_datetime")
        return qs

    @route.post("/save")
    def create_project(self, data: ProjectCreateInput):
        data_dict = data.dict()
        ident_qucover = Project.objects.filter(ident=data.dict()['ident'])
        if ident_qucover:
            return ChenResponse(code=400, status=400, message="项目标识重复，请重新设置")
        qs = create(self.context.request, data_dict, Project)
        # 创建项目时候添加第一轮测试
        if qs:
            Round.objects.create(project_id=qs.id,key='0',level='0',title='第1轮测试',name='第1轮测试',remark='第一轮测试',ident=''.join([qs.ident,'-R1']))
            return ChenResponse(code=200, status=200, message="添加项目成功，并添加第一轮测试")

    @route.put("/update/{project_id}")
    def update_project(self, project_id: int, payload: ProjectCreateInput):
        project = self.get_object_or_exception(Project, id=project_id)
        # 更新操作
        for attr, value in payload.dict().items():
            # setattr针对的是class
            setattr(project, attr, value)
        project.save()
        return ChenResponse(code=200, status=200, message="项目更新成功")

    @route.delete("/delete")
    def delete(self,data:DeleteSchema):
        multi_delete(data.ids, Project)
        return ChenResponse(message="删除成功！")
