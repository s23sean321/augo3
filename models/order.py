from sqlalchemy import Column,DateTime,String,Integer,func,Boolean,ForeignKey
from sqlalchemy.orm import relationship
from linebot.models import *
from database import Base


class Orders(Base):
    __tablename__ = 'orders'

    id = Column(String,primary_key=True)

    amount = Column(Integer)

    transaction_id = Column(String)
    is_pay = Column(Boolean,default=False)
    created_time = Column(DateTime,default=func.now())
    user_id = Column("user_id",ForeignKey("user.id"))
    items = relationship('Items',backref="order")

def display_receipt(self):
        item_box_component = []

        for item in self.items:#透過self.items取得訂單明細項目
            item_box_component.append(BoxComponent(
                layout='horizontal',
                contents=[#透過TextComponent顯示明細資料 text='{quantity} x {product_name}數量/產品名稱
                    TextComponent(text='{quantity} x {product_name}'.
                                  format(quantity=item.quantity,
                                         product_name=item.product_name),
                                  size='sm',
                                  color='#555555',
                                  flex=0),#text='NT${amount}'金額 
                    TextComponent(text='NT${amount}'.
                                  format(amount=(item.quantity * item.product_price)),
                                  size='sm',
                                  color='#111111',
                                  align='end')]
            ))
        #產生資料後就append到item_box_component等等會用到
        #透過BubbleContainer產生收據格式
        bubble = BubbleContainer(
            direction='ltr',
            body=BoxComponent(
                layout='vertical',
                contents=[
                    TextComponent(text='RECEIPT',
                                  weight='bold',
                                  color='#1DB446',
                                  size='sm'),
                    TextComponent(text='LSTORE',
                                  weight='bold',
                                  size='xxl',
                                  margin='md'),
                    TextComponent(text='Online Store',
                                  size='xs',
                                  color='#aaaaaa',
                                  wrap=True),
                    SeparatorComponent(margin='xxl'),
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=item_box_component#透過for迴圈產生的訂單明細
                    ),
                    SeparatorComponent(margin='xxl'),#分隔線
                    BoxComponent(
                        layout='vertical',
                        margin='xxl',
                        spacing='sm',
                        contents=[
                            BoxComponent(
                                layout='horizontal',
                                contents=[#顯示總金額
                                    TextComponent(text='TOTAL',
                                                  size='sm',
                                                  color='#555555',
                                                  flex=0),
                                    TextComponent(text='NT${total}'.
                                                  format(total=self.amount),
                                                  size='sm',
                                                  color='#111111',
                                                  align='end')]
                            )

                        ]
                    )
                ],
            )
        )

        message = FlexSendMessage(alt_text='receipt', contents=bubble)

        return message#return回給app.py裡的 confirm()這裡message = order.display_receipt()再push給user

