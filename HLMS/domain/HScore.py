class HScore:
    def __init__(self, member_id, kor, eng, math, id= None):
        self.member_id = member_id
        self.kor = kor
        self.eng = eng
        self.math = math
    @property
    def total(self):
        return self.kor + self.eng + self.math
    @property
    def avg(self):
        return round((self.total)/3,2) # 소수점 2자리까지
    @property
    def grade(self):
        avg = self.avg
        if avg >= 90:
            return 'A'
        elif avg >= 80:
            return 'B'
        elif avg >= 70:
            return 'C'
        else:
            return 'F'

    @classmethod
    def from_db(cls, row: dict):
        """DB 딕셔너리에서 member_id 기반으로 객체 생성"""
        if not row:
            return None

        return cls(
            id=row.get('id'),
            member_id=row.get('member_id'),  # uid 대신 member_id 사용
            kor=int(row.get('korean', 0)),
            eng=int(row.get('english', 0)),
            math=int(row.get('math', 0))
        )
