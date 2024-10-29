# 샘플 Python 스크립트입니다.
# Shift+F10을(를) 눌러 실행하거나 내 코드로 바꿉니다.
# 클래스, 파일, 도구 창, 액션 및 설정을 어디서나 검색하려면 Shift 두 번을(를) 누릅니다.
import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from naverCafe_Openai import WeddingAssistant


class WeddingAssistantBot:
    """WeddingAssistantBot은 Naver 카페에서 글을 가져와 댓글을 작성하는 자동화 봇입니다."""

    def __init__(self, login_id, pw):
        self.driver = webdriver.Chrome()  # WebDriver 초기화
        self.login_id = login_id
        self.pw = pw
        self.assistant = WeddingAssistant()

    def random_delay(self, min_delay=1, max_delay=3):
        """랜덤 딜레이를 주어 자동화 탐지를 피합니다."""
        time.sleep(random.uniform(min_delay, max_delay))

    def login_naver(self):
        """네이버 로그인 페이지에 접속하고, ID와 PW를 입력하여 로그인합니다."""
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

    def navigate_to_cafe(self, cafe_url, board_id):
        """카페 URL과 게시판 ID를 사용해 카페 특정 게시판으로 이동합니다."""
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

        # iframe으로 전환
        self.switch_to_iframe("iframe#cafe_main")

    def switch_to_iframe(self, iframe_selector):
        """특정 iframe으로 전환합니다."""
        iframe = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, iframe_selector)))
        self.driver.switch_to.frame(iframe)

    def fetch_recent_posts(self, count=10):
        """최근 게시글의 제목과 링크를 가져옵니다."""
        posts = []
        for n in range(1, count + 1):
            try:
                # 동적으로 CSS Selector를 생성하여 제목 및 링크 가져오기
                selector = f"#main-area > div:nth-child(4) > table > tbody > tr:nth-child({n}) > td.td_article > div.board-list > div > a"
                a_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                posts.append({
                    "title": a_element.text,
                    "link": a_element.get_attribute("href")
                })
            except Exception as e:
                print(f"Error fetching post {n}: {e}")
        return posts

    def post_comment(self, url, comment_text):
        """특정 URL 게시글에 댓글을 작성합니다."""
        self.driver.get(url)
        self.random_delay(1, 2)
        self.switch_to_iframe("iframe#cafe_main")

        try:
            # 댓글 입력 창 찾기
            comment_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                "#app > div > div > div.ArticleContentBox > div.article_container > "
                                                "div.CommentBox > div.CommentWriter > div.comment_inbox > textarea"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", comment_box)
            self.random_delay(1, 2)

            # 댓글 입력
            comment_box.send_keys(comment_text)

            # 제출 버튼 클릭
            submit_button = self.driver.find_element(By.CSS_SELECTOR,
                                                     "#app > div > div > div.ArticleContentBox > "
                                                     "div.article_container >"
                                                     "div.CommentBox > div.CommentWriter > div.comment_attach > "
                                                     "div.register_box > a")
            submit_button.click()
            self.random_delay(2, 3)
            print(f"Comment posted on URL {url}: {comment_text}")
        except Exception as e:
            print(f"Error posting comment on {url}: {e}")

    def execute(self, cafe_url, board_id):
        """봇의 주요 프로세스를 실행합니다: 로그인 -> 카페 탐색 -> 게시글 조회 -> 댓글 작성."""
        self.login_naver()
        self.navigate_to_cafe(cafe_url, board_id)

        # 게시글 제목을 질문으로 전송하여 답변 생성
        posts = self.fetch_recent_posts()
        queries = [post["title"] for post in posts]
        responses = self.assistant.get_answers(queries)

        print(responses)

        # 각 게시글에 댓글 작성
        for i, post in enumerate(posts):
            self.post_comment(post["link"], responses[i])

    def close(self):
        """브라우저를 종료합니다."""
        time.sleep(100)
        self.driver.quit()


# 사용 예시
if __name__ == "__main__":
    login_id = ""
    pw = ""
    cafe_url = "https://cafe.naver.com/directwedding"
    board_id = "menuLink113"  # 게시판 ID

    # 봇 초기화 및 실행
    bot = WeddingAssistantBot(login_id, pw)
    bot.execute(cafe_url, board_id)
    bot.close()
