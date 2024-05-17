from django.contrib import admin

from blog.models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'created_at',
        'title',
        'text',
        'pub_date'
    )
    list_editable = (
        'title',
        'text'
    )
    search_fields = (
        'title',
        'text',
        'author__username'
    )
    list_filter = ('title', 'author')


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'slug'
    )
    search_fields = (
        'title',
        'description',
        'slug'
    )
    list_filter = ('title', 'slug')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (PostInline,)
    list_display = ('name',)
    search_fields = ('name',)


admin.site.empty_value_display = 'Не задано'
