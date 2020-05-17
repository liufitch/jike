import requests
import json
from config import COOKIE, HEADER

# 获取视频列表
data = {
    "cid": "100026801",
    "order": "earliest",
    "prev": 0,
    "sample": False,
    "size": 200,
}
cookie ={
    "LF_ID":"1581467075446-2640718-2528415",
    "gksskpitn":"c9570efe-d8c2-49e0-bb32-592737e61b90",
    "GCID":"c255527-05df3d4-4df356c-e7cfb54",
    "GRID":"c255527-05df3d4-4df356c-e7cfb54",
    "GCESS":"BAgBAwUEAAAAAAoEAAAAAAkBAQME9QyuXgIE9QyuXgsCBAAGBAYEzJoBBDIsEwAMAQEHBKIHZUEEBAAvDQA-",
    "SERVERID":"1fa1f330efedec1559b3abbcb6e30f50|1588466376|1588464851"
}

url = "https://time.geekbang.org/serv/v1/column/articles"
# data 一定要dumps, 不然会报系统错误 虽然返回值是200
r=requests.post(url, data=json.dumps(data), headers =HEADER, cookies =cookie)

if r.status_code != 200:
    print("检测登录")
    exit(0)


articleList = r.json()["data"]["list"]
fileList = []
for article in articleList:
    # 普清(LD),标清(SD), 高清(HD)视频的清晰度
    title = article.get("article_title")
    videoId = article.get("video_id")
    fileList.append([videoId, title])
    print(videoId, title)
        
file = open("./video_list.json", "w", encoding='utf-8')
file.write(json.dumps(fileList))