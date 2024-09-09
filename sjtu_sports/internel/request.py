import requests
import json
from time import time
from sjtu_sports.internel.encrypt import (aes_encrypt, rsa_encrypt)
from sjtu_sports.resources import pubkey
from sjtu_sports.utils import (get_key, get_timestamp_ms)

def _request(session, method, url, params=None, data=None):
    """Request with params.

    Easy to use requests and auto retry.

    Args:
        session: requests session, login session.
        method: string, 'POST' OR 'GET'.
        url: string, post url.
        params=None: dict, get param.
        data=None: dict, post param.

    Returns:
        response: response, text.
    """
    res = session.request(method, url, params=params, data=data)
    return res.text


def get_field_info(session, field_type, date, venue_id):
    """Get field info.

    Args:
        session: requests session, login session.
        field_type: string, field type. 
        date: string, date.
        venueId: string, venueId.

    Returns:
        list: field info list.
        err:  Exception.
    """
    url = "https://sports.sjtu.edu.cn/manage/fieldDetail/queryFieldSituation" 

    data = {
        'fieldType': field_type,
        'date': date,
        'venueId': venue_id
    }
    res = _request(session, 'POST', url, data=data)

    res = json.loads(res)
    if res['code'] != 0:
        return None, Exception(res['msg'])

    return res['data'], None
    

def confirm_order(session, order):
    """Confirm order.

    Args:
        session: requests session, login session.
        order: dict, order data.

    Returns:
        status:
        - 0, success.
        - 1, login expired.
        - 2, order failed.
        - 3, unknown error.
        err:  Exception.

    """
    url = 'https://sports.sjtu.edu.cn//venue/personal/ConfirmOrder'

    key = get_key()
    time = get_timestamp_ms()

    sid = rsa_encrypt(pubkey, key)
    tim = rsa_encrypt(pubkey, time)

    order_json = json.dumps(order, separators=(',', ':'))
    order_encrypted = aes_encrypt(key, order_json)

    headers = {
        'Sid': sid,
        'Tim': tim,
        'Content-Type': 'application/json;charset=UTF-8'
    }

    res = _request(session, 'POST', url, params=headers, data=order_encrypted)
    if "登录" in res:
        return 1, Exception("Login expired.")
    if "操作异常" in res:
        return 2, Exception("Order failed.")

    # parse as json
    try:
        res = json.loads(res)
    except:
        return 3, Exception("Unknown error.")

    if res['code'] != 0:
        return 2, Exception(res['msg'])
    
    return 0, None