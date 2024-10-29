from openai import OpenAI
import re


class WeddingAssistant:
    def __init__(self):
        # OpenAI 클라이언트 초기화 및 API 키 설정
        self.client = OpenAI()
        self.system_content = (
            "You are an assistant answering wedding-related questions. "
            "Respond in Korean with each answer between 30 to 100 characters, in a polite tone using phrases like '~인 "
            "것 같아요~' or '~습니다.' or '~같아요' where appropriate."
            "Include suitable emoticons like ㅎㅎ or ㅜㅜ."
            "For questions involving costs, time, or quantities, provide reasonable estimates."
            "please use just characters in the BMP(Session info: chrome=130.0.6723.70)"
        )

    def get_answers(self, questions):
        # 질문을 번호와 함께 정리
        numbered_questions = "\n".join([f"{i + 1}. {q}" for i, q in enumerate(questions)])

        # API 호출
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": numbered_questions}
            ]
        )

        # 응답을 줄바꿈 기준으로 분할하여 리스트 생성
        answer_text = completion.choices[0].message.content
        answers = answer_text.split("\n")
        answers = [re.sub(r'^\d+\.\s*', '', answer.strip()) for answer in answers]

        return [answer.strip() for answer in answers]  # 각 답변의 앞뒤 공백 제거
