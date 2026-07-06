from .models import SiteSetting, Category

def site_settings(request):
    setting = SiteSetting.objects.first()
    if not setting:
        # Create a default one if it doesn't exist
        setting = SiteSetting.objects.create(site_name="NextGen Pro Learning")
    
    return {
        'site_setting': setting,
        'global_categories': Category.objects.all().order_by('name')
    }
