import datetime

status_dict = {
    'normal': '正常',
    'restricted': '受限',
    'disabled': '停用',
}
gender_dict = {
    'male': '男',
    'female': '女',
    None: '保密',
}

def calculate_age(birth):
    birth_d = birth
    today_d = datetime.date.today()
    birth_t = birth_d.replace(year=today_d.year)
    if today_d > birth_t:
        age = today_d.year - birth_d.year
    else:
        age = today_d.year - birth_d.year - 1
    return age

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]
