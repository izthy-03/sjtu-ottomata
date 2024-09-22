import requests
import json
from time import time

from sjtu_sports.internel.encrypt import (aes_encrypt, rsa_encrypt)
from sjtu_sports.resources import pubkey
from sjtu_sports.utils import (get_key, get_timestamp_ms)
from sjtu_sports.utils.error import *


def _request(session: requests.Session, method, url, headers=None, data=None, json=None):
    """Request with params.

    Internel request function.

    Args:
        session: requests session, login session.
        method: string, 'POST' OR 'GET'.
        url: string, post url.
        headers=None: dict, get header.
        data=None: dict, post param.

    Returns:
        response: response, text.
    """
    if method not in ['POST', 'GET']:
        raise OttoError(ErrorCode_kMethodNotAllowed, "Method not allowed.")
    if not session:
        raise OttoError(ErrorCode_kInvalidSession, "Invalid session.")

    res = session.request(method, url, headers=headers, data=data, json=json)

    return res.text


def get_field_info(session, field_type_id, date, venue_id):
    """Get field info.

    Args:
        session: requests session, login session.
        field_type_id: string, field type id.
        date: string, date. e.g. '2021-09-01'.
        venue_id: string, venueId.

    Returns:
        list: field info list.
    
    Raises:
        OttoError: error.
    """
    url = "https://sports.sjtu.edu.cn/manage/fieldDetail/queryFieldSituation" 

    jsons = {
        'fieldType': field_type_id,
        'date': date,
        'venueId': venue_id
    }
    res = _request(session, 'POST', url, json=jsons)

    res = json.loads(res)
    if res['code'] != 0:
        if res['code'] == 401:
            raise OttoError(ErrorCode_kLoginExpired, res['msg'])
        # TODO: Analyze other returned error codes
        raise OttoError(ErrorCode_kUnknown, res['msg'])
    
    if 'data' not in res:
        raise OttoError(ErrorCode_kInvalidFieldMeta, res['msg'])
    
    return res['data']


def get_field_type_id(session, venue_id, field_type_name):
    """
    Get field type id by venue id and field type name.
    
    Args:
        session: requests session, login session.
        venue_id: string, venue id.
        field_type: string, field type.

    Returns:
        string: venue type id.
    """
    sports = get_venue_type_id_list(session, venue_id)
    for sport in sports:
        if sport['name'] == field_type_name:
            return sport['id']

    raise OttoError(ErrorCode_kFieldTypeNotFound, f"Field type {field_type_name} not found.") 


def get_venue_type_id_list(session, venue_id):
    """
    Query venue type id list by venue id.
    
    Args:
        session: requests session, login session.
        venue_id: string, venue id.
    
    Returns:
        list: venue type id list.
    """
    url = "https://sports.sjtu.edu.cn/manage/venue/queryVenueById"
    data = {
        "id": venue_id
    }    
    res = _request(session, 'POST', url, data=data)
    if "登录" in res:
        raise OttoError(ErrorCode_kLoginExpired, "Get venue type id list failed, login expired.")

    res = json.loads(res)
    return res['data']['motionTypes'] 


def confirm_order(session, order):
    """Confirm order.

    Args:
        session: requests session, login session.
        order: dict, order data.

    Raises:
        err: OttoError.

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

    res = _request(session, 'POST', url, headers=headers, data=order_encrypted)

    # HTML response
    if "登录" in res:
        raise OttoError(ErrorCode_kLoginExpired, "Confirm order failed, login expired.")
    if "操作异常" in res:
        raise OttoError(ErrorCode_kInvalidOrder, "Invalid order.")

    # JSON response
    try:
        res = json.loads(res)
    except:
        raise OttoError(ErrorCode_kUnknown, "Unknown error in confirm order.")

    if res['code'] != 0:
        raise OttoError(ErrorCode_kInvalidOrder, res['msg'])
    