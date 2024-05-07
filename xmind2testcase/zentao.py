#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import csv
import logging
import os
from xmind2testcase.utils import get_xmind_testcase_list, get_absolute_path

"""
Convert XMind fie to Zentao testcase csv file 

Zentao official document about import CSV testcase file: https://www.zentao.net/book/zentaopmshelp/243.mhtml 
"""


def xmind_to_zentao_csv_file(xmind_file, merge=False):
    """Convert XMind file to a zentao csv file"""
    xmind_file = get_absolute_path(xmind_file)
    logging.info('Start converting XMind file(%s) to zentao file...', xmind_file)
    testcases = get_xmind_testcase_list(xmind_file)

    fileheader = ["所属模块", "用例标题", "前置条件", "步骤", "预期", "关键词", "优先级", "用例类型", "适用阶段"]
    zentao_testcase_rows = [fileheader]
    for testcase in testcases:
        row = gen_a_testcase_row(testcase)
        zentao_testcase_rows.append(row)

    zentao_file = xmind_file[:-6] + '.data'
    if os.path.exists(zentao_file):
        os.remove(zentao_file)
        # logging.info('The zentao csv file already exists, return it directly: %s', zentao_file)
        # return zentao_file

    if merge:
        zentao_testcase_rows = merge_testcase_same_name(zentao_testcase_rows=zentao_testcase_rows)

    with open(zentao_file, 'w', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerows(zentao_testcase_rows)
        logging.info('Convert XMind file(%s) to a zentao csv file(%s) successfully!', xmind_file, zentao_file)

    return zentao_file
    # return zentao_testcase_rows


def gen_a_testcase_row(testcase_dict):
    case_module = gen_case_module(testcase_dict['suite'])
    case_title = testcase_dict['name']
    case_precontion = testcase_dict['preconditions']
    case_step, case_expected_result = gen_case_step_and_expected_result(testcase_dict['steps'])
    case_keyword = ''
    case_priority = gen_case_priority(testcase_dict['importance'])
    case_type = gen_case_type(testcase_dict['execution_type'])
    case_apply_phase = '功能测试阶段'
    row = [case_module, case_title, case_precontion, case_step, case_expected_result, case_keyword, case_priority, case_type, case_apply_phase]
    return row


def gen_case_module(module_name):
    if module_name:
        module_name = module_name.replace('（', '(')
        module_name = module_name.replace('）', ')')
    else:
        module_name = '/'
    return module_name


def gen_case_step_and_expected_result(steps):
    case_step = ''
    case_expected_result = ''

    for step_dict in steps:
        case_step += str(step_dict['step_number']) + '. ' + step_dict['actions'].replace('\n', '').strip() + '\n'
        case_expected_result += str(step_dict['step_number']) + '. ' + \
            step_dict['expectedresults'].replace('\n', '').strip() + '\n' \
            if step_dict.get('expectedresults', '') else ''

    return case_step, case_expected_result


def gen_case_priority(priority):
    mapping = {1: '1', 2: '2', 3: '3', 4:'4'}
    if priority in mapping.keys():
        return mapping[priority]
    else:
        return '3'


def gen_case_type(case_type):
    mapping = {1: '功能测试', 2: '自动'}
    if case_type in mapping.keys():
        return mapping[case_type]
    else:
        # 修改默认功能测试
        return '功能测试'

def add_team_num(num, row):
    team_split = row[3].split('\n')[:-1]
    team_add_num = [num + item for item in team_split]
    team = '\n'.join(team_add_num)
    row[3] = team
    team_split = row[4].split('\n')[:-1]
    team_add_num = [num + item for item in team_split]
    team = '\n'.join(team_add_num)
    row[4] = team

def merge_testcase_same_name(zentao_testcase_rows):
    zentao_csv_rows = zentao_testcase_rows[1:]
    zentao_csv = []
    for row in zentao_csv_rows:
        # 使用" > "分割第二个变量
        split_values = row[1].split(" > ")
        if len(split_values) < 2:
            split_values.append(split_values[0])
        if len(split_values) > 2:
            split_values[1] = ''.join(split_values[1:])
        # 将分割的第一个值添加到第三和第四个值的开头
        row[1] = split_values[0]
        row[3] = split_values[1] + '\n' + row[3]
        row[4] = split_values[1] + '\n' + row[4]
        # 打印处理后的行
        # print(row)
        zentao_csv.append(row)

    # 创建一个字典用于存储合并后的行
    merged_rows = {}
    num_rows = {}
    # 遍历列表中的每一行
    for row in zentao_csv:
        key = row[1]  # 使用第二个变量作为字典的键
        if key in merged_rows:
            # 如果字典中已经存在相同的键，则将第三、第四元素相加
            num_rows[key] += 1
            num = str(num_rows[key]) + '.'
            add_team_num(num, row)
            merged_rows[key][4] += '\n'
            merged_rows[key][3] += '\n'
            merged_rows[key][4] += row[4]
            merged_rows[key][3] += row[3]
        else:
            # 如果字典中不存在相同的键，则将当前行添加到字典中
            add_team_num('1.', row)
            merged_rows[key] = row
            num_rows[key] = 1

    # 将字典转换为列表
    merged_rows_list = list(merged_rows.values())
    merged_rows_list.insert(0,zentao_testcase_rows[0])
    
    return merged_rows_list

if __name__ == '__main__':
    xmind_file = r'E:\A_CODE\python\Maintain\xmind2testcase_fork\docs\HOME2.xmind'
    zentao_csv_file = xmind_to_zentao_csv_file(xmind_file)
    print('Conver the xmind file to a zentao csv file succssfully: %s', zentao_csv_file)