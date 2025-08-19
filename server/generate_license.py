import sqlite3
import uuid
import argparse

DB_FILE = "licenses.db"

def create_license(email: str, limit: int):
    """새로운 라이선스 키를 생성하고 데이터베이스에 추가합니다."""
    new_key = str(uuid.uuid4())
    
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        
        # 데이터베이스에 새 키와 이메일 삽입
        cur.execute(
            "INSERT INTO licenses (key, api_call_limit, email) VALUES (?, ?, ?)",
            (new_key, limit, email)
        )
        con.commit()
        
        print("\n새로운 라이선스 키가 성공적으로 생성되었습니다!")
        print("="*50)
        print(f"  발급 대상: {email}")
        print(f"  라이선스 키: {new_key}")
        print(f"  횟수 제한: {limit}회/일")
        print("="*50)
        
    except sqlite3.IntegrityError:
        print("오류: 중복된 키가 생성되었습니다. 다시 시도해주세요.")
    except Exception as e:
        print(f"데이터베이스 작업 중 오류가 발생했습니다: {e}")
    finally:
        if con:
            con.close()

def main():
    # --- 데이터베이스 및 테이블 존재 여부 확인 ---
    try:
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='licenses';")
        if cur.fetchone() is None:
            print(f"오류: '{DB_FILE}' 데이터베이스에 'licenses' 테이블이 없습니다.")
            print("먼저 server.py를 한 번 실행하여 데이터베이스를 생성해주세요.")
            return
    except Exception as e:
        print(f"데이터베이스 연결 중 오류 발생: {e}")
        return
    finally:
        if con:
            con.close()

    parser = argparse.ArgumentParser(description="새로운 라이선스 키를 생성합니다.")
    parser.add_argument(
        '--email',
        type=str,
        required=True,
        help='라이선스를 발급할 사용자의 이메일 주소 (필수)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='일일 API 호출 최대 횟수를 지정합니다. (기본값: 100)'
    )
    args = parser.parse_args()

    create_license(args.email, args.limit)

if __name__ == "__main__":
    main()
