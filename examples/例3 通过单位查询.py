# -*- coding: utf-8 -*-  

import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath('..'))
from jxnuJWspider import SearchClient
import openpyxl
import time

#==================================================
#
#  在本例中，我们将尝试教务在线中的 所在单位 查询
#  通过对数信学院17级各个班级的单位查询，
#  我们可以获取数信学院17级全体名单，并把结果保存在新建的表格中
#
#==================================================

if __name__ == "__main__":
    #创建查询会话 (需要你手动填入自己的教务在线的账号和密码)
    jwsc=SearchClient('202066601001','my password')

    #创建用于写入结果的表格
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "查询结果"
    ws.append(['学院','班级名称','学号','姓名','性别'])

    #手动输入学院和班级列表(必须输入教务在线上的全称)
    college='数学与信息科学学院'
    classes=[
        '17级数学与应用数学1班',
        '17级数学与应用数学2班',
        '17级数学与应用数学3班',
        '17级数学与应用数学4班',
        '17级数学与应用数学英才班',
        '17级数学与应用数学（免费师范生）班',
        '17级信息与计算科学班',
        '17级统计学班',
        '17级经济统计学班']

    #=========================开始查询=========================
    i=1
    for c in classes:
        print(c)

        #调用查询并返回到data
        data=jwsc.searchByUnit('学生',college,c)

        #将数据写入表格
        for d in data:
            ws.cell(row=i+1,column=1).value = d['所在单位']
            ws.cell(row=i+1,column=2).value = d['班级名称']
            ws.cell(row=i+1,column=3).value = d['学号']
            ws.cell(row=i+1,column=4).value = d['姓名']
            ws.cell(row=i+1,column=5).value = d['性别']
            i+=1

        #设定一个延迟，防止批量访问对教务在线产生负担
        time.sleep(0.5)
    #=========================查询结束=========================

    #保存表格
    wb.save('例3查询结果.xlsx')
    print('查询完成')