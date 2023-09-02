import json
import requests
from flask import url_for
from config import Config


#PAY_API_URL = 'https://api-pay.line.me/v2/payments/request'#官方
PAY_API_URL = 'https://sandbox-api-pay.line.me/v2/payments/request'#測試
CONFIRM_API_URL = 'https://sandbox-api-pay.line.me/v2/payments/{}/confirm'#測試
#CONFIRM_API_URL = 'https://api-pay.line.me/v2/payments/{}/confirm'#官方

class LinePay():

    def __init__(self, currency='TWD'):
        self.channel_id = Config.LINE_PAY_ID #直接設定在設定檔中，記得到Config中去設定
        self.secret = Config.LINE_PAY_SECRET #直接設定在設定檔中
        self.redirect_url = url_for('.confirm',#到app.py去加入confirm這個function，放在callback上面
                                    _external=True,
                                    _scheme='https')
        self.currency = currency
    # 透過裝飾器@app.route()可以定義路由，使用者可以利用該路由來訪問網頁
    # 現在有一個問題在於如果今天程式都寫死路由，一但路由有所變更，那就必需對所有的專案開始搜尋，然後一起修正路由，
    # 對吧!所以在flask有個方式可以避免這個問題，就是透過url_for，這是flask內建的函數，可以從flask直接導入
    # from flask import url_for
    def _headers(self, **kwargs):#會自動帶入那三個設定
        return {**{'Content-Type': 'application/json',
                   'X-LINE-ChannelId': self.channel_id,
                   'X-LINE-ChannelSecret': self.secret},
                **kwargs}

    def pay(self, product_name, amount, order_id, product_image_url=None):
        data = {#pay方法用字典帶入我們所需要的值
            'productName': product_name,
            'amount': amount,
            'currency': self.currency,
            'confirmUrl': self.redirect_url,
            'orderId': order_id,
            'productImageUrl': product_image_url
        }
        #把上面資料轉換成json格式並帶入headers，利用post方法送出資料
        # PAY_API_URL對應到第8行
        response = requests.post(PAY_API_URL, headers=self._headers(), data=json.dumps(data).encode('utf-8'))
        #response就是line的回應
        return self._check_response(response)#取得回應後透過_check_response確認

    def confirm(self, transaction_id, amount):#首先會接收transaction_id, amount
        data = json.dumps({#接著把這些資料轉成json格式
            'amount': amount,
            'currency': self.currency
        }).encode('utf-8')
        # CONFIRM_API_URL對應到第9行
        response = requests.post(CONFIRM_API_URL.format(transaction_id), headers=self._headers(), data=data)
        return self._check_response(response)

    def _check_response(self, response):
        res_json = response.json()

        if 200 <= response.status_code < 300:
            if res_json['returnCode'] == '0000':#確認狀態為0000再return res_json['info']
                return res_json['info']
        #裡面的資料包含有付款的URL & transaction_id
        raise Exception('{}:{}'.format(res_json['returnCode'], res_json['returnMessage']))