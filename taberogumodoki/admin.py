from taberogumodoki.forms import UserCreationForm
from django.contrib import admin
from taberogumodoki.models import Item, Category, Tag, User, Profile
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .models import Reservation
 
class TagInline(admin.TabularInline):
    model = Item.tags.through
 
 
class ItemAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    exclude = ['tags']
    search_fields = ['name']
 
 
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
 
 
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password',)}),
        (None, {'fields': ('is_active', 'is_admin',)}),
    )
 
    list_display = ('username', 'email', 'is_active',)
    list_filter = ()
    ordering = ()
    filter_horizontal = ()
 
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'is_active',)}),
    )
 
    add_form = UserCreationForm
 
    inlines = (ProfileInline,)
 
 
admin.site.register(Item, ItemAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Reservation)


