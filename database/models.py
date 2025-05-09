from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class Store(Base):
    __tablename__ = 'stores'
    
    store_id = Column(String(255), primary_key=True)
    link = Column(String(255))
    
    giftcodes = relationship("GiftCode", back_populates="store")
    feedbacks = relationship("Feedback", back_populates="store")


class GiftCode(Base):
    __tablename__ = 'giftcode'
    
    code = Column(String(255), primary_key=True)
    store_id = Column(String(255), ForeignKey('stores.store_id'))
    isdelete = Column(Boolean, default=False)
    isvalid = Column(Boolean, default=False)
    issent = Column(Boolean, default=False)
    smsstatus = Column(Boolean, default=False)
    timestamp_ = Column(DateTime)

    store = relationship("Store", back_populates="giftcodes")

class Feedback(Base):
    __tablename__ = 'feedback_db'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    language = Column(String(50))
    nps = Column(Integer)
    first_visit = Column(String(50))
    satisfaction = Column(String(50))
    satisfaction_reason = Column(String(255))
    dissatisfaction_reason = Column(String(255))
    staff_reasons = Column(ARRAY(String))
    product_reasons = Column(ARRAY(String))
    ambience_reasons = Column(ARRAY(String))
    feedback = Column(Text)
    branch = Column(String(100))

    store_id = Column(String(255), ForeignKey('stores.store_id'))
    store = relationship("Store", back_populates="feedbacks")
    