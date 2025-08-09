from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html
from django.template.response import TemplateResponse
from .models import Category, Menu, Contact

class MenuAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'order', 'image_preview']
    list_editable = ['order']
    list_filter = ['category']
    search_fields = ['name', 'desc']
    ordering = ['order', '-id']
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_reorder_link'] = True
        return super().changelist_view(request, extra_context)
    
    def image_preview(self, obj):
        if obj.img:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.img.url)
        return "No image"
    image_preview.short_description = 'Image'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('reorder/', self.admin_site.admin_view(self.reorder_view), name='menu_reorder'),
        ]
        return custom_urls + urls
    
    def reorder_view(self, request):
        if request.method == 'POST':
            try:
                data = request.POST
                menu_id = data.get('menu_id')
                new_order = data.get('new_order')
                
                if menu_id and new_order:
                    menu = Menu.objects.get(id=menu_id)
                    menu.order = int(new_order)
                    menu.save()
                    return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})
        
        # GET request - show reorder interface
        menus = Menu.objects.all().order_by('order', '-id')
        context = {
            'menus': menus,
            'title': 'Reorder Menu Items',
            'opts': self.model._meta,
        }
        return TemplateResponse(request, 'admin/menu/reorder.html', context)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    search_fields = ['name']

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']

admin.site.register(Category, CategoryAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Contact, ContactAdmin)

admin.site.site_header = "Pizza Admin"
admin.site.index_title = "Welcome to Pizza Admin Portal"