from common import HSession



class HScoreService:
    @classmethod
    def load(cls):
        conn = HSession.get_connection()
        #세션객체에 있는 db연결 메서드를 실행하고 conn변수에 넣음
        try:
            with conn.cursor() as cursor:
                #커서 객체는 db연결 성공시 연결정보를 가지고 있음
                cursor.execute("SELECT COUNT(*) AS cnt FROM scores")
                #sql문 실행
                count = cursor.fetchone()['cnt']
                # 실행결과를 1개 가져와 count변수에 넣음
                print(f"시스템:현재 등록된 성적수는 {count}개 입니다.")
        except:
            print("ScoreService.load()실행오류 발생!!!!!")
        finally:
            conn.close()

    @classmethod
    def run(cls):
        cls.load()    # 읽어오기
        if not HSession.is_login():
            print("로그인후 이용하세요")
            return
        member = HSession.login_member
        while True:
            print("\n=======성적관리시스템========")
            if member.role in ("manager","admin"):
                print("1 학생 성적 입력/ 수정")
            #2. 공통메뉴
            print("2. 내성적 조회")
            #3.관리자 전용메뉴
            if member.role == "admin":
                print("3.전체성적현황(join)")

            print("0.뒤로가기")
            sel = input(">>>")
            if sel == "1" and member.role in ("manager","admin"):
                cls.add_score()
            elif sel == "2":
                cls.view_my_score()
            elif sel == "3" and member.role == "admin":
                cls.view_all()
            elif sel == "0":
                break

    @classmethod
    def add_score(cls):
        target_uid = input("성적 입력할 학생 아이디(uid): ")
        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 학생 존재 확인
                cursor.execute("SELECT id, name FROM members WHERE uid = %s", (target_uid,))
                student = cursor.fetchone()

                if not student:
                    print(f"'{target_uid}' 학생을 찾을 수 없습니다.")
                    return

                # 2. 점수 입력
                kor = int(input("국어: "))
                eng = int(input("영어: "))
                math = int(input("수학: "))

                # 3. Score 객체를 생성 (여기서 파이썬의 @property가 계산됨)
                temp_score = Score(member_id=student['id'], kor=kor, eng=eng, math=math)

                print(f"입력 평균: {temp_score.avg}")

                # 4. DB 저장 (객체의 프로퍼티 값을 SQL에 전달)
                cursor.execute("SELECT id FROM scores WHERE member_id = %s", (student['id'],))

                if cursor.fetchone():
                    # UPDATE 로직  # 성적이 있으면 업데이트
                    sql = """
                              UPDATE scores \
                              SET korean=%s, \
                                  english=%s, \
                                  math=%s, \
                                  total=%s, \
                                  avgrage=%s, \
                                  grade=%s
                              WHERE member_id = %s \
                              """
                    # 객체의 프로퍼티(temp_score.total 등)를 사용합니다.
                    cursor.execute(sql, (
                        temp_score.kor, temp_score.eng, temp_score.math,
                        temp_score.total, temp_score.avg, temp_score.grade,
                        student['id']
                    ))
                else:
                    # INSERT 로직 # 성적이 없으면 생성하기
                    sql = """
                              INSERT INTO scores (member_id, korean, english, math, total, avgrage, grade)
                              VALUES (%s, %s, %s, %s, %s, %s, %s) \
                              """
                    cursor.execute(sql, (
                        student['id'], temp_score.kor, temp_score.eng, temp_score.math,
                        temp_score.total, temp_score.avg, temp_score.grade
                    ))

                conn.commit() # 디비에 저장
                print(f"{student['name']} 학생의 성적 저장 완료 (객체 계산 방식)")
        finally:
            conn.close()

    @classmethod
    def view_my_score(cls):  # 내 성적 조회    ## 조인하지 않고 하는 방법
        member = HSession.login_member  # 로그인한 멤버 객체
        conn = HSession.get_connection()  # 디비 연결 객체
        try:
            with conn.cursor() as cursor:  # 연결 성공시 참
                # 로그인한 사람의 PK(id)로 성적 조회
                sql = "SELECT * FROM scores WHERE member_id = %s"  # 세션에 있는 멤버아이디를 넣는다 s에
                cursor.execute(sql, (member.id,))  # id 는 번호자동생성 숫자로 입력되는거야
                data = cursor.fetchone()  # 멤버에 디비정보가 담김

                if data:  # 데이터가 있으면
                    s = Score.from_db(data)  # 딕셔너리 타입의 객체를 S에 넣음 # 점수를 S에 넣음
                    # 도메인 클래스의 __init__에는 uid 정보가 없으므로 세션 정보를 활용해 출력
                    cls.print_score(s, member.uid)  # 콘솔에 보기 좋게 출력하려고 만듬
                else:
                    print("등록된 성적이 없습니다.")
        finally:
            conn.close()

    @classmethod
    def print_score(cls, s, uid): # 개인성적출력, 전체 성적 출력도 가능(메서드 : 동작->재활용가능)
        # 도메인 모델(Score)에 계산 로직(@property)이 있으므로 s.total, s.avg 등을 그대로 사용
        print(
            f"ID:{uid:<10} | "
            f"국어:{s.kor:>3} 영어:{s.eng:>3} 수학:{s.math:>3} | "
            f"총점:{s.total:>3} 평균:{s.avg:>5.2f} | 등급 : {s.grade}"
        )

    @classmethod
    def view_all(cls):
        print("\n[전체 성적 목록 - join결과]")
        conn = HSession.get_connection()
        try:
            with conn.cursor() as cursor:
                #member 와 scores를 조인하여 아이디(uid)와 성적을 함께 가져옴
                sql = """
                        SELECT m.uid, s.* \
                        FROM scores s \
                        JOIN members m ON s.member_id = m.id \
                        """
                cursor.execute(sql)
                datas = cursor.fetchall()  # all 은 모든값
                for data in datas:
                    s = Score.from_db(data) # 딕셔너리 타입을 객체로 만든거
                    cls.print_score(s, data['uid']) # 출력용 메서드에 주입한거
        finally:
            conn.close()

    @staticmethod
    def print_score(s, display_uid):
        # 도메인 모델(Score)에 계산 로직(@property)이 있으므로 s.total, s.avg 등을 그대로 사용
        print(
            f"ID:{display_uid:<10} | "
            f"국어:{s.kor:>3} 영어:{s.eng:>3} 수학:{s.math:>3} | "
            f"총점:{s.total:>3} 평균:{s.avg:>5.2f} | 등급 : {s.grade}"
        )