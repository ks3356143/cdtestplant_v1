from datetime import datetime

from ninja import Schema


class EvidenceOutSchema(Schema):
    """抗抵赖证据输出（仅审计员可查）"""
    id: int
    evidence_type: str
    actor_name: str
    actor_role: str = ""
    action: str
    business_type: str
    business_ident: str
    business_name: str = ""
    data_digest: str
    operation_ip: str = ""
    create_datetime: datetime

