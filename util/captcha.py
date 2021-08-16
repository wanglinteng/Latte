import requests


def captcha_check(captcha_url='http://localhost:8080/verify_captcha'):
    """爬取过程中可能会触发知乎反爬验证码，请求验证码服务"""
    return requests.get(url=captcha_url).json()


if __name__ == '__main__':
    res = captcha_check()
    print(res)
