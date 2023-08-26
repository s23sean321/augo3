
from  sqlalchemy import Column,String,Integer
from linebot.models import *
from models.database import Base,db_session
from urllib.parse  import quote


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer,primary_key=True)
    name = Column(String)
    price = Column(Integer)
    description = Column(String)
    product_image_url = Column(String)


#列出所有的產品
    @staticmethod
    def list_all():
        products = db_session.query(Products).all()#抓取資料庫中所有產品的資料

        bubbles = []

        for product in products:
            bubble = BubbleContainer(
                hero=ImageComponent(
                    size='full',
                    aspect_ratio='20:13',
                    aspect_mode='cover',
                    url=product.product_image_url
                ),
                body=BoxComponent(
                    layout='vertical',
                    contents=[
                        TextComponent(text=product.name,#產品名稱
                                      wrap=True,
                                      weight='bold',
                                      size='xl'),
                        BoxComponent(#產品價格
                            layout='baseline',
                            contents=[#利用format的方法把product.price轉換成字串
                                TextComponent(text='NT${price}'.format(price=product.price),
                                              wrap=True,
                                              weight='bold',
                                              size='xl')
                            ]
                        ),
                        TextComponent(margin='md',#產品敘述 如果product.description or ''是空值的話就直接回傳空字串
                                      text='{des}'.format(des=product.description or ''),
                                      wrap=True,
                                      size='xs',
                                      color='#aaaaaa')
                    ],
                ),
                footer=BoxComponent(#購物車按鈕
                    layout='vertical',
                    spacing='sm',
                    contents=[
                        ButtonComponent(
                            style='primary',
                            color='#1DB446',
                            action=URIAction(label='Add to Cart',
                                             uri='line://oaMessage/{base_id}/?{message}'.format(base_id='@717eecic',
                                                                                                message=quote("{product}, I'd like to have:".format(product=product.name)))),
                        )
                    ]
                )
            )

            bubbles.append(bubble)

        carousel_container = CarouselContainer(contents=bubbles)

        message = FlexSendMessage(alt_text='products', contents=carousel_container)

        return message
