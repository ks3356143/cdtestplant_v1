# 本模块主要以项目开始时间、结束时间、轮次开始时间、结束时间计算文档中的各个时间
from datetime import timedelta, date
from apps.project.models import Project
from django.shortcuts import get_object_or_404
from ninja.errors import HttpError  # 从代码抛出该异常，被ninja截取变为response

def format_remove_heng(dateT: date) -> str:
    """该函数将date对象的横杠-去掉，输出str"""
    return str(dateT).replace('-', '')

def times_by_cover_time(cover_time: date) -> dict:
    """该函数为每个产品文档根据封面时间，渲染签署页时间、文档变更记录时间"""
    return {
        'preparation_time_no_format': cover_time - timedelta(days=2),
        'preparation_time': format_remove_heng(cover_time - timedelta(days=2)),  # 拟制时间：为编制结束时间-2天
        'inspect_time': format_remove_heng(cover_time - timedelta(days=1)),  # 校对时间：为编制时间+1天
        'auditing_time': format_remove_heng(cover_time),
        'ratify_time': format_remove_heng(cover_time),
        'create_doc_time': format_remove_heng(cover_time - timedelta(days=2)),
        'doc_v1_time': format_remove_heng(cover_time)
    }

class DocTime:
    def __init__(self, project_id: int):
        self.project = get_object_or_404(Project, id=project_id)
        # 用户录入时间-项目
        self.p_start = self.project.beginTime  # 被测件接收时间/
        self.p_end = self.project.endTime  # 大纲测评时间周期结束时间/
        # 遍历轮次时间-多个
        self.round_count = self.project.pField.count()
        self.round_time = []  # 轮次按顺序排序
        for round in self.project.pField.all():
            self.round_time.append({
                'start': round.beginTime,
                'end': round.endTime,
                'location': round.location
            })
        # ~~~~由上面时间二次计算得出时间~~~~ -> TODO:可由用户设置间隔时间!!!!
        self.dg_bz_start = self.p_start + timedelta(days=1)  # 大纲编制开始时间，项目开始时间+1天
        self.dg_bz_end = self.dg_bz_start + timedelta(days=6)  # 大纲编制结束时间，大纲编制开始+6天
        self.test_sj_start = self.dg_bz_end + timedelta(days=1)  # 测评设计与实现时间，在大纲编制结束+1天
        self.test_sj_end = self.test_sj_start + timedelta(days=5)  # 测评设计与实现结束，在开始+5天
        # ~~~~储存每个文档的cover_time~~~~
        self.dg_cover_time = self.dg_bz_end
        self.sm_cover_time = self.test_sj_end
        self.jl_cover_time = self.round_time[0]['end']
        self.wtd_cover_time = self.round_time[-1]['end']

    # 该函数生成大纲文档片段-测评时间和地点的时间和地点信息
    def dg_address_time(self):
        """直接返回context去渲染"""
        # 需要判断round_time是否有值
        if len(self.round_time) <= 0:
            raise HttpError(status_code=400, message='您还未创建轮次时间，请填写后生成')
        return {
            'start_year': self.p_start.year,
            'start_month': self.p_start.month,
            'end_year': self.p_end.year,
            'end_month': self.p_end.month,
            'beginTime_strf': format_remove_heng(self.p_start),
            'dgCompileStart': format_remove_heng(self.dg_bz_start),
            'dgCompileEnd': format_remove_heng(self.dg_bz_end),
            'designStart': format_remove_heng(self.test_sj_start),
            'designEnd': format_remove_heng(self.test_sj_end),
            'location': self.round_time[0]['location']
        }

    # 该函数生成报告文档片段-测评时间和地点【注意使用了dg_address_time -> 所以后续有修改注意前导】
    def bg_address_time(self):
        if len(self.round_time) <= 0:
            raise HttpError(status_code=400, message='您还未创建轮次时间，请填写后生成')
        # 先使用大纲的时间行数作为前三行
        cname = ['首轮测试', '第二轮测试', '第三轮测试', '第四轮测试', '第五轮测试', '第六轮测试', '第七轮测试',
                 '第八轮测试', '第九轮测试', '第十轮测试']
        dg_address_time = self.dg_address_time()
        round_time_list = []
        index = 0
        for round_dict in self.round_time:
            one_dict = {
                'name': cname[index],
                'start': format_remove_heng(round_dict['start']),
                'end': format_remove_heng(round_dict['end']),
                'location': round_dict['location']
            }
            index += 1
            round_time_list.append(one_dict)
        return {
            'begin_year': dg_address_time['start_year'],
            'begin_month': dg_address_time['start_month'],
            'end_year': dg_address_time['end_year'],
            'end_month': dg_address_time['end_month'],
            'begin_time': dg_address_time['beginTime_strf'],
            'dg_weave_start_date': dg_address_time['dgCompileStart'],
            'dg_weave_end_date': dg_address_time['dgCompileEnd'],
            'sj_weave_start_date': dg_address_time['designStart'],
            'sj_weave_end_date': dg_address_time['designEnd'],
            'round_time_list': round_time_list,
            # 测评总结 -> 依据项目结束时间-7 ~ 项目结束时间
            'summary_start_date': format_remove_heng(self.p_end - timedelta(days=7)),
            'summary_end_date': format_remove_heng(self.p_end),
        }

    # 生成报告中测评完成情况 -> 必须依据其他内容生成时间【注意使用了bg_address_time -> 所以后续有修改注意前导】
    def bg_completion_situation(self):
        bg_timer_dict = self.bg_address_time()
        xq_fx_time_end = self.dg_bz_start + timedelta(days=2)
        ch_time_start = xq_fx_time_end + timedelta(days=1)
        ch_time_end = self.dg_bz_end
        if len(self.round_time) < 1:
            raise HttpError(status_code=400, message='您还未创建第一轮测试的时间，请填写后再生成')
        return {
            'start_time_year': bg_timer_dict['begin_year'],
            'start_time_month': bg_timer_dict['begin_month'],
            'xq_fx_time_start_year': self.dg_bz_start.year,
            'xq_fx_time_start_month': self.dg_bz_start.month,
            'xq_fx_time_start_day': self.dg_bz_start.day,
            'xq_fx_time_end_year': xq_fx_time_end.year,  # 需求分析结束时间是大纲编制开始+2
            'xq_fx_time_end_month': xq_fx_time_end.month,
            'xq_fx_time_end_day': xq_fx_time_end.day,
            'ch_start_year': ch_time_start.year,
            'ch_start_month': ch_time_start.month,
            'ch_start_day': ch_time_start.day,
            'ch_end_year': ch_time_end.year,
            'ch_end_month': ch_time_end.month,
            'ch_end_day': ch_time_end.day,
            'sj_start_year': self.test_sj_start.year,
            'sj_start_month': self.test_sj_start.month,
            'sj_start_day': self.test_sj_start.day,
            'sj_end_year': self.test_sj_end.year,
            'sj_end_month': self.test_sj_end.month,
            'sj_end_day': self.test_sj_end.day,
            'end_time_year': self.p_end.year,
            'end_time_month': self.p_end.month,
            'exec_start_time_year': self.round_time[0]['start'].year,
            'exec_start_time_month': self.round_time[0]['start'].month,
            'exec_start_time_day': self.round_time[0]['start'].day,
            'exec_end_time_year': self.round_time[0]['end'].year,
            'exec_end_time_month': self.round_time[0]['end'].month,
            'exec_end_time_day': self.round_time[0]['end'].day,
        }

    # 该函数生成最终大纲的时间
    def dg_final_time(self):
        cover_time = self.dg_bz_end
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        # 新增给大纲模版10.2章节context
        context.update(basic_line1=cover_time.strftime("%Y年%m月"), basic_line2=self.p_end.strftime("%Y年%m月"))
        # 新增给大纲模版10.3.2章节的context
        sm_context = self.sm_final_time()
        context.update(sm_end_time=sm_context['preparation_time_no_format'].strftime("%Y年%m月"))
        return context

    # 该函数生成说明文档的时间 -> 依据项目时间而非用户第一轮填写时间!
    def sm_final_time(self):
        cover_time = self.test_sj_end  # 封面时间：为大纲时间中“测评设计与实现”结束时间
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        return context

    # 该函数生成记录文档的时间 -> 依据第一轮测试用户填写的事件
    def jl_final_time(self):
        if len(self.round_time) < 1:
            raise HttpError(status_code=400, message='您还未创建第一轮测试的时间，请填写后再生成')
        cover_time = self.round_time[0]['end']  # 封面时间为用户填写第一轮结束时间
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        return context

    # 问题单的时间 -> 依据最后一轮次的结束时间+1天
    def wtd_final_time(self):
        if len(self.round_time) < 1:
            raise HttpError(status_code=400, message='您还未创建第一轮测试的时间，请填写后再生成')
        cover_time = self.round_time[-1]['end']
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        return context

    # 回归测试说明时间 -> 根据第二轮、第三轮...的开始时间
    def hsm_final_time(self, round_key: str):
        if len(self.round_time) < int(round_key) + 1:
            raise HttpError(status_code=400, message='您填写的回归轮次时间不正确，请填写后再生成')
        cover_time = self.round_time[int(round_key)]['start']
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        return context

    # 回归测试记录时间 -> 根据第二轮、第三轮...的结束时间
    def hjl_final_time(self, round_key: str) -> dict:
        if len(self.round_time) < int(round_key) + 1:
            raise HttpError(status_code=400, message='您填写的回归轮次时间不正确，请填写后再生成')
        cover_time = self.round_time[int(round_key)]['end']
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        return context

    # 生成报告非过程时间 -> 根据项目结束时间来定
    def bg_final_time(self) -> dict:
        if len(self.round_time) <= 0:
            raise HttpError(status_code=400, message='您还未创建轮次时间，请填写后生成')
        cover_time = self.p_end
        # 这里做判断，如果项目结束时间/最后一轮结束时间
        if cover_time < self.round_time[-1]['end']:
            raise HttpError(500, message='项目结束时间早于最后一轮次结束时间或等于开始时间，请修改项目结束时间')
        context = times_by_cover_time(cover_time)
        context.update(cover_time=cover_time.strftime("%Y年%m月%d日"))
        return context
