from django.shortcuts import redirect, resolve_url
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponse
from system_manage.models import AgencyAdmin, Agency, ShopAdmin, Shop

# 권한 체크
def permission_required(redirect_url=None, raise_exception=False):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if 'system-manage' in request.path:
                if not user.is_authenticated:
                    if raise_exception:
                        return HttpResponse('Unauthorized', status=401)
                    else:
                        return redirect(f"{resolve_url('system_manage:login')}?next={request.path}")
                if user.is_superuser:
                    pass
                else:
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        next_url = request.get_full_path()
                        path = resolve_url(redirect_url)
                        return redirect(f'{path}?next={next_url}')
            elif 'agency-manage' in request.path:
                if not user.is_authenticated:
                    if raise_exception:
                        return HttpResponse('Unauthorized', status=401)
                    else:
                        return redirect(f"{resolve_url('agency_manage:login')}?next={request.path}")
                agency_id = kwargs.get('agency_id')
                try:
                    agency = Agency.objects.get(pk=agency_id)
                except:
                    if raise_exception:
                        return ObjectDoesNotExist()
                    else:
                        return redirect(resolve_url('agency_manage:notfound'))
                if user.is_superuser or AgencyAdmin.objects.filter(agency=agency, user=user).exists():
                    pass
                else:
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        next_url = request.get_full_path()
                        path = resolve_url(redirect_url)
                        return redirect(f'{path}?next={next_url}')
            elif 'shop-manage' in request.path:
                if not user.is_authenticated:
                    if raise_exception:
                        return HttpResponse('Unauthorized', status=401)
                    else:
                        return redirect(f"{resolve_url('shop_manage:login')}?next={request.path}")
                shop_id = kwargs.get('shop_id')
                try:
                    shop = Shop.objects.get(pk=shop_id)
                except:
                    if raise_exception:
                        return ObjectDoesNotExist()
                    else:
                        return redirect(resolve_url('shop_manage:notfound'))
                if user.is_superuser or AgencyAdmin.objects.filter(agency=shop.agency, user=user).exists() or ShopAdmin.objects.filter(shop=shop, user=user).exists():
                    pass
                else:
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        next_url = request.get_full_path()
                        path = resolve_url(redirect_url)
                        return redirect(f'{path}?next={next_url}')
            return function(request, *args, **kwargs)
        return wrapper
    return decorator