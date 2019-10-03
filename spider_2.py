import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlsplit, urljoin, urlunsplit
import sys
import pymongo
from pymongo import MongoClient

home_url = sys.argv[1]
current_url = home_url
global SAVE_DIR
SAVE_DIR = '/home/autumanl/python/crawler_pic/'
client = MongoClient()
db = client.posts
db_posts = db.posts
new_data = []  #用于存取所有 post 整体数据结构为new_data[new_posts[post_in{}]]
'''
Target:
1.All datas should be stored in the same collection,which means 'db_pictures' collection must be deleted.
2.The concept of mininum unit means all kind of information is collected in it.Meanwhile, data relevance is important. Every picture link should be corresponded to its post correctly.
3.Around Unique Key starting to judge.
'''

def spider(current_url, db_collection_post, check_post_id, active):
    current_page = requests.get(current_url)
    page_soup = bs(current_page.text, 'lxml')

    post_keyword = '.m-post'
    page_keyword = '.m-pager'

    posts = page_soup.select(post_keyword)
    pages = page_soup.select(page_keyword) 
    for post_index, post in enumerate(posts, start=1):
        #  爬取当前页信息(帖子URL、时间、评论、文字)
        post_url = post.select('a.date')[0]['href']
        post_id = urlsplit(post_url).path.split('/')[-1]

        #非第一运行，则进行比较
        if active:
            #判断将要爬取的 post 是否已经爬取过
            check = post_id > check_post_id  #当前帖子id与数据库中最新的帖子id比较(大于则为新帖子）
        #第一次运行，则不考虑比较
        else:
            check = True

        if check:
            print('Post.{}'.format(post_index))
            print('post_url:{}'.format(post_url))

            post_date = post.select('a.date')[0]
            post_date_format = post_date.text.strip()
            print('post_date:{}'.format(post_date_format))
            
            post_cmt = post.select('a.cmt')
            if post_cmt:
                post_cmt_format = post_cmt[0].text.strip()
            else:
                post_cmt_format = ''
            print('post_cmt:{}'.format(post_cmt_format))
            
            post_text = post.select('div.text')
            if post_text:
                post_text_format = post_text[0].text.strip()
            else:
                post_text_format = ''
            print('post_text:{}'.format(post_text_format))

            print('Store post\'s information')
            
            #  爬取帖子中的所有图片信息
            new_pictures = []  #用于存放当前帖子的所有图片了链接 
            post_page = requests.get(post_url)
            post_soup = bs(post_page.text, 'lxml')
            pictures_url = post_soup.select('div.pic')
            print('post.{}'.format(post_index))

            for picture_index, picture_url in enumerate(pictures_url, start=1):
                picture_link = picture_url.select('a.img > img')[0]['src']
                scheme, netloc, path, _, _ = urlsplit(picture_link) 
                picture_link = urlunsplit((scheme, netloc, path, '', ''))

                print('No.{} --> picture_link:{}'.format(picture_index,
                                                         picture_link))
                #  存储图片信息到数据库
                print('Store picture\'s information')
                new_pictures.append(
                    picture_link)  #将帖子里所有图片加入 new_pictures 列表

            post_information = {
                "post_id": post_id,
                "date": post_date_format,
                "text": post_text_format,
                "post_pic_link": new_pictures
            }  #存取帖子的 dictionary

            new_data.append(post_information)  #每个帖子信息存入 new_posts 列表，统一插入
            
            check_post_id = post_id  #爬取完后的帖子id用于下一次比较

        else:
            print('Post has been accessed')  #已被爬取，爬取下一个帖子
            break
            

    if check:  #判断本页最后一个帖子是否已被爬取
        # 查找下一页 
        page = pages[0]
        show_page = page.select('a.active')[0].text
        print('Current Page is page.{}'.format(show_page))
        next_page = page.select('a.next')
        if next_page:
            next_url_suffix = next_page[0]['href']
            current_url = urljoin(current_url, next_url_suffix)
            spider(current_url, db_collection_post, check_post_id, active)
        else:
            if new_data:
                new_data.reverse()
                result_data = db_collection_post.insert_many(
                    new_data)  #将所有数据一次性加入数据库
            print('The last page already!')
    else:
        print('The lastest post already!')


if db_posts.count():
    print('Not First Run')
    active = True
else:
    print('First Run')
    active = False

#非第一次运行，查找数据库最新数据
if active:
    check_post_cursor = db_posts.find().sort([('post_id',-1)]).limit(1)  #数据库中最新的帖子
    check_post = list(check_post_cursor)[0]
    check_post_id = check_post['post_id']  #非第一次爬取则取最新帖子id
else:
    check_post_id = ''

spider(current_url, db_posts, check_post_id, active)
