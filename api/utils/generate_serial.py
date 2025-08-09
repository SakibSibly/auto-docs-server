import datetime
from ..models import CustomUser


def get_serial(user: CustomUser, doc_type: str) -> str:
    DOC_TYPE = "INVALID"
    if doc_type == "certificate":
        DOC_TYPE = "CRT"
    elif doc_type == "testimonial":
        DOC_TYPE = "TST"
    elif doc_type == "transcript":
        DOC_TYPE = "TRT"
    elif doc_type == "appeared":
        DOC_TYPE = "APR"
    

    UNI_CODE = str(user.department.faculty.university.code)
    DEPT_CODE = f"{int(user.department.code):02d}"
    STD_ID = str(user.student_id)[-2:]
    SESSION = user.session.split('-')[0][-2:]
    
    now = datetime.datetime.now()
    YEAR = f"{now.year % 100:02d}"
    MONTH = f"{now.month:02d}"
    DATE = f"{now.day:02d}"
    HOUR = f"{now.hour:02d}"
    SECOND = f"{now.second:02d}"

    return DOC_TYPE + UNI_CODE + DEPT_CODE + STD_ID + SESSION + YEAR + MONTH + DATE + HOUR + SECOND
    