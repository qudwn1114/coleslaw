from django.shortcuts import render, redirect, resolve_url, get_object_or_404
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.utils.decorators import method_decorator
from django.db.models import F
from django.db import transaction
from django.utils.translation import gettext as _
from system_manage.decorators import  permission_required
from django.views.decorators.http import require_http_methods
from system_manage.models import Shop, ShopAdmin, SubCategory, Goods, MainCategory

from shop_manage.views.shop_manage_views.auth_views import check_shop
import json

class GoodsRankManageView(View):
    '''
        Shop 상품 순위관리
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        rank_type = request.GET.get('rank_type', 'POS')
        context['rank_type'] = rank_type
        
        return render(request, 'goods_manage/rank_manage.html', context)


@require_http_methods(["GET"])
def rank_goods(request: HttpRequest, *args, **kwargs):
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
    sub_category_id = kwargs.get('sub_category_id')
    try:
        sub_category = SubCategory.objects.get(pk=sub_category_id, shop=shop)
    except:
        return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
    rank_type = request.GET.get('rank_type', 'POS')
    if rank_type == 'POS':
        goods_list = list(Goods.objects.filter(shop=shop, sub_category=sub_category, delete_flag=False, status=True, kiosk_display=True).annotate(rank=F('pos_rank')).order_by('pos_rank').values('id', 'name_kr', 'rank', 'sale_price'))
    elif rank_type == 'KIOSK':
        goods_list = list(Goods.objects.filter(shop=shop, sub_category=sub_category, delete_flag=False, status=True, kiosk_display=True).annotate(rank=F('kiosk_rank')).order_by('kiosk_rank').values('id', 'name_kr', 'rank', 'sale_price'))
    else:
        return JsonResponse({'message': _('ERR_TYPE_INVALID')}, status=400)
    data = {'goods_list':goods_list}
    return JsonResponse(data, status = 200)



@require_http_methods(["POST"])
def update_rank_goods(request: HttpRequest, *args, **kwargs):
    shop_id = kwargs.get('shop_id')
    shop = check_shop(pk=shop_id)
    if not shop:
        return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
    sub_category_id = kwargs.get('sub_category_id')
    try:
        sub_category = SubCategory.objects.get(pk=sub_category_id, shop=shop)
    except:
        return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
    rank_type = request.GET.get('rank_type', None)
    if rank_type == 'POS':
        rank_field = 'pos_rank'
    elif rank_type == 'KIOSK':
        rank_field = 'kiosk_rank'
    else:
        return JsonResponse({'message': _('ERR_TYPE_INVALID')}, status=400)
    try:
        data = json.loads(request.body)
        order_list = data.get('order', [])
         # ID와 rank를 기반으로 한 리스트 구성
        goods_ids = [item.get('id') for item in order_list]
        goods_queryset = Goods.objects.filter(id__in=goods_ids, shop_id=shop_id, sub_category=sub_category)

        if goods_queryset.count() != len(goods_ids):
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        # ID → rank 매핑 딕셔너리
        rank_map = {int(item['id']): item['rank'] for item in order_list}
        # 트랜잭션으로 일괄 업데이트
        with transaction.atomic():
            for goods in goods_queryset:
                new_rank = rank_map.get(goods.id)
                setattr(goods, rank_field, new_rank)
            Goods.objects.bulk_update(goods_queryset, [rank_field])
        return JsonResponse({'message': _('MSG_UPDATED')}, status=200)
    
    except Exception as e:
        print(e)
        return JsonResponse({'message': _('ERR_UPDATE')}, status=400)
