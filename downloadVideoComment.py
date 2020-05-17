import requests
import json
import html2text as ht
import re
from config import COOKIE, HEADER, DOWNLOADPATH
import time
import random
import os
url ="https://time.geekbang.org/serv/v1/article"
commentUrl = "https://time.geekbang.org/serv/v1/comments"
class TestDownloadArticle :

 
     # 下载成makedown文档
    def download_markdown2(self, title, commentList):
        title = re.sub(r'[\?\\/\:\*"<>\|]', "", title)
        title = title.replace("\t","")
        with open(os.path.join(DOWNLOADPATH, title + ".md"), "w",encoding='utf-8') as f:
            i =1
            for com in commentList:
                qus = re.sub(r'[\?\\/\:\*"<>\|]', "", com.get("Qus"))
                f.write("### " + "Qus"+str(i)+"："+ qus + "\n")
                f.write(ht.HTML2Text().handle(re.sub(r"[\xa5]", "","Ans:" + com.get("Ans"))))
                i=i+1

    def get_article_list(self, cid):
        url = "https://time.geekbang.org/serv/v1/column/articles"
        data = {
            "cid": cid,
            "order": "earliest",
            "prev": 0,
            "sample": False,
            "size": 200,
        }
        # data 一定要dumps, 不然会报系统错误 虽然返回值是200
        r=requests.post(url, data=json.dumps(data), headers =HEADER, cookies =COOKIE)
        if r.status_code != 200:
            print(r.status_code)
            print("get_article_list----检测登录")
            exit(0)
        articleList = r.json()["data"]["list"]
        articleListArr = []
        for article in articleList:
            articleListArr.append({
                "id":article.get("id"),
                "title":article.get("article_title")
            })
        return articleListArr

    def get_comment(self, id, prev):
        commentArr = []
        data = {
            "aid": str(id),
            "prev": prev
        }
        comment_header = {
            "Content-Type": "application/json",
            "Referer":"https://time.geekbang.org/column/article/" + str(id),
            "Host": "time.geekbang.org",
            "Origin": "https://time.geekbang.org",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"
        }
        # data 一定要dumps, 不然会报系统错误 虽然返回值是200
        r=requests.post(commentUrl, data=json.dumps(data), headers =comment_header, cookies =COOKIE)    
        if r.status_code != 200:
            print("检测登录")
            exit(0)
        response_data = r.json()["data"]
        articleList = response_data.get("list")
        commentArr.extend(self.parse_comment(articleList))

        more = response_data.get("page").get("more")
        if more:
            score = articleList[-1].get("score")
            commentArr.extend(self.get_comment(id,score))
        return commentArr

    def parse_comment(self,list):
        commentArr = []
        # 过滤掉没有回复的评论
        for comment in list:
            replies = comment.get("replies")
            content = comment.get("comment_content")
            if replies:
                for reply in replies:
                    commentArr.append({
                        "Qus": content,
                        "Ans": reply.get("content")
                    })

        return commentArr
    # count是代表从第几篇开始下载
    def run(self, cid, count = None):
        articleList = self.get_article_list(cid)
        for index, article in enumerate(articleList):
            if count is not None and index < int(count-1):
                continue
            print(article)
            commentList = self.get_comment(article.get("id"),"0")
            self.download_markdown2(article.get("title"),commentList)
            time.sleep(random.randint(3, 10))


if __name__ == '__main__':
    count = 4
    TestDownloadArticle().run(cid= "100030501", count=count)
   