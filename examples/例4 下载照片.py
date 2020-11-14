import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath('..'))
from jxnuJWspider import SearchClient
import requests,time
#==================================================
#
#  在本例中，我们将从教务在线下载照片
#  在登录状态下，直接访问学号对应的照片地址即可获取照片
#  然后将照片储存在本地，便完成了下载
#
#==================================================


# 教务在线上访问照片的真实地址，需要在登录状态下访问，例：https://jwc.jxnu.edu.cn/TeacherPhotos/004758.jpg
PHOTO_URL={
    '学生':'https://jwc.jxnu.edu.cn/StudentPhoto/',
    '教工':'https://jwc.jxnu.edu.cn/TeacherPhotos/',
}

# 教务在线用的图片后缀是.jpg
IMAGE_TYPE='.jpg'

# 创建一个函数用于下载照片
def savePhoto(SType,num,savePath):
    num=str(num)
    # 下载一张照片，使用try语句处理异常
    try:
        #            获取二进制内容  || 通过字符串相加组成该照片的访问地址
        #                  ↓                        ↓
        content=jwsc.getHtmlContent( PHOTO_URL[SType]+num+IMAGE_TYPE )
    except requests.exceptions.HTTPError:
        print(SType,num,'获取失败，可能是教务在线上没有ta的照片')
    except:
        raise

    # 写入到本地文件
    with open(os.path.join(savePath,num+IMAGE_TYPE),'wb') as ph:
        ph.write(content)
    print(SType,num,'下载完成')

# 创建查询会话 （全局变量）
jwsc=SearchClient('202066601001','my password')

if __name__ == "__main__":
    # 设置照片保存地址
    savePath='例4 下载结果'

    # 检测并创建保存地址
    if not os.path.exists(savePath):
        os.mkdir(savePath)

    # 下载一张照片
    savePhoto('教工','004758',savePath)

    # 通过和前面的几个例子组合，先获取学号，然后循环调用savePhoto函数就可以轻松下载大量照片
    for i in range(201925304001,201925304025):
        savePhoto('学生',i,savePath)
        
        #设定一个延迟，减少批量访问对教务在线产生负担
        time.sleep(0.2)
        