import requests
from bs4 import BeautifulSoup as bs
import urllib.request
from urllib.parse import urlsplit, urljoin, urlunsplit

def find_current_post(current_url):
    current_page = requests.get(current_url)
    page_soup = bs(current_page.text, 'lxml')
    post_keyword = '.m-post'
    posts = page_soup.select(post_keyword)
    return posts, current_page
    
def find_next_page(current_page, home_url):
    page_soup = bs(current_page.text, 'lxml')
    page_keyword = '.m-pager'
    pages = page_soup.select(page_keyword)
    page = pages[0]
    active_page = page.select('a.active')[0].text
    print('Current Page is page.{}'.format(active_page))
    next_page = page.select('a.next')
    next_url_suffix = next_page[0]['href']
    if next_page:
        current_url = urljoin(home_url, next_url_suffix) 
    else:
        print('The last page already!')
        current_url = ''
    return current_url

def print_information(lists):
    for post_index, post in enumerate(
            lists,start=1):  #print infomation of homepage
        print('Post.{}'.format(post_index))
        post_url = post.select('a.img')[0]['href']
        print('post_url:{}'.format(post_url))

        pic_url = post.select('a.img > img')[0]['src']
        #       pic_url = pic_url.split('?')[0]
        scheme, netloc, path, _, __ = urlsplit(pic_url) 
        pic_url = urlunsplit((scheme, netloc, path, '', ''))
        print('pic_url:{}'.format(pic_url))
        
        post_date = post.select('a.date')[0]
        post_date_format = post_date.text.strip()
        print('post_date:{}'.format(post_date_format))
        
        post_cmt = post.select('a.cmt')
        if post_cmt:
            post_cmt_format = post_cmt[0].text.strip()
        else:
            post_cmt_format = ''
        print('post_cmt:{}'.format(post_cmt_format))

def download_pictures(lists):
    default_path = '/home/autumanl/pictures/'
    for index_post, post in enumerate(lists):  #print all picture_url of a post
        post_url = post.select('a.img')[0]['href']
        post_page = requests.get(post_url)
        post_soup = bs(post_page.text, 'lxml')
        pictures_url = post_soup.select('div.pic')
        print('post.{}'.format(index_post))
        for index_picture, picture_url in enumerate(pictures_url):
            picture_link = picture_url.select('a.img > img')[0]['src']
            scheme, netloc, path, _, __ = urlsplit(picture_link) 
            picture_link = urlunsplit((scheme, netloc, path, '', ''))
            print('No.{} --> picture_link:{}'.format(index_picture,
                                                    picture_link))
            print('Downloading picture')
            picture_save_path = '{}post.{}picture.{}.jpg'.format(
                picture_save_path, index_post, index_picture)
            reponse = requests.get(picture_link)
            if reponse.status_code == 200:
                with open(picture_save_path, 'wb') as fp:
                    fp.write(picture.content)
            #       local_filename, headers = urllib.request.urlretrieve(
            #       picture_link,picturesavepath)
            print('Finishing')
