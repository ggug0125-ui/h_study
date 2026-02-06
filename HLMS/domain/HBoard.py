class HBoard:
    def __init__(self, id, title,content, member_id, active=True,writer_name=None,writer_uid=None):
        self.id = id
        self.title = title
        self.content = content
        self.member_id = member_id
        self.active = active
        self.writer_name = writer_name
        self.writer_uid = writer_uid

    @classmethod
    def from_db(cls, row:dict):
        if not row:
            return None
        return cls(
            id = row.get('id'),
            title = row.get('title'),
            content = row.get('content'),
            member_id = row.get('member_id'),
            active = bool(row.get('active')),
            writer_name = row.get('name'),
            writer_uid = row.get('uid')
        )

    def __str__(self):
        writer = self.writer_name if self.writer_name else f'id:{self.member_id}'
        return f"{self.id:<4} | {self.title:<20} | {writer:<10}"