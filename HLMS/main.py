from service import *
from common.HSession import HSession
from service.HMemberService import HMemberService
from service.HBoardService import HBoardService
from service.HScoreService import HScoreService
from flask import Flask
from web.routes import web_bp


def main():
    # 프로그램 시작용 코드
    HMemberService.load()

    run = True
    while run:
        print("""
        ==========================
         MBC 아카데미 관리 시스템
        ==========================
        1. 회원가입  2. 로그인 3. 로그아웃
        4. 회원관리  
        5. 게시판  6. 성적관리 7. 상품몰
        9. 종료
        """)
        member = HSession.login_member # None
        if member is None:
            print("현재 로그인 상태가 아닙니다.")
        else:
            print(f"{member.name}님 환영합니다.")

        sel = input(">>>")
        if sel == "1":
            print("회원가입 서비스로 진입합니다.")
            HMemberService.signup()
        elif sel == "2":
            print("로그인 서비스로 진입합니다.")
            HMemberService.login()
        elif sel == "3":
            print("로그아웃을 진행합니다.")
            HMemberService.logout()
        elif sel == "4":
            print("회원관리 서비스로 진입합니다.")
            HMemberService.modify()
        elif sel == "5":
            print("게시판관리 서비스로 진입합니다.")
            HBoardService.run()
        elif sel == "6":
            print("성적관리 서비스로 진입합니다.")
            HScoreService.run()
        elif sel == "7":
            print("관리자 서비스로 진입합니다.")
            HMemberService.admin()
        elif sel == "9":
            print("LMS 서비스를 종료합니다.")
            run = False


app = Flask(__name__)
app.secret_key = "secret-key"   # 세션용 (필수)

app.register_blueprint(web_bp)

if __name__ == "__main__":
    app.run(debug=True)
