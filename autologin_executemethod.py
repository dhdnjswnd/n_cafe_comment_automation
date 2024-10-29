# 샘플 Python 스크립트입니다.
import pyperclip
# Shift+F10을(를) 눌러 실행하거나 내 코드로 바꿉니다.
# 클래스, 파일, 도구 창, 액션 및 설정을 어디서나 검색하려면 Shift 두 번을(를) 누릅니다.


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random


# Function to simulate human-like typing with random delays
################################################################################################


################################################################################################


id = ""
pw = ""

driver = webdriver.Chrome()
url = 'https://www.naver.com/'
driver.get(url)



# 로그인 버튼 클릭
time.sleep(3)
driver.find_element(By.CSS_SELECTOR, "#account > div > a").click()

time.sleep(random.uniform(1, 2))
# 아이디입력
# id_element = driver.find_element(By.ID, 'id')
# id_element.click()
actions = ActionChains(driver)
id_element = driver.find_element(By.ID, 'id')
human_typing(id_element, id)
time.sleep(random.uniform(1, 2))  # 1초 기다림
# 비밀번호 입력
actions.key_down(Keys.TAB).perform()
actions.key_up(Keys.TAB).perform()
password_element = driver.switch_to.active_element
time.sleep(random.uniform(1, 2))  # 1초 기다림
human_typing(password_element, pw)

time.sleep(random.uniform(10, 20))
password_element.send_keys(Keys.ENTER)


# pw_element = driver.find_element(By.ID, "pw")

# Add a delay to prevent the browser from closing immediately
time.sleep(100)  # Keeps the browser open for 10 seconds

# Close the browser after the delay
driver.quit()
