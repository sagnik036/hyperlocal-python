from rest_framework.permissions import BasePermission
from strings import *
from base.choices import UserType


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser


class IsEmailNotVerified(BasePermission):
    message = EMAIL_ALREADY_VERIFIED

    def has_permission(self, request, view):
        return request.user.is_authenticated and not request.user.is_email_verified


"""m2 permissions --> """

class IsShopOwnerIsNot(BasePermission):
    message = NOTSHOPOWNER

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_shop and \
            request.user.user_type == UserType.a.value[0]
    
class IsDeliveryPersonOrNot(BasePermission):
    message = NOTDELIVERYPERSON

    def has_permission(self, request, view):
        return request.user.is_authenticated and \
            request.user.user_type == UserType.b.value[0]