import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath('..'))
from jxnuJWspider import SearchClient

#==================================================
#
#  在本例中，我们将从教务在线下载一张照片
#  根据对教务在线的网址进行分析，我们找到了它访问照片的地址
#  在 SearchClient 的登录状态下，直接访问该地址即可获取照片
#
#==================================================

# 创建一个函数用于下载照片
def savePhoto(SType,num,savePath):
    # 教务在线用的图片后缀是.jpg
    imageType='.jpg'

    # 教务在线上访问照片的真实地址，需要在登录状态下访问，例：https://jwc.jxnu.edu.cn/TeacherPhotos/004758.jpg
    photoUrl={
        '学生':'https://jwc.jxnu.edu.cn/StudentPhoto/',
        '教工':'https://jwc.jxnu.edu.cn/TeacherPhotos/',
    }

    # 检测并创建保存地址
    if not os.path.exists(savePath):
        os.mkdir(savePath)
    
    # 下载并保存一张照片
    with open(os.path.join(savePath,num+imageType),'wb') as ph:
        # 写入文件 ||  获取二进制内容  || 通过字符串相加组成该照片的地址 ||
        #    ↓             ↓                        ↓
        ph.write(jwsc.getHtmlContent(photoUrl[SType]+num+imageType))


# 创建查询会话 （全局变量）
jwsc=SearchClient('202066601001','my password')


if __name__ == "__main__":
    # 设置照片保存地址
    savePath='./photos/'

    # 下载一张照片
    savePhoto('教工','004758',savePath)

    # 通过和前面的几个例子组合，循环调用savePhoto函数就可以轻松下载大量照片
    for i in range(201725501001,201725501010):
        savePhoto('学生',str(i),savePath)
    # ps:学号参数必须是字符串