import json
import time
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import db

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Host': 'www.pachitele.com'
}


def get_video_url(video_url):
    """
    获取视频ID
    :param video_url:
    :return:
    """
    username = 'wmcool1314@gmail.com'
    password = 'wmcool1314'
    driver_path = r'./chromedriver'
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')  # 无头浏览器
    option.add_argument('--disable-gpu')  # 不需要GPU加速
    option.add_argument('--no-sandbox')  # 无沙箱
    driver = webdriver.Chrome(options=option, service=Service(driver_path))
    driver.get(video_url)
    # 登录
    login_btn = driver.find_element(By.XPATH, '//div[@class="loginBtn"]/a')
    login_btn.click()
    username_input = driver.find_element(By.ID, 'loginMail')
    username_input.send_keys(username)
    password_input = driver.find_element(By.ID, 'loginPassword')
    password_input.send_keys(password)
    time.sleep(1)
    button = driver.find_element(By.XPATH, '//div[@class="mainBtn mt10"]/button')
    button.click()
    time.sleep(4)
    js = "var videoinfo = videojs('videoPlayer'); return videoinfo.mediainfo.sources[0].src"
    res = driver.execute_script(js)
    return res


def get_video_list():
    request_url = "https://www.pachitele.com/contents/search?page={}"
    for page in range(2, 4):
        request_url = request_url.format(page)
        html_response = requests.get(request_url, headers=headers)
        response = etree.HTML(html_response.text)
        video_html_url_list = response.xpath('//div[@class="thumb"]/a/@href')
        thumb_url_list = response.xpath('//div[@class="thumb"]/a/img/@src')
        title_list = response.xpath('//div[@class="mvTitle"]/a/text()')
        category_list = response.xpath('//div[@class="category"]/p/text()')
        summary_list = response.xpath('//div[@class="mvIntro"]/text()')
        publish_time_list = response.xpath('//div[@class="update"]/text()')
        index = 0
        for video_html_url in video_html_url_list:
            video_id = video_html_url.split('/')[-1]
            video_url = get_video_url(video_html_url)
            if video_url:
                video_type = 1
                category = category_list[index]
                if 'パチンコ' in category:
                    category = 'パチンコ'
                    video_type = 1
                elif 'パチスロ' in category:
                    category = 'パチスロ'
                    video_type = 2
                video_info = {
                    "thumb": thumb_url_list[index], "title": title_list[index], "category": category,
                    "summary": summary_list[index], "publish_time": publish_time_list[index], "url": video_html_url,
                    "video_url": video_url, "video_type": video_type
                }
                print(video_info)
                if video_type == 1:
                    db.Redis(0).insert_list('danZhuJi', video_id)
                if video_type == 2:
                    db.Redis(0).insert_list('laoHuJi', video_id)
                db.Redis(0).insert_data(video_id, json.dumps(video_info))
            index += 1


if __name__ == '__main__':
    get_video_list()
