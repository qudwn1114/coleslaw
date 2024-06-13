from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.db.models import Exists, OuterRef
from system_manage.decorators import permission_required
from system_manage.models import Shop, ShopAdmin

class ShopAdminManageView(View):
    '''
        가맹점 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        shop = get_object_or_404(Shop, pk=pk)
        context['shop'] = shop

        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}

        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        shop_admins = ShopAdmin.objects.filter(user=OuterRef('pk'), shop=shop)
        obj_list = User.objects.filter(**filter_dict).annotate(is_admin=Exists(shop_admins)).values(
            'id',
            'username',
            'profile__membername',
            'date_joined',
            'profile__phone',
            'is_admin'
        ).order_by('-date_joined')

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

        return render(request, 'shop_manage/shop_admin_manage.html', context)
    

    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get("pk")
        id = request.POST['id']
        try:
            shop = Shop.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        try:
            user = User.objects.get(pk=id)
        except:
            return JsonResponse({"message": "유저 오류"},status=400)
        
        admin = ShopAdmin.objects.filter(shop=shop, user=user)
        if admin.exists():
            admin.delete()
        else:
            ShopAdmin.objects.create(shop=shop, user=user)

        return JsonResponse({'message' : '저장 되었습니다.'}, status = 201)