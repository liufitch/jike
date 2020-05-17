import requests
import json
from config import COOKIE, HEADER, DOWNLOADPATH
from urllib.parse import quote_plus
import re
from binascii import b2a_hex, a2b_hex
import os
import base64
import time

from concurrent.futures import ThreadPoolExecutor, as_completed


videoListUrl = "https://time.geekbang.org/serv/v1/column/articles"
vidoPlayAuthUrl = "https://time.geekbang.org/serv/v3/source_auth/video_play_auth"
m3u8Url = "http://ali.mantv.top/play/info?playAuth="
class DownloadVideo():
    # 获取视频列表
    def getVideoList(self, cid):
        data = {
            "cid": cid,
            "order": "earliest",
            "prev": 0,
            "sample": False,
            "size": 200,
        }
        # data 一定要dumps, 不然会报系统错误 虽然返回值是200
        r = requests.post(videoListUrl, data=json.dumps(data), headers =HEADER, cookies =COOKIE)
        
        if r.status_code != 200:
            print("检测登录")
            exit(0)


        articleList = r.json()["data"]["list"]
        videoList = []
        for article in articleList:
            # 普清(LD),标清(SD), 高清(HD)视频的清晰度
            title = article.get("article_title")
            videoId = article.get("video_id")
            videoList.append({
                "videoId":videoId,
                "title":title,
                "id":article.get("id")
            })
        return videoList
    
    # 获取视频权限
    def getVideoPlayAuth(self, id, vid):
        data = {
            "source_type": 1, 
            "aid": id, 
            "video_id": str(vid)
        }
      
        r = requests.post(vidoPlayAuthUrl, data=json.dumps(data), headers =HEADER, cookies =COOKIE)
        
        if r.status_code != 200:
            print("检测登录")
            exit(0)
        print(str(id)  +"  **** "+ str(vid) + "auth：" + str(r.json()))
        auth = r.json().get("data").get("play_auth")
        return auth
        
    
    # 获取m3u8地址
    def getM3u8(self, id, vid):
        auth = self.getVideoPlayAuth(id,vid)
        tempUrl = m3u8Url+  quote_plus(auth)
        r = requests.get(tempUrl)
        videoInfoList = r.json().get("PlayInfoList")
        if videoInfoList is not None :
            if len(videoInfoList.get("PlayInfo")) == 3:
                for video in videoInfoList.get("PlayInfo"):
                    # "HD" "SD" "LD" 高清晰度 HD 、标准清晰度 SD 、普通清晰度 LD
                    definition = video.get("Definition")
                    if definition == "HD" :
                        return video.get("PlayURL")
            else :
                return videoInfoList.get("PlayInfo")[0].get("PlayURL")
    
    def downloadTS(self, urlObj):
        res = requests.get(urlObj.get("prex") + "/"+ urlObj.get("ts"))
        # 如果是单线程 可以直接 写成mp4文件。 但是要多线程 ts拼接 写成MP4 不行
        with open(os.path.join(DOWNLOADPATH, urlObj.get("ts")), 'ab') as f:
            f.write(res.content)
            f.flush()
        

    def getTs(self, text, title, urlPrex):
        urls = []
        lines = text.text.split('\n')
        for line in lines :
            if line.endswith(".ts"):
                urls.append({
                    "prex":urlPrex,
                    "ts":line
                })
        
        #  # 建立5个线程
        executor = ThreadPoolExecutor(max_workers=5)
       
        # 这种方式 不能传递多参数需要将参数构造成List进行传入；还有一种是将参数构造成dict进行传入
        all_task = [executor.submit(self.downloadTS, (url)) for url in urls]

        # 等待线程结束
        for future in as_completed(all_task):
            print(222)
      
        
        self.merge_file(title,urls[0].get("ts").split("-")[0])

    #ts 合并
    def merge_file(self, title, namePrex):
        print(11111111)
        os.chdir(DOWNLOADPATH)
        # 文件名中不能有 | ：等特殊字符 否则会 报错 错误码：123
        title1 = "".join(re.split("[| : /]",title))
        title1 = title1.replace("\t","")
        # 将所有ts 复制到new.tmp中 然后删除
        cmd = "copy /b " + namePrex +"*.ts "+namePrex+".tmp"
        os.system(cmd)
        os.system('del /Q '+namePrex+'*.ts')
        # os.system('del /Q *.mp4')
        os.rename(namePrex+".tmp",  title1 +".mp4")
               
    
    def run(self, cid, count = None):
        videoList = self.getVideoList(cid)
        
        for  index,video in enumerate(videoList):
            if count is not None and index < count -1:
                continue
            m3u8Path = self.getM3u8(video.get("id"), video.get("videoId"))
            tsPathText = requests.get(m3u8Path)
            self.getTs(tsPathText,video.get("title"), m3u8Path.rsplit("/", 1)[0] )
        


if __name__ == '__main__':
    ## count  是从第count 开始下载. 从0 开始的话是None
    ## cid 是课程编号。https://time.geekbang.org/serv/v3/learn/product 返回的 集合中的pid 就是课程编号
    count = 4
    DownloadVideo().run(cid="100030501", count=count)






