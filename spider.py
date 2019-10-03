from func import find_current_post as fPost, find_next_page as fPage, print_information, download_pictures 
import sys

home_url = sys.argv[1]  #  'http://misstoyger.lofter.com/
current_url = home_url
next_url = ''

while True:
    if current_url:
        posts, current_page = fPost(current_url)
        print_information(posts)
        next_url = fPage(current_page, home_url)
        dowanload_pictures(posts)
        current_url = next_url
    else:
        break

print('Program completing')
