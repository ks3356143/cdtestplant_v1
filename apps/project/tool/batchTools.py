from ninja.errors import HttpError


def parse_test_content_string(content: str):
    """
    解析前端传来的批量新增测试项testContent字段
    """
    # 判断是否为空字符串
    if not content or not content.strip():
        return []
    create_subDemands = []  # 储存测试子项内容
    current_subDemand: None | dict = None
    lines = content.strip().split("\n")
    line_number = 0

    for i, line in enumerate(lines):
        line_number = i + 1
        line = line.strip()
        # 跳过空行
        if not line:
            continue
        # 检查是否以^开头
        if line.startswith("^"):
            # 标识一个测试子项开始了
            if current_subDemand:
                create_subDemands.append(current_subDemand)
            # 解析新测试子项
            try:
                # 检查是否包含分隔符@，包含则分割
                if '@' in line:
                    [item_name, item_desc] = line.split("@")
                else:
                    item_name = line
                    item_desc = ""

                # 判断名称是否为空
                item_name = item_name.replace("^", "", count=1)
                if not item_name:
                    raise HttpError(400, f"您字符串中，第{line_number}行没有测试子项名称")

                # 组装一个测试子项
                current_subDemand = {
                    'subName': item_name,
                    'subDescription': item_desc,
                    'subStep': []
                }
            except HttpError:
                raise
            except Exception as e:
                print('解析^行报错，后台详情：', e)
                raise HttpError(400, f"您字符串中，第{line_number}行解析错误，错误原因请检查")

        elif '@' in line and current_subDemand is not None:
            try:
                [operation, expect] = line.split('@')
                current_subDemand['subStep'].append({  # type:ignore
                    'operation': operation,
                    'expect': expect
                })
            except Exception as e:
                print('解析步骤行报错，后台详情：', e)
                raise HttpError(400, f"第{line_number}发现您子项步骤格式有问题，请检查")
        else:
            # 这里就是即没有^也没有@的情况，直接跳出本次循环即可
            continue
        # 添加最后一个测试项
    if current_subDemand:
        create_subDemands.append(current_subDemand)
    return create_subDemands


def parse_case_content_string(content: str):
    """
        解析前端传来的批量新增测试用例test_step字段
    """
    # 如果为空返回空列表-不会引起错误因为前端限制
    if not content or not content.strip():
        return []
    create_step = []  # 储存测试子项内容
    lines = content.strip().split("\n")
    line_number = 0
    for i, line in enumerate(lines):
        line_number = i + 1
        line = line.strip()
        # 跳过空行
        if not line:
            continue
        # 判断是否有“@”，如果没有则给用户报错
        if "@" not in line:
            raise HttpError(400, f"第{line_number}行没有使用@符号分割，请检查!")
        # 这里必然有@，组装current_step（一行内@多于1个时给出明确错误，避免 ValueError 直冒 500）
        try:
            [operation, expect] = line.strip().split("@")
        except ValueError:
            raise HttpError(400, f"第{line_number}行@符号数量不正确，请检查!")
        # 错误处理两种情况，操作为空，预期为空
        if not operation.strip():
            raise HttpError(400, f"第{line_number}行@符号前面的输入内容为空，请检查!")
        if not expect.strip():
            raise HttpError(400, f"第{line_number}行@符号后面的预期为空，请检查!")
        # 组装当前步骤行
        create_step.append({
            "operation": operation,
            "expect": expect
        })

    return create_step
