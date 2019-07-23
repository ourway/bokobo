from sqlalchemy.dialects.postgresql import UUID,ENUM
from sqlalchemy import  Column, ForeignKey, Float

from db_session import Base, PrimaryModel
from accounts.models import Account

class Transaction(Base,PrimaryModel):

    __tablename__ = 'transactions'

    account_id = Column(UUID, ForeignKey(Account.id),nullable=False)
    credit = Column(Float, default=0.00)
    debit = Column(Float, default=0.00)

