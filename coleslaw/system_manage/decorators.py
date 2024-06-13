from django.shortcuts import redirect, resolve_url
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from system_manage.models import ShopAdmin

# 권한 체크
def permission_required(redirect_url=None, raise_exception=False):
    def decorator(function):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if 'system-manage' in request.path:
                if not user:
                    if raise_exception:
                        return HttpResponse('Unauthorized', status=401)
                    else:
                        return redirect(resolve_url('system_manage:login'))
                if user.is_superuser:
                    pass
                else:
                    if raise_exception:
                        raise PermissionDenied()
                    else:
                        next_url = request.get_full_path()
                        path = resolve_url(redirect_url)
                        return redirect(f'{path}?next={next_url}')
            elif 'shop-manage' in request.path:
                if not user:
                    if raise_exception:
                        return HttpResponse('Unauthorized', status=401)
                    else:
                        return redirect(resolve_url('shop_manage:login'))
                shop_id = kwargs.get('shop_id')
                if user.is_superuser or ShopAdmin.objects.filter(shop_id=shop_id, user=user).exists():
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