# -*- coding:utf8 -*- 
import requests
from bs4 import BeautifulSoup
import time
from jxnuJWspider.login import JWclient

class SearchClient(JWclient):
    def __init__(self,usrnum,password):
        super().__init__(usrnum,password)
        self.__searchUrl={
            '学生':r"https://jwc.jxnu.edu.cn/User/default.aspx?&&code=119&uctl=MyControl%5call_searchstudent.ascx",
            '教工':r"https://jwc.jxnu.edu.cn/User/default.aspx?&&code=120&uctl=MyControl%5call_teacher.ascx"
        }
        self.__dataKeys={
            '学生':['所在单位','班级名称','姓名','学号','性别'],
            '教工':['所在单位','姓名','教号','性别']
        }
        self.__unitIds={}

    def search(self,SType,value,SWay='姓名',SQLType='精确'):
        """
        条件查询, 参数类型均为srting
        :param SType: 对象类型 '学生' or '教工'
        :param value: 查询值
        :param SWay: 查询方式 '姓名' or '学号' or '教号'
        :param SQLType: 查询类型 '精确' or '模糊' 
        """
        if SType=='学生':
            if not (SWay=='姓名' or SWay=='学号'):
                raise ValueError("参数输入错误，查询方式为'姓名'或'学号'",SWay)
        elif SType=='教工':
            if not (SWay=='姓名' or SWay=='教号'):
                raise ValueError("参数输入错误，查询方式为'姓名'或'教号'",SWay)
        else:
            raise ValueError("参数输入错误，对象类型为'学生'或'教工'",SType)
        if not (SQLType=='精确' or SQLType=='模糊'):
            raise ValueError("参数输入错误，查询类型为'精确'或'模糊'",SQLType)
        postData={
            '_ctl1:rbtType': 'SQL',
            '_ctl1:txtKeyWord': value,
            '_ctl1:ddlType': SWay,
            '_ctl1:ddlSQLType': SQLType,
            '_ctl1:btnSearch': '查询',
        }
        postData.update(self._getHiddenvalue(self.getHtmlText(self.__searchUrl[SType])))
        return self.__handleResp(self._session.post(self.__searchUrl[SType], data=postData, headers=self.header),SType)
    
    def searchByUnit(self,SType,college,sclass=''):
        """ 
        所在单位查询, 参数类型均为srting
        :param SType:对象类型 '学生' or '教工'
        :param college:查询的学院、单位全称
        :param sclass:查询的班级全称，如果你不知道这些全称，请直接在教务在线上查看 
        """
        if SType=='学生':
            if sclass=='':
                raise ValueError("参数输入错误，需要输入班级")
            self.__getUnitId(True,college)
            if not sclass in self.__unitIds[college]['classes']:
                raise ValueError("参数输入错误，你输入的班级不存在",sclass)
        elif SType=='教工':
            self.__getUnitId(False,college)
        else:
            raise ValueError("参数输入错误，对象类型为'学生'或'教工'",SType)
        postData={
            '_ctl1:rbtType': 'College',
            '_ctl1:ddlCollege': self.__unitIds[college]['id'],
            '_ctl1:btnSearch': '查询',
        }
        if SType=='学生':
            postData['_ctl1:ddlClass']=self.__unitIds[college]['classes'][sclass]
        postData.update(self.__getHiddenvalueOfUnitStu(SType,college))
        req=self._session.post(self.__searchUrl[SType], data=postData, headers=self.header)
        #print(req.status_code)
        return self.__handleResp(req,SType)

    def __getHiddenvalueOfUnitStu(self,SType,college=None):
        postData={
            '_ctl1:rbtType': 'College'
        }
        postData.update(self._getHiddenvalue(self.getHtmlText(self.__searchUrl[SType])))
        req=self._session.post(self.__searchUrl[SType], data=postData, headers=self.header)
        if SType=='教工' or college==None:
            return self._getHiddenvalue(req.text)
        else:
            postData={
                '_ctl1:rbtType': 'College',
                '_ctl1:ddlCollege': self.__unitIds[college]['id'],
            }
            postData.update(self._getHiddenvalue(req.text))
            req=self._session.post(self.__searchUrl[SType], data=postData, headers=self.header)
            return self._getHiddenvalue(req.text)
        
    def __getUnitId(self,stu=False,clgName=None):
        #获取各单位的id
        if len(self.__unitIds)==0:
            postData={
                '_ctl1:rbtType': 'College'
            }
            postData.update(self._getHiddenvalue(self.getHtmlText(self.__searchUrl['教工'])))
            req=self._session.post(self.__searchUrl['教工'], data=postData, headers=self.header)
            table = BeautifulSoup(req.text, "html.parser").find(id="_ctl1_ddlCollege")
            for op in table.find_all('option'):
                self.__unitIds[op.text.replace(' ','')]={}
                self.__unitIds[op.text.replace(' ','')]['id']=op['value']
        if not clgName in self.__unitIds:
            raise ValueError('参数输入错误，你输入的单位不存在',clgName)
        if stu:
            if not 'classes' in self.__unitIds[clgName] :
                postData={
                    '_ctl1:rbtType': 'College',
                    '_ctl1:ddlCollege': self.__unitIds[clgName]['id'],
                }
                postData.update(self.__getHiddenvalueOfUnitStu('学生'))
                req=self._session.post(self.__searchUrl['学生'], data=postData, headers=self.header)
                if req.status_code==500:
                    raise ValueError('参数输入错误，你输入的单位不可用作学生查询',clgName)
                table = BeautifulSoup(req.text, "html.parser").find(id="_ctl1_ddlClass")
                self.__unitIds[clgName]['classes']={}
                for op in table.find_all('option'):
                    self.__unitIds[clgName]['classes'][op.text.replace(' ','')]=op['value']

    def __handleResp(self,req,SType='学生'):
        #处理查询结果，以字典形式返回
        req.encoding = 'utf-8'
        """ with open('test.html','w') as f:
            f.write(req.text) """
        table = BeautifulSoup(req.text, "html.parser").find(id="_ctl1_dgContent")
        getdata=[]
        for i,atr in enumerate(table.find_all("tr")):
            if i!=0:
                getdata.append({})
                tds = atr.find_all("td")
                for j,key in enumerate(self.__dataKeys[SType]):
                    getdata[i-1][key]=tds[j].get_text().replace(' ','')
        return getdata
