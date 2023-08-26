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
from database import db_session,init_db
from models.user import Users

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
	
if __name__ == "__main__":
    init_db()
    app.run()


@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):

    get_or_create_user(event.source.user_id)
    profile = line_bot_api.get_profile(event.source.user_id)
    uid=profile.user_id
    message_text = str(event.message.text).lower()

    if message_text == '@使用說明':
        about_us_event(event)

        line_bot_api.reply_message(
            event.reply_token,TextSendMessage(text="HIHIHIHIIHHIIHHI")
        )
