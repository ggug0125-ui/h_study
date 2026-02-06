from common.HSession import HSession
from domain.HMember import HMember

class HMemberService:



    @staticmethod
    def add():
        print("\n[ 회원 추가 ]")
        uid = input("아이디: ")
        password = input("비밀번호: ")
        name = input("이름: ")

        member = HMember(uid, password, name)
        print("회원 등록 완료:", member)

    @classmethod
    def signup_web(cls, uid, password, name):
        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                # 중복 체크
                cursor.execute("SELECT id FROM members WHERE uid=%s", (uid,))
                if cursor.fetchone():
                    return False, "이미 존재하는 아이디입니다."

                sql = """
                    INSERT INTO members (uid, password, name, role)
                    VALUES (%s, %s, %s, 'user')
                """
                cursor.execute(sql, (uid, password, name))
                conn.commit()
                return True, "회원가입 성공"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @classmethod
    def login_web(cls, uid, pw):
        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM members WHERE uid = %s AND password = %s"
                cursor.execute(sql, (uid, pw))
                row = cursor.fetchone()

                if not row:
                    return False, "아이디 또는 비밀번호가 틀렸습니다."

                member = HMember.from_db(row)

                if not member.active:
                    return False, "비활성화된 계정입니다."

                HSession.login(member)
                return True, member

        except Exception as e:
            return False, str(e)
        finally:
            conn.close()

    @classmethod
    def load(cls):
        conn = HSession.get_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute("select count(*) as cnt from members")
                count = cursor.fetchone()['cnt']
                print(f"시스템에 현재 등록된 회원수는 {count}명 입니다. ")
        except : # 예외발생 문구
            print("MemberServie.load()메서드 오류발생....")

        finally: # 항상 출력되는 코드
            print("데이터베이스 접속 종료됨....")
            conn.close()

    @classmethod
    def login(cls):
        print("\n[로그인]")
        uid = input("아이디: ")
        password = input("비밀번호: ")

        conn = HSession.get_connection()

        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM members WHERE uid = %s AND password = %s"
                cursor.execute(sql, (uid, password))
                row = cursor.fetchone()

                if not row:
                    print("아이디 또는 비밀번호가 틀렸습니다.")
                    return

                member = HMember.from_db(row)

                if not member.active:
                    print("비활성화된 계정입니다. 관리자에게 문의하세요.")
                    return

                HSession.login(member)
                print(f"{member.name}님 로그인 성공 ({member.role})")

        except Exception as e:
            print("로그인 처리 중 오류 발생")
            print(e)
        finally:
            conn.close()

    @classmethod
    def logout(cls):
        # 1. 먼저 세션에 로그인 정보가 있는지 확인
        if not HSession.is_login():
            print("\n[알림] 현재 로그인 상태가 아닙니다.")
            return

        # 2. 세션의 로그인 정보 삭제
        HSession.logout()
        print("\n[성공] 로그아웃 되었습니다. 안녕히 가세요!")

    @classmethod
    def signup(cls):
        print("\n[회원가입]")
        uid = input("아이디: ")

        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 중복 체크
                check_sql = "SELECT id FROM members WHERE uid = %s"
                cursor.execute(check_sql, (uid,))

                if cursor.fetchone():
                    print("이미 존재하는 아이디입니다.")
                    return

                password = input("비밀번호: ")
                name = input("이름: ")

                # 2. 데이터 삽입
                insert_sql = "INSERT INTO members (uid, password, name) VALUES (%s, %s, %s)"
                cursor.execute(insert_sql, (uid, password, name))
                conn.commit()
                print("회원가입 완료! 로그인해 주세요.")
        except Exception as e:
            conn.rollback()
            # 트랜젝션 : with안쪽에 2개이상의 sql문이 둘다 true일때는 commit()
            #                    2중 한개라도 오류가 발생하면 rollback()
            print(f"회원가입 오류: {e}")
        finally:
            conn.close()

    @classmethod
    def signup_web(cls, name, email, password):
        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO members (name, email, password) VALUES (%s, %s, %s)"
                cursor.execute(sql, (name, email, password))
                conn.commit()
                return True, "성공"
        except Exception as e:
            conn.rollback()
            return False, str(e)
        finally:
            conn.close()

    @classmethod
    def modify(cls):  # 회원 수정 메서드
        if not HSession.is_login():
            print("로그인 후 이용 가능합니다.")
            return

        member = HSession.login_member
        print(f"내정보확인 : {member}")  # Member.__str__()
        print("\n[내 정보 수정]\n1. 이름 변경  2. 비밀번호 변경 3. 계정비활성 및 탈퇴 0. 취소")
        sel = input("선택: ")

        new_name = member.name
        new_password = member.password

        if sel == "1":
            new_name = input("새 이름: ")
        elif sel == "2":
            new_password = input("새 비밀번호: ")
        elif sel == "3":
            print("회원 중지 및 탈퇴를 진행합니다.")
            cls.delete()
        else:
            return

        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "UPDATE members SET name = %s, password = %s WHERE id = %s"
                cursor.execute(sql, (new_name, new_password, member.id))
                conn.commit()

                # 메모리(세션) 정보도 동기화
                member.name = new_name
                member.password = new_password
                print("정보 수정 완료")
        finally:
            conn.close()

    @classmethod
    def delete(cls):
        if not HSession.is_login(): return
        member = HSession.login_member

        print("\n[회원 탈퇴]\n1. 완전 탈퇴  2. 계정 비활성화")
        sel = input("선택: ")

        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                if sel == "1":
                    sql = "DELETE FROM members WHERE id = %s"
                    cursor.execute(sql, (member.id,))
                    print("회원 탈퇴 완료")
                elif sel == "2":
                    sql = "UPDATE members SET active = FALSE WHERE id = %s"
                    cursor.execute(sql, (member.id,))
                    print("계정 비활성화 완료")

                conn.commit()
                HSession.logout()
        finally:
            conn.close()

    @classmethod
    def admin(cls):
        if not HSession.is_login():
            print("로그인 필요")
            return

        if not HSession.is_admin():
            print("관리자 권한 필요")
            return
        member = HSession.login_member
        while True:
            print("""
            [ 관 리 자 메 뉴 ]
    1. 회원 목록 조회
    2. 권한 변경
    3. 블랙리스트 처리
    0. 뒤로가기
    """)
            sel = input("선택 번호 : ")
            if sel == "1":
                cls.list_member()
            elif sel == "2":
                cls.change_role()
            elif sel == "3":
                cls.block_member()
            elif sel == "0":
                break

    @classmethod
    def list_member(cls):
        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM members"
                cursor.execute(sql)
                rows = cursor.fetchall()

                print("\n[ 회원 목록 ]")
                for row in rows:
                    member = HMember.from_db(row)
                    print(member)
        finally:
            conn.close()

    @classmethod
    def change_role(cls):
        cls.list_member()
        uid = input("대상아이디: ")


    @classmethod
    def block_member(cls):
        pass
