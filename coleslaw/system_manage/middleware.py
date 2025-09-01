from django.conf import settings
from django.utils import translation

class ActivateSettingsLanguageMiddleware:
    """
    settings.py에 설정된 LANGUAGE_CODE로 모든 요청에서 활성 언어 설정
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # settings.py LANGUAGE_CODE로 활성화
        translation.activate(settings.LANGUAGE_CODE)
        response = self.get_response(request)
        return response