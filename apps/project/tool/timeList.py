from apps.createDocument.extensions.documentTime import DocTime
from django.shortcuts import get_object_or_404
from apps.project.models import Project

def time_return_to(id):
    project_obj = get_object_or_404(Project, id=id)
    time = []
    time_parser = DocTime(id)
    dg_otime = {}
    # 1.大纲-测评地点与时间相关的时间
    temp_dict = time_parser.dg_address_time()
    dg_otime['title'] = '测评大纲'
    dg_otime['被测件接收'] = [temp_dict['beginTime_strf'], temp_dict['beginTime_strf']]
    dg_otime['大纲编制时间'] = [temp_dict['dgCompileStart'], temp_dict['dgCompileEnd']]
    dg_otime['设计与实现时间'] = [temp_dict['designStart'], temp_dict['designEnd']]
    # 2.大纲-文档时间
    temp_dict = time_parser.dg_final_time()
    dg_otime['封面时间'] = temp_dict['cover_time']
    dg_otime['拟制时间'] = temp_dict['preparation_time']
    dg_otime['校对时间'] = temp_dict['inspect_time']
    dg_otime['审核时间'] = temp_dict['auditing_time']
    dg_otime['批准时间'] = temp_dict['ratify_time']
    dg_otime['创建时间'] = temp_dict['create_doc_time']
    dg_otime['v1版本时间'] = temp_dict['doc_v1_time']
    time.append(dg_otime)
    # 3.说明的时间
    temp_dict = time_parser.sm_final_time()
    sm_otime = {
        'title': '测试说明',
        '封面时间': temp_dict['cover_time'],
        '拟制时间': temp_dict['preparation_time'],
        '校对时间': temp_dict['inspect_time'],
        '审核时间': temp_dict['auditing_time'],
        '批准时间': temp_dict['ratify_time'],
        '创建时间': temp_dict['create_doc_time'],
        'v1版本时间': temp_dict['doc_v1_time']
    }
    time.append(sm_otime)
    # 4.记录时间
    temp_dict = time_parser.jl_final_time()
    jl_otime = {
        'title': '测试记录',
        '封面时间': temp_dict['cover_time'],
        '拟制时间': temp_dict['preparation_time'],
        '校对时间': temp_dict['inspect_time'],
        '审核时间': temp_dict['auditing_time'],
        '批准时间': temp_dict['ratify_time'],
        '创建时间': temp_dict['create_doc_time'],
        'v1版本时间': temp_dict['doc_v1_time']
    }
    time.append(jl_otime)
    # 5.回归说明时间
    # 5.回归记录时间
    rounds = project_obj.pField.all()
    for round in rounds:
        if round.key == '0':
            continue
        temp_dict = time_parser.hsm_final_time(round.key)
        round_otime = {
            'title': f'第{int(round.key) + 1}轮测试说明',
            '封面时间': temp_dict['cover_time'],
            '拟制时间': temp_dict['preparation_time'],
            '校对时间': temp_dict['inspect_time'],
            '审核时间': temp_dict['auditing_time'],
            '批准时间': temp_dict['ratify_time'],
            '创建时间': temp_dict['create_doc_time'],
            'v1版本时间': temp_dict['doc_v1_time']
        }
        time.append(round_otime)
        temp_dict = time_parser.hjl_final_time(round.key)
        round_otime = {
            'title': f'第{int(round.key) + 1}轮测试记录',
            '封面时间': temp_dict['cover_time'],
            '拟制时间': temp_dict['preparation_time'],
            '校对时间': temp_dict['inspect_time'],
            '审核时间': temp_dict['auditing_time'],
            '批准时间': temp_dict['ratify_time'],
            '创建时间': temp_dict['create_doc_time'],
            'v1版本时间': temp_dict['doc_v1_time']
        }
        time.append(round_otime)
    # 6.报告时间
    ## 6.1.报告文档片段-测评时间和地点
    temp_dict = time_parser.bg_address_time()
    bg_otime = {
        'title': '测评报告',
        '被测件接收时间': temp_dict['begin_time'],
        '大纲编制时间': [temp_dict['dg_weave_start_date'], temp_dict['dg_weave_end_date']],
        '测评设计与实现': [temp_dict['sj_weave_start_date'], temp_dict['sj_weave_end_date']],
        '测评总结': [temp_dict['summary_start_date'], temp_dict['summary_end_date']]
    }
    for r in temp_dict['round_time_list']:
        bg_otime[r['name']] = [r['start'], r['end']]
    temp_dict = time_parser.bg_final_time()
    ### 6.2.报告文档时间
    bg_otime['封面时间'] = temp_dict['cover_time'],
    bg_otime['拟制时间'] = temp_dict['preparation_time']
    bg_otime['校对时间'] = temp_dict['inspect_time'],
    bg_otime['审核时间'] = temp_dict['auditing_time'],
    bg_otime['批准时间'] = temp_dict['ratify_time'],
    bg_otime['创建时间'] = temp_dict['create_doc_time'],
    bg_otime['v1版本时间'] = temp_dict['doc_v1_time']
    time.append(bg_otime)
    return time
