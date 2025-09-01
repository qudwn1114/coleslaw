from django.conf import settings

def global_variables(request):
    context={}
    context['global_site_name'] = settings.SITE_NAME
    context['CURRENCY_SYMBOL']  = settings.CURRENCY_SYMBOL
    context['LANGUAGE_CODE'] = settings.LANGUAGE_CODE

    return context