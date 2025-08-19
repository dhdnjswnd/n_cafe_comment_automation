from openai import OpenAI
import re


class WeddingAssistant:
    def __init__(self, additional_prompt=None):
        # OpenAI 클라이언트 초기화 및 API 키 설정은 환경변수로 세팅됨
        self.client = OpenAI()
        self.system_content = (
            "결혼준비토론방에서 게시글에 대해 답글을 다는 일반인인 척 하는 챗봇이야"
            "최대한 결혼을 준비하거나, 결혼한 사람 입장에서 댓글을 달아줘"
            "Don't use emoticons like this 😊🙂 and so on"
            "Don't use emojis like this 😊🙂 and so on"
            "For questions involving costs, time, or quantities, provide reasonable estimates."
            "Please provide output using only Basic Multilingual Plane (BMP) characters."
            "Please answer considering the wedding context, using 'wedding' only when essential."
            "Based on the above system prompt, please refer to the following system prompt when answering."
            "다음 규칙을 참고해서 답변해줘. 각 규칙의 우선순위는 없이 모두 동등하게 봐줘"
            "1. 선택지가 있는 경우 적절한 근거를 들어서 하나의 답변으로 말해주세요"
            "2. 의견을 묻는다면 적당히 답해주세요"
            "3. 답변의 길이를 50자 이내로 작성해줘"
            "4. title은 질문의 제목이고, content는 상세 내용이야. title 및 content를 모두 참고해서 답변해줘"
            "5. 제목에 vs라는 단어가 있는 경우 답을 제목에 있는 표현을 일부만 사용해서 답변해"
            "6. 내용에 링크url가 포함되어 있는 경우는 답변하지 않고 넘어가줘"
            "7. 내용을 왜곡하지 말고 합리적인 유추만 해서 답변해"
            
            "다음 예시를 참고해줘"
            "질문1 : title : 소개시켜준 친구 20 vs 30이상, content : 친구가 소개해줘서 결혼까지 하게 되었습니다. 소개시켜준 친구 어떻게 챙겨주는게 좋을까요?"
            "답변1 : 30이상 추천드립니다. 소중한 인연 만들어줬는데, 그정도는 써도 괜찮을 것 같아요"
            "질문2 : title : 본식 토요일 vs 일요일, content : 본식 날짜 다들 언제로 정하셨어요?"
            "답변2 : 손님이 멀리서 오셔서 토요일로 했어요"
            "질문3 : title : 웨촬 시 치아미백 한다 vs 안한다, content : 치아가 평소에 누런 편이라 컴플렉스여서 본식 때는 꼭 할 예정이거든요!\n근데 웨촬 때 하는 건 너무 오바인가.. 싶어서 여쭤봅니다!"
            "답변3 : 보정으로 가능할 것 같아서 따로 안했어요 ㅎㅎ"
            "질문4 : title : 결혼식 스몰웨딩 VS 가성비웨딩 VS 일반웨딩, content : 스몰웨딩이 돈 더 많이 든다고도 하고,저는 일반 보다 적게 쓰고싶어서다 갖추되 가성비 웨딩으로 했오요..!!"
            "답변4 : 저는 일반 웨딩으로 했어요. 양가부모님 설득 등 여러모로 편해서..ㅎㅎ"
            "질문5 : title : 본식후 바로 임신준비 vs 신혼 즐기다가 임신준비, content : 본식 치루고 바로 임신 준비 하시나요? 아니면 신혼을 즐기다가 슬슬 하시나요?"
            "답변5 : 자녀 계획 및 나이에 따라 다를 것 같아요. 둘 이상 생각 중이라면 바로 준비 ㄱㄱ"
            
            "용어 정리"
            "결토 : 결혼 토론방"
            "웨촬 : 웨딩 촬영"
            "가방순이 : 혼식에서 신부의 짐을 들어주고, 신부의 소지품을 관리하며, 축의금을 대신 받아주는 등 신부를 곁에서 보조하는 역할을 하는 사람을 뜻하는 신조어입니다. 주로 신부와 가장 가까운 친구나 자매가 맡는 경우가 많습니다"
        )
        if additional_prompt:
            self.system_content += f"\n{additional_prompt}"

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
        answers = [re.sub(r'^\d+\.\s*', '', answer.strip()) for answer in answers if answer.strip()]
        result = []
        for ans in answers:
            result.append(ans.replace("😊", ''))

        return result  # 각 답변의 앞뒤 공백 제거

if __name__ == "__main__":
    assistant = WeddingAssistant()
    result = assistant.get_answers(["{title:신행 스페인 포르투갈 vs 이탈리아 스위스, content : 신행으로 어디가 더 좋을까요?\n내년 5월 중순예정입니다.\n금액은 후자가 조금 더 나가는 것 같아요}",
                                    """{title:소개시켜준 친구 20 vs 30이상,content:안녕하세요!\n소개시켜준 친구는 제 초등학교부터 동창이자 남자친구의 고등학교 동창이에요 :)\n
                                    계기가 소개시켜준 친구한테 제 친구를 소개시켜줬어서 둘이 사겼었거든요 둘이 데이트 할 때 저를 부르길래 저도 친구 불러달라했구 그 때 만난 친구가 지금 남자친구에욥\n
                                    중간에 한 번 헤어졌었는데 다시 만나서 결혼하게 되었네요 ㅋㅋㅋ\n
                                    사실 소개팅이라기보다 겸사겸사 만나서 사귀게 된건데 이 친구가 내심 받고싶었는지 남자친구한테 '뭐해줄거냐 뭐 양복해준다는데 자기는 됐다' 라곤 했다는데.. \n
                                    진짜 됐으면 얘기 꺼내지도 않았을 것 같아서 준비를 하긴 해야될 것 같아 고민글 올립니다🥹 (제 친구랑 소개시켜준 친구는 헤어졌어요)\n
                                    여러분이라면 이 경우에 어떻게 챙겨줘야 하는게 맞는지 의견 부탁드립니닷 도와주세요 ㅠㅠ}"""
                                    ,"{title:신혼가전으로 밥솥 쿠쿠(6인용 이상) vs 소형(1~2인용) 구매, content: 당장 둘이사니까 작은걸로 한다?\n아니면 집들이나 가족이 늘어날 것을 생각해서 기본 밥솥을 구매한다?! 여러분들의 선택은?!}"
                                    ,"""{title : 11월 신혼여행지 스페인 vs 호주 어디가 좋을까요 !, content : 내년 11월에 결혼예정입니다 :)\n저는 여행을 워낙 좋아해서 자유여행으로 미리 준비하려고하는데요 !\n
                                    11월이면 스페인이든 호주든 날씨가 너무 좋고\n
                                    사그라다파밀리아 성당도 완공될거 같아서 두 나라가 고민이 되더라구요 !\n
                                    스페인을 가게 되면 포르투갈이랑 같이 갈거 같고\n
                                    호주는 시드니 + 멜버른을 갈거 같은데\n
                                    저랑 예비신랑 의견이 달라서 고민이 돼요 !\n
                                    11월에 호주나 스페인 가보신 분들 의견도 같이 공유 부탁드립니다 *.*"""])
    print(result)
