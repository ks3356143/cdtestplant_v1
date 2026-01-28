from apps.project.models import TestDemand

def demand_sort_by_designKey(demand_obj: TestDemand) -> tuple[int, ...]:
    """仅限于测试项排序函数，传入sorted函数的key里面"""
    parts = demand_obj.key.split('-')
    sort_tuple = tuple(int(part) for part in parts)
    return sort_tuple

__all__ = ['demand_sort_by_designKey']
