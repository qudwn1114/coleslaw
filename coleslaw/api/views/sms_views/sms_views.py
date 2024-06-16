from django.conf import settings
import time, hashlib, hmac, base64, json, requests


def send_sms(phone:str, message:str):
    """
        지정된 번호로 SMS 메세지를 보냅니다.
    """
    timestamp = str(int(time.time() * 1000))
    signature = _make_NCP_signature(settings.SMS_API_KEY, settings.SMS_ACCESS_KEY, settings.SMS_SECRET_KEY, timestamp)
    uri = f"https://sens.apigw.ntruss.com/sms/v2/services/{settings.SMS_API_KEY}/messages"

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp, # 네이버 API 서버와 5분이상 시간차이 발생시 오류
        'x-ncp-iam-access-key': settings.SMS_ACCESS_KEY,
        'x-ncp-apigw-signature-v2': signature
    }

    body = {
        "type":"SMS",
        "contentType":"COMM",
        "countryCode":"82",
        "from":settings.SMS_SENDER,
        "content": message,
        "messages":[
            {
                "to": phone.replace('-', ''),
            }
        ],
    }
    body = json.dumps(body)
    response = requests.post(uri, headers=headers, data=body)
    return response

def send_mms(phone:str, subject:str, message:str):
    """
        지정된 번호로 MMS 메세지를 보냅니다.
    """

    timestamp = str(int(time.time() * 1000))
    signature = _make_NCP_signature(settings.SMS_API_KEY, settings.SMS_ACCESS_KEY, settings.SMS_SECRET_KEY, timestamp)
    uri = f"https://sens.apigw.ntruss.com/sms/v2/services/{settings.SMS_API_KEY}/messages"

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'x-ncp-apigw-timestamp': timestamp, # 네이버 API 서버와 5분이상 시간차이 발생시 오류
        'x-ncp-iam-access-key': settings.SMS_ACCESS_KEY,
        'x-ncp-apigw-signature-v2': signature
    }

    body = {
        "type":"MMS",
        "contentType":"COMM",
        "countryCode":"82",
        "from":settings.SMS_SENDER,
        "subject": subject,
        "content": message,
        "messages":[
            {
                "to": phone.replace('-', ''),
                "subject": subject,
                "content": message
            }
        ],
    }
    body = json.dumps(body)
    response = requests.post(uri, headers=headers, data=body)
    return response

def	_make_NCP_signature(api_key, access_key, secret_key, timestamp):
    """
        NCP SMS 서비스 요청을 위한 시그니처 키를 생성합니다.
    """

    secret_key = bytes(secret_key, 'UTF-8')
    method = "POST"
    uri = "/sms/v2/services/"+ api_key +"/messages"
    message = method + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, 'UTF-8')
    signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
    return signingKey


