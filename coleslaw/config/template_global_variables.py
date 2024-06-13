from django.conf import settings

def global_variables(request):
    context={}
    context['global_site_name'] = settings.SITE_NAME

    return context