from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.utils.decorators import method_decorator
from django.db.models import Min
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods
from system_manage.decorators import permission_required
from shop_manage.views.shop_manage_views.auth_views import check_shop
from system_manage.models import ShopTable, Pos
import json

class ShopPosManageView(View):
    '''
        pos manage
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        paginate_by = '20'
        page = request.GET.get('page', '1')
        pos_id = request.GET.get('pos_id', '')
        if pos_id:
            pos_id = int(pos_id)
        else:
            if shop.pos:
                pos_id = shop.pos.pk
            else:
                pos_id = None

        context['pos_id'] = pos_id
        
        filter_dict = {}
        filter_dict['pos_id'] = pos_id
        filter_dict['shop'] = shop
        filter_dict['table_no__lte'] = 0 

        pos = Pos.objects.all().values('id', 'name')
        context['pos'] = pos

        obj_list = ShopTable.objects.filter(**filter_dict).values(
            'id',
            'name',
            'table_no',
            'tid',
            'created_at'
        ).order_by('id')

        paginator = Paginator(obj_list, paginate_by)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            page_obj = paginator.page(page)
        except EmptyPage:
            page = 1
            page_obj = paginator.page(page)
        except InvalidPage:
            page = 1
            page_obj = paginator.page(page)

        pagelist = paginator.get_elided_page_range(page, on_each_side=3, on_ends=1)
        context['pagelist'] = pagelist
        context['page_obj'] = page_obj

        return render(request, 'pos_manage/pos_manage.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def put(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        request.PUT = json.loads(request.body)
        rq_type = request.PUT['type']

        if rq_type == 'NAME':
            table_id = request.PUT['id']
            try:
                shop_table = ShopTable.objects.get(pk=table_id, shop=shop)
            except:
                return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
            table_name = request.PUT['table_name'].strip()            
            shop_table.name = table_name
            shop_table.save()
        elif rq_type == 'TID':
            table_id = request.PUT['id']
            try:
                shop_table = ShopTable.objects.get(pk=table_id, shop=shop)
            except:
                return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
            tid = request.PUT['tid'].strip()
            shop_table.tid = tid
            shop_table.save()
        elif rq_type == 'POS':
            pos_id = request.PUT['pos_id']
            try:
                pos = Pos.objects.get(pk=pos_id)
            except:
                return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
            shop.pos = pos
            shop.save()
        return JsonResponse({'message' : _('MSG_UPDATED')}, status = 201)
    
    @method_decorator(permission_required(raise_exception=True))
    def delete(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        request.DELETE = json.loads(request.body)
        table_id = request.DELETE['id']

        try:
            shop_table = ShopTable.objects.get(pk=table_id, shop=shop)
        except:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        if shop_table.table_no > 0:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        shop_table.delete()
        
        return JsonResponse({'message' : _('MSG_DELETED')}, status = 201)

class ShopPosCreateView(View):
    '''
        pos 생성
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        pos_id = request.GET.get('pos_id', '')
        pos = get_object_or_404(Pos, pk=pos_id)
        context['pos'] = pos

        return render(request, 'pos_manage/pos_create.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        table_name = request.POST['table_name'].strip()
        pos_id = request.POST['pos_id']
        try:
            pos = Pos.objects.get(pk=pos_id)
        except:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        if not ShopTable.objects.filter(pos=pos, shop=shop, table_no__lte=0).exists():
            table_no = 0
        else:
            min_table_no = ShopTable.objects.filter(pos=pos, shop=shop, table_no__lte=0).aggregate(Min("table_no", default=0))['table_no__min']        
            table_no = min_table_no - 1
        ShopTable.objects.create(
            pos=pos,
            shop=shop,
            name=table_name,
            tid='',
            table_no= table_no
        )
        
        return JsonResponse({'message' : _('MSG_CREATED'), 'url':f"{reverse('shop_manage:pos_manage', kwargs={'shop_id':shop.id})}?pos_id={pos.pk}"},  status = 201)


class ShopPosDetailView(View):
    '''
        가맹점 포스 정보 상세
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        return render(request, 'pos_manage/shop_pos_detail.html', context)
    

class ShopPosEditView(View):
    '''
        가맹점 포스 정보 수정
    '''
    @method_decorator(permission_required(redirect_url='shop_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return redirect('shop_manage:notfound')
        context['shop'] = shop
        
        return render(request, 'pos_manage/shop_pos_edit.html', context)
    
    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        VIDEO_MAX_UPLOAD_SIZE = 209715200
        shop_id = kwargs.get('shop_id')
        shop = check_shop(pk=shop_id)
        if not shop:
            return JsonResponse({'message': _('ERR_DATA_INVALID')}, status=400)
        
        pos_ad_video = request.FILES.get("pos_ad_video")
        receipt = request.POST['receipt'].strip()
        shop_receipt_flag = bool(request.POST.get('shop_receipt_flag', None))

        if pos_ad_video:
            if pos_ad_video.size > VIDEO_MAX_UPLOAD_SIZE:
                return JsonResponse({'message': _('ERR_AD_SIZE')}, status=400)
        
        shop.receipt = receipt
        shop.shop_receipt_flag = shop_receipt_flag
        if pos_ad_video:
            shop.pos_ad_video = pos_ad_video

        shop.save()
        return JsonResponse({'message' : _('MSG_UPDATED'), 'url':reverse('shop_manage:shop_pos_detail', kwargs={'shop_id':shop.id})},  status = 201)
    