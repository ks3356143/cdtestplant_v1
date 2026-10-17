from typing import List

from ninja_extra import api_controller, ControllerBase, route
from ninja_extra.permissions import IsAuthenticated
from ninja_jwt.authentication import JWTAuth
from django.db import transaction

from apps.project.models import NonrepudiationEvidence
from apps.project.schemas.evidence import EvidenceOutSchema
from utils.permissions import IsAuditor


# 抗抵赖证据查询：仅系统审计员（auditadmin）可查；证据无任何修改/删除接口（GB/T 28452-2012 7.1.2）
@api_controller("/project", auth=JWTAuth(), permissions=[IsAuthenticated, IsAuditor], tags=['抗抵赖证据'])
class NonrepudiationController(ControllerBase):

    @route.get("/nonrepudiation/list", response=List[EvidenceOutSchema], url_name="evidence-list")
    @transaction.atomic
    def list_evidence(self, business_ident: str = None, business_type: str = None,
                      actor_name: str = None):
        """按业务标识/业务类型/主体账号核验证据链"""
        qs = NonrepudiationEvidence.objects.all()
        if business_ident:
            qs = qs.filter(business_ident__icontains=business_ident)
        if business_type:
            qs = qs.filter(business_type=business_type)
        if actor_name:
            qs = qs.filter(actor_name__icontains=actor_name)
        return list(qs[:200])
