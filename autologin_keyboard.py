#
import random
import time

import keyboard
from selenium import webdriver
from selenium.webdriver.common.by import By

## 네이버 로그인 진행
login_id = ""
pw = ""
driver = webdriver.Chrome()
url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/'
driver.get(url)
driver.implicitly_wait(10)
time.sleep(random.uniform(1, 2))
keyboard.write(id, delay=0.1)
time.sleep(random.uniform(1, 2))

keyboard.write(pw, delay=0.1)
time.sleep(random.uniform(1, 2))
keyboard.press_and_release("enter")
time.sleep(10)  # Keeps the browser open for 10 seconds






## 카페 진입
cafeurl = 'https://cafe.naver.com/directwedding'
driver.get(cafeurl)
driver.implicitly_wait(10)
time.sleep(random.uniform(1, 2))

## 게시판 진입 -> 즐겨찾기 결혼준비 토론방 진입
driver.find_element(By.ID, 'favoriteMenuLink113').click()
driver.implicitly_wait(3)
time.sleep(random.uniform(1, 2))

# 공지사항 제외 최근 글 10개의 제목 가져오기 <- 아마 스크롤 필요할 듯?
for n in range(1, 11):
    try:
        # Construct the CSS selector dynamically
        selector = f"main-area > div:nth-child(4) > table > tbody > tr:nth-child({n}) > td.td_article > " \
                   f"div.board-list > div > a"

        # Find the <a> element using the constructed selector
        a_element = driver.find_element(By.CSS_SELECTOR, selector)

        # 제목 및 링크 가져오기
        a_text = a_element.text  # Get the text inside the <a> tag
        a_href = a_element.get_attribute("href")  # Get the href attribute if needed
        print(f"Text: {a_text}, Link: {a_href}")

    except Exception as e:
        print(f"Element for n={n} not found or an error occurred: {e}")
time.sleep(100)

# Close the browser after the delay
driver.quit()
