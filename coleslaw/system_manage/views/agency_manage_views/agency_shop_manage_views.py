from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import View
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, InvalidPage
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.db.models import Exists, OuterRef
from system_manage.decorators import permission_required
from system_manage.models import Agency, AgencyShop, Shop

class AgencyShopManageView(View):
    '''
        가맹점 가맹점 관리 화면
    '''
    @method_decorator(permission_required(redirect_url='system_manage:denied'))
    def get(self, request: HttpRequest, *args, **kwargs):
        context = {}
        pk = kwargs.get("pk")
        agency = get_object_or_404(Agency, pk=pk)
        context['agency'] = agency

        paginate_by = '20'
        page = request.GET.get('page', '1')
        search_type = request.GET.get('search_type', '')
        search_keyword = request.GET.get('search_keyword', '')

        filter_dict = {}

        if search_keyword:
            context['search_type'] = search_type
            context['search_keyword'] = search_keyword
            filter_dict[search_type + '__icontains'] = search_keyword

        agency_shops = AgencyShop.objects.filter(shop=OuterRef('pk'), agency=agency)
        obj_list = Shop.objects.filter(**filter_dict).annotate(is_agency_shop=Exists(agency_shops)).values(
            'id',
            'name',
            'phone',
            'created_at',
            'is_agency_shop'
        ).order_by('-id')

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

        return render(request, 'agency_manage/agency_shop_manage.html', context)
    

    @method_decorator(permission_required(raise_exception=True))
    def post(self, request: HttpRequest, *args, **kwargs):
        pk = kwargs.get("pk")
        id = request.POST['id']
        try:
            agency = Agency.objects.get(pk=pk)
        except:
            return JsonResponse({"message": "데이터 오류"},status=400)
        try:
            shop = Shop.objects.get(pk=id)
        except:
            return JsonResponse({"message": "가맹점 오류"},status=400)
        
        agency_shop = AgencyShop.objects.filter(agency=agency, shop=shop)
        if agency_shop.exists():
            agency_shop.delete()
        else:
            AgencyShop.objects.create(agency=agency, shop=shop)

        return JsonResponse({'message' : '저장 되었습니다.'}, status = 201)