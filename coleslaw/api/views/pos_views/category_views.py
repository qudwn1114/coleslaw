from django.views.generic import View
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Value as V


from system_manage.models import Shop, ShopTable, SubCategory, MainCategory, Goods

import json, traceback

class ShopPosMainCategoryListView(View):
    '''
        pos 메인 카테고리 list api
    '''
    def get(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        mainpos_id = int(kwargs.get('mainpos_id'))
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop=shop, pos=shop.pos)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        fixed_category_id = shop_table.fixed_category_id
        fixed_main_category_id = None
        if fixed_category_id == 0:
            fixed = True
        else:
            fixed = False

        try:
            shop_sub_category = Goods.objects.filter(shop=shop, delete_flag=False, status=True).values('sub_category').distinct()
            shop_sub_category_id_list = list(shop_sub_category.values_list('sub_category', flat=True))
            shop_main_category_id_list = list(shop_sub_category.values_list('sub_category__main_category', flat=True))
            queryset = MainCategory.objects.filter(id__in=shop_main_category_id_list, shop=shop).values(
                    'id',
                    'name_kr',
                    'name_en'
                ).order_by('rank')
            
            for i in queryset:
                i['sub_category'] = list(SubCategory.objects.annotate(fixed=V(False)).filter(id__in=shop_sub_category_id_list, main_category_id=i['id'], shop=shop).values(
                    'id',
                    'name_kr',
                    'name_en',
                    'fixed'
                ).order_by('rank'))

                if not fixed:
                    for j in i['sub_category']:
                        if j['id'] == fixed_category_id:
                            fixed_main_category_id = i['id']
                            j['fixed'] = True
                            fixed = True
                            break
            return_data = {
                'data': list(queryset),
                'fixed_main_category_id' : fixed_main_category_id,
                'resultCd': '0000',
                'msg': '가맹점 POS 카테고리 리스트',
                'totalCnt' : queryset.count()
            }
        except:
            print(traceback.format_exc())
            return_data = {
                'data': [],
                'msg': '오류!',
                'resultCd': '0001',
            }
    
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
    



class ShopPosCatgoryFixView(View):
    '''
        상품담기
    '''
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ShopPosCatgoryFixView, self).dispatch(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        mainpos_id = int(kwargs.get('mainpos_id'))
        try:
            shop = Shop.objects.get(pk=shop_id)
        except:
            return_data = {'data': {},'msg': 'shop id 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        try:
            shop_table = ShopTable.objects.get(table_no=mainpos_id, shop=shop, pos=shop.pos)
        except:
            return_data = {'data': {},'msg': '테이블 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        if shop_table.table_no > 0:
            return_data = {'data': {},'msg': 'POS 홈에만 적용 가능합니다.','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        sub_category_id = request.POST['sub_category_id']
        try:
            sub_category = SubCategory.objects.get(pk=sub_category_id, shop=shop)
        except:
            return_data = {'data': {},'msg': '카테고리 ID 오류','resultCd': '0001'}
            return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
            return HttpResponse(return_data, content_type = "application/json")
        
        shop_table.fixed_category_id = sub_category.pk
        shop_table.save()

        return_data = {'data': {},'msg': '고정되었습니다.','resultCd': '0000'}
        return_data = json.dumps(return_data, ensure_ascii=False, cls=DjangoJSONEncoder)
        return HttpResponse(return_data, content_type = "application/json")
        
