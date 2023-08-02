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
from apps.project.models import Design, Dut, Round, TestDemand, TestDemandContent
from apps.project.schemas.testDemand import DeleteSchema,TestDemandModelOutSchema,TestDemandFilterSchema

@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated], tags=['测试项相关接口'])
class TestDemandController(ControllerBase):
    @route.get("/getTestDemandList", response=List[TestDemandModelOutSchema], exclude_none=True, url_name="testDemand-list")
    @transaction.atomic
    @paginate(MyPagination)
    def get_dut_list(self, datafilter: TestDemandFilterSchema = Query(...)):
        for attr, value in datafilter.__dict__.items():
            if getattr(datafilter, attr) is None:
                setattr(datafilter, attr, '')
        design_key = "".join([datafilter.round_id, '-', datafilter.dut_id,'-',datafilter.design_id])
        qs = TestDemand.objects.filter(project__id=datafilter.project_id, design__key=design_key,
                                   ident__icontains=datafilter.ident,
                                   name__icontains=datafilter.name,
                                   testType__icontains=datafilter.testType,
                                   priority__icontains=datafilter.priority).order_by("-create_datetime")
        return qs
