from sqlalchemy import Column,DateTime,String,func
from sqlalchemy.orm import relationship
from database import Base

class Users(Base):
    __tablename__='user'

    id = Column(String,primary_key=True)
    nick_name=Column(String)
    image_url=Column(String(length=256))
    created_time = Column(DateTime,default=func.now())

    orders = relationship('Orders',backref='user')