
from  sqlalchemy import Column,String,Integer
from linebot.models import *
from models.database import Base,db_session

class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    product_image_url = Column(String)