from ninja_extra import api_controller, ControllerBase, route
from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.permissions import IsAuthenticated
from ninja.pagination import paginate
from utils.chen_pagination import MyPagination
from django.db import transaction
from typing import List
from utils.chen_response import ChenResponse
from utils.chen_crud import multi_delete
from apps.project.models import Design
from apps.project.schemas.design import DeleteSchema, DesignFilterSchema, DesignModelOutSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['设计需求数据'])
class DesignController(ControllerBase):
    @route.get("/getDesignDemandList", response=List[DesignModelOutSchema], exclude_none=True, url_name="design-list")
    @paginate(MyPagination)
    def get_dut_list(self, datafilter: DesignFilterSchema = Query(...)):
        for attr, value in datafilter.__dict__.items():
            if getattr(datafilter, attr) is None:
                setattr(datafilter, attr, '')
        dut_key = "".join([datafilter.round_id, '-', datafilter.dut_id])
        qs = Design.objects.filter(project__id=datafilter.project_id, dut__key=dut_key,
                                   ident__icontains=datafilter.ident,
                                   name__icontains=datafilter.name,
                                   demandType__contains=datafilter.demandType).order_by("-create_datetime")
        return qs
