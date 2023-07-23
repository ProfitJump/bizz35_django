from django.contrib import admin
from .models import Profile, LedgerEntry
from django.contrib.sites.models import Site

# Register your models here.
admin.site.register(Profile)
admin.site.register(LedgerEntry)
admin.site.unregister(Site)


class SiteAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'domain')
    readonly_fields = ('id',)
    list_display = ('id', 'name', 'domain')
    list_display_links = ('name',)
    search_fields = ('name', 'domain')


admin.site.register(Site, SiteAdmin)
