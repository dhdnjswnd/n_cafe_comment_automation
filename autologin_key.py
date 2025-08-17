# 샘플 Python 스크립트입니다.
# Shift+F10을(를) 눌러 실행하거나 내 코드로 바꿉니다.
# 클래스, 파일, 도구 창, 액션 및 설정을 어디서나 검색하려면 Shift 두 번을(를) 누릅니다.
import random
import time
from datetime import datetime
import os
import re

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from naverCafe_Openai import WeddingAssistant



class WeddingAssistantBot:
    """WeddingAssistantBot은 Naver 카페에서 글을 가져와 댓글을 작성하는 자동화 봇입니다."""

    def __init__(self, login_id, pw, log_callback=None, additional_prompt=None):
        self.driver = None  # Initialize later
        self.login_id = login_id
        self.pw = pw
        self.assistant = WeddingAssistant(additional_prompt=additional_prompt)
        self.is_running = True
        self.log_callback = log_callback

    def log(self, message):
        """Logs a message to the callback or prints to console."""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def stop(self):
        """Stops the bot's execution."""
        self.log("실행을 정지 중입니다. 잠시만 기다려주세요")
        self.is_running = False

    def random_delay(self, min_delay=1, max_delay=3):
        """랜덤 딜레이를 주어 자동화 탐지를 피합니다."""
        if not self.is_running:
            return
        time.sleep(random.uniform(min_delay, max_delay))

    def login_naver(self):
        """네이버 로그인 페이지에 접속하고, ID와 PW를 입력하여 로그인합니다."""
        if not self.is_running: return
        self.log("Naver에 로그인 시도 중입니다.")
        url = 'https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/'
        self.driver.get(url)
        self.driver.implicitly_wait(10)
        self.random_delay(1, 2)

        # ID 입력
        self.driver.execute_script(f"document.getElementsByName('id')[0].value='{self.login_id}'")
        self.random_delay(1, 2)

        # PW 입력
        self.driver.execute_script(f"document.getElementsByName('pw')[0].value='{self.pw}'")
        self.driver.find_element(By.XPATH, '//*[@id="log.login"]').click()
        self.random_delay(5, 6)
        self.log("로그인 성공!")

    def navigate_to_cafe(self, cafe_url, board_id):
        """카페 URL과 게시판 ID를 사용해 카페 특정 게시판으로 이동합니다."""
        if not self.is_running: return
        self.log(f"다음 url로 이동합니다. : {cafe_url}")
        self.driver.get(cafe_url)
        self.driver.implicitly_wait(10)
        self.random_delay(1, 2)

        # 게시판 버튼 클릭
        board_btn = self.driver.find_element(By.ID, board_id)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", board_btn)

        # 링크 추출 후 게시판으로 이동
        link = board_btn.get_attribute("href")
        self.random_delay(1, 2)
        self.driver.get(link)
        self.random_delay(3, 4)
        self.log("원하는 게시판으로 이동 완료")

    def switch_to_iframe(self, iframe_selector):
        """특정 iframe으로 전환합니다."""
        if not self.is_running: return
        try:
            iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
            self.driver.switch_to.frame(iframe)
        except Exception as e:
            self.log(f"Could not switch to iframe {iframe_selector}: {e}")

    def fetch_recent_posts(self, count=10):
        """최근 게시글의 제목과 링크를 가져옵니다."""
        if not self.is_running: return []
        self.log(f"Fetching {count} recent posts...")
        posts = []
        for n in range(1, count + 1):
            if not self.is_running: break
            try:
                # 동적으로 CSS Selector를 생성하여 제목 및 링크 가져오기
                selector = f"#cafe_content > div.article-board > table > tbody:nth-child(5) > tr:nth-child({n}) > td:nth-child(2) > div > div > a"

                a_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                title = a_element.text
                link = a_element.get_attribute("href")

                # Skip empty titles
                if title.strip():
                    posts.append({"title": title, "link": link})
                    self.log(f"  - 찾은 게시판 제목 : {title}")

            except Exception as e:
                self.log(f"Could not fetch post at index {n}: {e}")
        self.log(f"Found {len(posts)} posts.")
        return posts

    def _get_next_daily_index(self):
        """Calculates the next index for today's log entries."""
        log_file = "comment_log.txt"
        if not os.path.exists(log_file):
            return 1

        today_str = datetime.now().strftime("%Y-%m-%d")
        last_index = 0
        
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in reversed(lines):
            match = re.search(r"((\d{4}-\d{2}-\d{2}).*?)\[Daily Index: (\d+)\]", line)
            if match:
                last_date_str = match.group(2)
                if last_date_str == today_str:
                    last_index = int(match.group(3))
                break
        
        return last_index + 1

    def log_comment_to_file(self, url, comment_text):
        """Logs the posted comment to a file with a daily index."""
        if not self.is_running: return
        try:
            daily_index = self._get_next_daily_index()
            with open("comment_log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp}] [Daily Index: {daily_index}] URL: {url}\nComment: {comment_text}\n---\n"
                f.write(log_entry)
            self.log("Comment logged to file.")
        except Exception as e:
            self.log(f"Error logging comment to file: {e}")

    def post_comment(self, url, comment_text):
        """특정 URL 게시글에 댓글을 작성합니다."""
        if not self.is_running: return
        self.log(f"Posting comment on: {url}")
        self.driver.get(url)
        self.random_delay(1, 2)
        self.switch_to_iframe("iframe#cafe_main")

        try:
            comment_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.comment_inbox_text"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_box)
            self.random_delay(1, 2)

            comment_box.send_keys(comment_text)

            submit_button = self.driver.find_element(By.CSS_SELECTOR, "a.btn_register")
            submit_button.click()
            self.random_delay(2, 3)
            self.log(f"  - 성공한 댓글 : {comment_text}")
            self.log_comment_to_file(url, comment_text)

        except Exception as e:
            self.log(f"  - Error posting comment: {e}")

    def execute(self, cafe_url, board_id):
        """봇의 주요 프로세스를 실행합니다: 로그인 -> 카페 탐색 -> 게시글 조회 -> 댓글 작성."""
        # self.driver = webdriver.Chrome()
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        
        self.login_naver()
        if not self.is_running: return

        self.navigate_to_cafe(cafe_url, board_id)
        if not self.is_running: return

        posts = self.fetch_recent_posts(13)
        if not posts or not self.is_running:
            self.log("No posts found or stop signal received. Exiting.")
            return
            
        queries = [post["title"] for post in posts]
        self.log("Generating comments with OpenAI...")
        responses = self.assistant.get_answers(queries)
        self.log(f"Generated {len(responses)} comments.")

        if not self.is_running: return

        for i, post in enumerate(posts):
            if not self.is_running: break
            if i < len(responses):
                self.post_comment(post["link"], responses[i])
            else:
                self.log(f"Warning: No response generated for post '{post['title']}'.")

    def close(self):
        """브라우저를 종료합니다."""
        if self.driver:
            self.log("브라우저 종료!")
            self.driver.quit()
            self.driver = None


# 사용 예시
if __name__ == "__main__":
    login_id = "your login id"
    pw = "your password"
    cafe_url = "https://cafe.naver.com/directwedding"
    board_id = "menuLink113"  # 게시판 ID

    # 봇 초기화 및 실행
    bot = WeddingAssistantBot(login_id, pw)
    bot.execute(cafe_url, board_id)
    bot.close()
