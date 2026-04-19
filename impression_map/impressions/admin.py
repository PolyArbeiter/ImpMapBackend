from django.contrib import admin

from impressions.models import Impression, ImpressionMedia


class ImpressionMediaInline(admin.TabularInline):
    model = ImpressionMedia
    extra = 1
    fields = ["file", "is_video"]


@admin.register(Impression)
class ImpressionAdmin(admin.ModelAdmin):
    inlines = [ImpressionMediaInline]


admin.site.register(ImpressionMedia)
