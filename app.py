from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage,StickerSendMessage,FollowEvent,UnfollowEvent,
)
from linebot.models import *
from models.database import db_session,init_db
from models.user import Users

from models.product import Products
from models.cart import Cart

app = Flask(__name__)


line_bot_api = LineBotApi('72hT6u6TdhRodoEY9uScdlS/vHkheb9tkUjiKrVbSFszK/W4JsvKDzTKLtFbazt2FfJaByplh0qyvpxgJpyaGnTx2vNU+uDt0o8MTv4nSQdIH+1Swz0fsqUoetC15H/v8y6IjX2sekdiYbLCfXU80QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('73e77743813aa99f6508e667d0cce181')


app = Flask(__name__)

#建立或取得user
def get_or_create_user(user_id):
    #從id=user_id先搜尋有沒有這個user，如果有的話就會直接跳到return
    user = db_session.query(Users).filter_by(id=user_id).first()
    #沒有的話就會透過line_bot_api來取得用戶資訊
    if not user:
        profile = line_bot_api.get_profile(user_id)
        #然後再建立user並且存入到資料庫當中
        user = Users(id=user_id, nick_name=profile.display_name, image_url=profile.picture_url)
        db_session.add(user)
        db_session.commit()

    return user

def about_us_event(event):
    emoji = [
            {
                "index": 0,
                "productId": "5ac21184040ab15980c9b43a",
                "emojiId": "225"
            },
            {
                "index": 17,
                "productId": "5ac21184040ab15980c9b43a",
                "emojiId": "225"
            }
        ]

    text_message = TextSendMessage(text='''$ Master RenderP $
Hello! 您好，歡迎您成為 Master RenderP 的好友！

我是Master 支付小幫手 

-這裡有商城，還可以購物喔~
-直接點選下方【圖中】選單功能

-期待您的光臨！''', emojis=emoji)

    sticker_message = StickerSendMessage(
        package_id='8522',
        sticker_id='16581271'
    )
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, sticker_message])
    
# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
	



@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):

    get_or_create_user(event.source.user_id)
    cart = Cart(user_id=event.source.user_id)

    message_text = str(event.message.text).lower()

    if message_text == '@使用說明':
        about_us_event(event)
    elif message_text == '我想訂購商品':
        message = Products.list_all()
    elif "I'd like to have:" in message_text:
            product_name=message_text.split(',')[0]
            num_item = message_text.rsplit(':')[1]
            product = db_session.query(Products).filter(Products.name.ilike(product_name)).first()
            if product:

                cart.add(product=product_name, num=num_item)
                #然後利用confirm_template的格式詢問用戶是否還要加入？
                confirm_template = ConfirmTemplate(
                    text='Sure, {} {}, anything else?'.format(num_item, product_name),
                    actions=[
                        MessageAction(label='Add', text='add'),
                        MessageAction(label="That's it", text="That's it")
                    ])

                message = TemplateSendMessage(alt_text='anything else?', template=confirm_template)
            else:
                message = TextSendMessage(text= "Sorry ,We don't havev {}.".format(product_name))
            print(cart.bucket())
    elif message_text in ['my cart','cart',"that's it"]:

        if cart.bucket():
            message = cart.display()
        else:
            message =TextSendMessage(text='your cart is empty now')
    if message:
        line_bot_api.reply_message(
            event.reply_token,message
        )






#初始化產品資訊
@app.before_first_request
def init_products():
    # init db
    result = init_db()#先判斷資料庫有沒有建立，如果還沒建立就會進行下面的動作初始化產品
    if result:
        init_data = [Products(name='打拋雞肉',
                              product_image_url='https://i.imgur.com/6Jrc4NX.jpg',
                              price=100,
                              description='爆香蒜及辣椒，加入碎雞肉拌炒，以小蕃茄及九層塔快拌輔味'),
                     Products(name='黑胡椒豬肉',
                              product_image_url='https://i.imgur.com/OO3EM1P.jpg',
                              price=100,
                              description='醬油醃製豬肉拌炒洋蔥，以黑胡椒粒提香增辣，豐富你味蕾的一刻'),
                     Products(name='蔬菜套餐',
                              price=80,
                              product_image_url='https://i.imgur.com/zo59nEc.jpg',
                              description='燙青菜、低油低鹽調味，清淡的一餐不造成任何負擔'),
                     Products(name='松阪豬肉',
                              price=130,
                              product_image_url='https://i.imgur.com/LYZRbcR.jpg',
                              description='使用氣炸鍋將肉質自身油脂逼出，原味、天然、就是這樣有嚼勁')]
        db_session.bulk_save_objects(init_data)#透過這個方法一次儲存list中的產品
        db_session.commit()#最後commit()才會存進資料庫
        #記得要from models.product import Products在app.py
        

if __name__ == "__main__":
    init_products()
    app.run()
