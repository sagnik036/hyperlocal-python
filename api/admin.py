from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.gis.admin import OSMGeoAdmin
from api.forms import ( PaymentTermForm,
                       PrivacyPolicyForm, TermForm, AdminNotificationForm)
from api.models import (AdminContact, AdminNotification, CustomUser,
                        PaymentTerm, PrivacyPolicy, ProprietorShop, \
                    TermAndCondition,FrequentlyAskedQuestion,
)


from api.task import send_notification_to_users
from django.db import transaction
from base.choices import NotificationType

admin.site.site_header = 'HYPERLOCAL-ADMIN'
admin.site.site_url = None

admin.site.unregister(Group)
admin.site.register(FrequentlyAskedQuestion)


class OneObjectAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return None

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(AdminContact)
class AdminContactAdmin(OneObjectAdmin):
    list_display = ('email', 'phone_number')


@admin.register(TermAndCondition)
class TermAndConditionAdmin(OneObjectAdmin):
    form = TermForm
    list_display = ('modified_at',)


@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(OneObjectAdmin):
    form = PrivacyPolicyForm
    list_display = ('modified_at',)


@admin.register(PaymentTerm)
class PaymentTermAdmin(OneObjectAdmin):
    form = PaymentTermForm
    list_display = ('modified_at',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        ('Credentials', {'fields': ('mobile_number','email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name','profile_pic','is_shop','adhar_photo_front','adhar_photo_back')}),  
        ('Permissions', {
            'fields': ('is_active', 'is_superuser','is_adhar_verified'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        ('Credentials', {
            'classes': ('wide',),
            'fields': ('mobile_number','email','password1', 'password2'),
        }),
    )
    list_display = ('mobile_number','first_name', 'last_name', \
                    'is_active','user_type','is_shop','is_adhar_verified')
    list_filter = ('is_superuser', 'is_active','user_type','is_adhar_verified','is_shop')
    search_fields = ('first_name', 'last_name', 'mobile_number')
    ordering = ('first_name',)



# @admin.register(AdminNotification)
# class AdminNotificationAdmin(admin.ModelAdmin):
#     form = AdminNotificationForm
#     list_display = ('title',)
#     add_form_template = 'admin/admin_notification_add.html'
#     change_form_template = 'admin/admin_notification_change.html'

#     def save_model(self, request, obj, form, change):
#         super().save_model(request, obj, form, change)
#         if obj.sent_to_all:
#             # TODO: Enforce this condition if CustomerUser model have a user_type field.
#             # if obj.current_user_type:
#             #     user_ids = set(CustomUser.objects.filter(
#             #         current_user_type=obj.current_user_type).values_list('id', flat=True))
#             # else:
#             #     user_ids = set(CustomUser.objects.filter(
#             #         is_superuser=False, is_staff=False, is_active=True).values_list('id', flat=True))

#             # TODO: Remove this if obj have a user_type field
#             user_ids = set(CustomUser.objects.filter(
#                 is_superuser=False, is_staff=False, is_active=True).values_list('id', flat=True))
#         else:
#             user_ids = set(AdminNotification.recipients.through.objects.filter(
#                 adminnotification_id=obj.id).values_list('customuser_id', flat=True))

#         user_ids = list(map(lambda val: str(val), user_ids))

#         transaction.on_commit(lambda: send_notification_to_users.apply_async(kwargs={
#             'user_ids': user_ids,
#             'notification_type': NotificationType.admin.value[0],
#             'title': obj.title,
#             'body': obj.description,
#             'admin_notification_id': str(obj.id)
#         }))

@admin.register(ProprietorShop)
class ProprietorShopAdmin(OSMGeoAdmin):
    list_display = ('user','location')

