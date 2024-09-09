from requests import Session
from pickle import dump, load
from re import search
from time import time
from PIL import Image

def get_session(session):
    url = 'https://jaccount.sjtu.edu.cn/oauth2/authorize?response_type=code&scope=profile&client_id=mB5nKHqC00MusWAgnqSF&redirect_uri=https://sports.sjtu.edu.cn/oauth2Login'
    res = session.get(url).text
    if 'Login jAccount' in res:
        return False
    return True

def get_JAAuthCookie(session):
    #url = 'https://jaccount.sjtu.edu.cn/jaccount/ulogin'
    url = 'https://jaccount.sjtu.edu.cn/oauth2/authorize?response_type=code&scope=profile&client_id=mB5nKHqC00MusWAgnqSF&redirect_uri=https://sports.sjtu.edu.cn/oauth2Login'
    res = session.get(url).text

    username = input('请输入用户名：')
    password = input('请输入密码：')

    sid = search(r'sid: "(.*?)"', res).group(1)
    returl = search(r'returl:"(.*?)"', res).group(1)
    se = search(r'se: "(.*?)"', res).group(1)
    client = search(r'client: "(.*?)"', res).group(1)
    uuid = search(r'captcha\?uuid=(.*?)&t=', res).group(1)

    captcha_id = search(r'img.src = \'captcha\?(.*)\'', res).group(1) + str(int(time() * 1000))
    captcha_url = 'https://jaccount.sjtu.edu.cn/jaccount/captcha?' + captcha_id
    captcha = session.get(captcha_url, headers={'Referer': 'https://jaccount.sjtu.edu.cn'})
    with open('captcha.jpeg', 'wb') as f:
        f.write(captcha.content)
    img = Image.open('captcha.jpeg')
    img.show()
    code = input('请输入验证码：')

    data = {
        'sid': sid,
        'client': client,
        'returl': returl,
        'se': se,
        'v': '',
        'uuid': uuid,
        'user': username,
        'pass': password,
        'captcha': code,
    }
        
    res = session.post('https://jaccount.sjtu.edu.cn/jaccount/ulogin', data=data)
    with open('res.html', 'w', encoding='UTF-8') as f:
        f.write(res.text)
    if '请正确填写验证码' in res.text:
        print('验证码错误')
        return False
    elif '请正确填写你的用户名和密码' in res.text:
        print('用户名或密码错误')
        return False
    with open('cookie.save', 'wb') as f:
        dump(session, f)
    return True

def login():
    try:
        with open('cookie.save', 'rb') as f:
            session = load(f)
            if get_session(session):
                return session
    except FileNotFoundError:
        pass
    print('未找到cookie文件或凭证已过期，请登录')
    session = Session()
    get_JAAuthCookie(session)
    return session 

if __name__ == '__main__':
    s = login()
    print(s.cookies)
