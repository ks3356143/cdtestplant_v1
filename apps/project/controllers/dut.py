from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from typing import List
from utils.chen_response import ChenResponse
from apps.project.models import Dut
from apps.project.schemas.dut import DutModelOutSchema, DutFilterSchema, DutTreeReturnSchema, DutTreeInputSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['被测件数据'])
class DutController(ControllerBase):
    @route.get("/getDutList", response=List[DutModelOutSchema], exclude_none=True)
    @paginate(MyPagination)
    def get_dut_list(self, filters: DutFilterSchema = Query(...)):
        for attr, value in filters.__dict__.items():
            if getattr(filters, attr) is None:
                setattr(filters, attr, '')
        qs = Dut.objects.filter(ident__icontains=filters.ident, name__icontains=filters.name,
                                type__contains=filters.type).order_by("-create_datetime")
        return qs

    # 处理树状数据
    @route.get("/getDutInfo", response=List[DutTreeReturnSchema], url_name="round-info")
    def get_round_tree(self, payload: DutTreeInputSchema = Query(...)):
        qs = Dut.objects.filter(project__id=payload.project_id,round__key=payload.key)
        return qs

    # 添加被测件
    @route.post("/")
