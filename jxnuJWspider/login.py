# -*- coding:utf8 -*- 
import requests
import re
import time
import json
from PIL import Image
from io import BytesIO
import os

LOGIN_URL='https://jwc.jxnu.edu.cn/Portal/LoginAccount.aspx?t=account'
PASSCODE_URL='https://jwc.jxnu.edu.cn/Portal/'
HOME_URL = "https://jwc.jxnu.edu.cn/User/Default.aspx"

class JWclient:
    _session = requests.session()
    cookiePath='./JWCookies.json'
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    }
    def __init__(self,usrnum,password):
        # 建立对象的时候直接调用登录
        self.login(usrnum,password)

    def login(self,usrnum,password):
        # 创建会话并登录
        # 先尝试使用cookies，如果登陆失败，再用账号密码登录
        if os.path.isfile(self.cookiePath):
            self.loadCookies()
            if self.loginStatus():
                print("使用cookies登录")
                return
            else:
                self._session.cookies.clear_session_cookies()
        print(f"cookie失效或不存在，开始登录...")
        loginPage=self.getHtmlText(LOGIN_URL)
        ccUrl=PASSCODE_URL+re.findall(r'<img id="_ctl0_cphContent_imgPasscode" src="(.*?)" border="0" style="height:32px;width:80px;" />',loginPage,re.I)[0]
        img=Image.open(BytesIO(requests.get(ccUrl).content))
        img.show()
        checkcode=input("请输入验证码(不区分大小写)：").upper()
        postData={
            '_ctl0:cphContent:ddlUserType': 'Student',
            '_ctl0:cphContent:txtUserNum': usrnum,
            '_ctl0:cphContent:txtPassword': password,
            '_ctl0:cphContent:txtCheckCode': checkcode,
            '_ctl0:cphContent:btnLogin': '登录',
        }
        postData.update(getHiddenvalue(loginPage))
        res=self._session.post(LOGIN_URL, data=postData, headers=self.header)
        res.encoding = 'UTF-8'
        try:
            alert=re.findall(r"<script language='javascript' defer>alert[(]'(.*?)'[)];</script>",res.text,re.I)[0]
            raise ConnectionError(alert)
        except IndexError:
            if self.loginStatus():
                print('登录成功')
                self.saveCookies()
            else:
                raise ConnectionError('登陆失败，错误原因未知')
        except ConnectionError:
            raise
    
    def getHtmlText(self, url,coding='UTF-8'):
        try:
            r = self._session.get(url, headers=self.header)
            #print(f"Status : {r.status_code}")
            r.raise_for_status()  # 如果非200产生异常
            r.encoding = coding
            return r.text
        except:
            print('网络连接发生错误:',r.status_code)
            raise
    def getHtmlContent(self,url):
        try:
            r = self._session.get(url, headers=self.header)
            r.raise_for_status()  # 如果非200产生异常
            return r.content
        except:
            print('网络连接发生错误:',r.status_code)
            raise
    
    def saveCookies(self):
        # 保存cookies
        with open(self.cookiePath, "w") as fp:
            json.dump(requests.utils.dict_from_cookiejar(self._session.cookies), fp)
    
    def loadCookies(self):
        # 载入cookies
        with open(self.cookiePath, "r") as fp:
            self._session.cookies=requests.utils.cookiejar_from_dict(json.load(fp))
    
    def loginStatus(self):
        #通过访问个人信息页面来判断是否为登录状态
        if re.search(r'江西师范大学 教务在线', self.getHtmlText(HOME_URL)):
            return True
        else:
            return False
def getHiddenvalue(text):
    # 获取VIEWSTATE和EVENTVALIDATION
    data={
        '__VIEWSTATE':re.findall(r'<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.*?)" />',text,re.I)[0],
        '__EVENTVALIDATION':re.findall(r'<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.*?)" />',text,re.I)[0]
    }
    return data
