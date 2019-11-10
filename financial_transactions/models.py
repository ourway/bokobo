from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from db_session import Base, PrimaryModel
from accounts.models import Account
from payment.models import Payment


class Transaction(Base,PrimaryModel):

    __tablename__ = 'transactions'

    account_id = Column(UUID, ForeignKey(Account.id),nullable=False)
    credit = Column(Float, default=0.00)
    debit = Column(Float, default=0.00)
    payment_id = Column(UUID,ForeignKey(Payment.id))
    details = Column(JSON)

    # payment = relationship(Payment, primaryjoin=payment_id == Payment.id)

