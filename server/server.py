import os
import sqlite3
import uvicorn
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from datetime import date

# --- Configuration ---
# 서버의 OpenAI API 키를 환경 변수에서 불러옵니다.
# 이 키는 클라이언트가 아닌 서버만 알고 있습니다.
# 터미널에서 'set OPENAI_API_KEY=your_key' 와 같이 설정해야 합니다.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("경고: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    # raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

DB_FILE = "licenses.db"

# --- Pydantic Models for Request/Response ---
class CommentRequest(BaseModel):
    """클라이언트가 댓글 생성을 요청할 때 보내는 데이터 모델"""
    license_key: str
    post_title: str
    post_content: str
    additional_prompt: str | None = None

class CommentResponse(BaseModel):
    """서버가 클라이언트에게 반환하는 데이터 모델"""
    comment: str | None = None
    error: str | None = None

class LicenseRequest(BaseModel):
    """라이선스 생성을 요청할 때 필요한 데이터 모델"""
    email: str
    api_call_limit: int = 100

class LicenseResponse(BaseModel):
    """라이선스 생성 후 반환되는 데이터 모델"""
    license_key: str
    email: str
    message: str


# --- Database Functions ---
def init_db():
    """서버 시작 시 데이터베이스와 테이블을 초기화합니다."""
    con = sqlite3.connect(DB_FILE)
    cur = con.cursor()
    # 라이선스 정보를 저장할 테이블 생성 (email 컬럼 추가)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS licenses (
            key TEXT PRIMARY KEY,
            api_calls_made INTEGER DEFAULT 0,
            api_call_limit INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT 1,
            last_call_date TEXT,
            email TEXT UNIQUE
        )
    """)
    con.commit()
    con.close()