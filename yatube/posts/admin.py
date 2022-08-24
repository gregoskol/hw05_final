from django.contrib import admin

from .models import Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "text",
        "created",
        "author",
        "group",
    )
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Follow, FollowAdmin)
