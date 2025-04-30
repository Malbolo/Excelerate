# from sqlalchemy.orm import Session
# from models.email_model import Email
#
#
# def create_email(db: Session, recipient_email: str, subject: str, message: str, error_message: str = None):
#     db_email = Email(
#         recipient_email=recipient_email,
#         subject=subject,
#         message=message,
#         error_message=error_message
#     )
#     db.add(db_email)
#     db.commit()
#     db.refresh(db_email)
#     return db_email
