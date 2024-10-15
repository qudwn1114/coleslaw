from django.views.generic import View
from django.http import HttpRequest, JsonResponse

from system_manage.models import Goods

class GoodsShopView(View):
    '''
        Goods Shop api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        code = kwargs.get('code')
        try:
            goods = Goods.objects.get(code=code)
            return JsonResponse({'message':'조회성공', 'shop_id':goods.shop.pk},  status = 200)        
        except:
            return JsonResponse({'message':'없음', 'shop_id':None},  status = 400)