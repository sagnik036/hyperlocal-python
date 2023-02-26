import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.hashers import check_password
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views import View
from django.db.models import F
from django.views.generic.list import BaseListView
import logging

from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.backends import TokenBackend, TokenBackendError
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_gis.filters import GeoFilterSet
from rest_framework.filters import SearchFilter

from base.base_permissions import IsSuperUser, IsEmailNotVerified, \
    IsShopOwnerIsNot,IsDeliveryPersonOrNot
from base.base_views import (CustomAPIView, CustomCreateModelMixin,
                             CustomDestroyModelMixin, CustomGenericView,
                             CustomListModelMixin, CustomRetrieveModelMixin,
                             CustomUpdateModelMixin)
from base.choices import NotificationType
from api.models import (AdminContact, CustomUser, DeviceToken, PaymentTerm,\
                        PrivacyPolicy, TermAndCondition, UserNotification,\
                        FrequentlyAskedQuestion, ProprietorShop,VehicleDeliveryPerson)
from base.utils import (CustomException, error_response, \
                        success_response, create_otp,phonenumber_validator)
from api.serializers import (AdminContactSerializer, CustomUserSerializer,
                             DeviceTokenSerializer, TextSerializer,
                             UserNotificationSerializer,FrequentlyAskedQuestionSerializer,
                             UserPasswordSerializer,ShopSerializers,ShopListSerializers,
                             VehicleListSerializers,VehicleSerializers)

from api.task import send_mail_task, send_notification_to_users, send_transactional_sms
from strings import *
from rest_framework.validators import ValidationError
from rest_framework_gis.filters import DistanceToPointFilter
# from .filters import ShopFilter

from django_filters.rest_framework import DjangoFilterBackend

from base.utils import get_jwt_auth_token
logger = logging.getLogger(__file__)


class TermAndConditionAPI(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsSuperUser,)
        super().initial(request, *args, **kwargs)

    def get(self, request):
        tnc = TermAndCondition.objects.first()
        if not tnc:
            tnc = TermAndCondition.objects.create(text=DEFAULT_CLAUSES_TEXT)
        serializer = TextSerializer(tnc, context={'request': request})
        return success_response(data=serializer.data)

    @transaction.atomic
    def post(self, request):
        tnc = TermAndCondition.objects.first()
        serializer = TextSerializer(
            instance=tnc,
            data=request.data,
            context={'request': request, 'model': TermAndCondition},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if tnc is not None:
            send_notification_to_users.apply_async(
                kwargs={
                    'user_ids': None,
                    'notification_type': NotificationType.tnc_updated.value[0],
                    'title': TNC_UPDATED_TITLE,
                    'body': TNC_UPDATED_DESCRIPTION
                }
            )
        return success_response(data=serializer.data)


class AdminContactAPI(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsSuperUser,)
        super().initial(request, *args, **kwargs)

    def get(self, request):
        contact = AdminContact.objects.first()
        if not contact:
            contact = AdminContact.objects.create(
                email=settings.DEFAULT_FROM_EMAIL, phone_number='+61458495849')
        serializer = AdminContactSerializer(contact, context={'request': request})
        return success_response(data=serializer.data)

    @transaction.atomic
    def post(self, request):
        contact = AdminContact.objects.first()
        serializer = AdminContactSerializer(instance=contact, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data)


class PrivacyPolicyAPI(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsSuperUser,)
        super().initial(request, *args, **kwargs)

    def get(self, request):
        privacy_policy = PrivacyPolicy.objects.first()
        if not privacy_policy:
            privacy_policy = PrivacyPolicy.objects.create(text=DEFAULT_CLAUSES_TEXT)
        serializer = TextSerializer(privacy_policy, context={'request': request})
        return success_response(data=serializer.data)

    @transaction.atomic
    def post(self, request):
        privacy_policy = PrivacyPolicy.objects.first()
        serializer = TextSerializer(
            instance=privacy_policy,
            data=request.data,
            context={'request': request, 'model': PrivacyPolicy},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if privacy_policy is not None:
            send_notification_to_users.apply_async(
                kwargs={
                    'user_ids': None,
                    'notification_type': NotificationType.get_value(
                        NotificationType.privacy_policy_updated.name
                    ),
                    'title': PRIVACY_POLICY_UPDATED_TITLE,
                    'body': PRIVACY_POLICY_UPDATED_DESCRIPTION
                }
            )
        return success_response(data=serializer.data)


class PaymentTermAPI(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsSuperUser,)
        super().initial(request, *args, **kwargs)

    def get(self, request):
        payment_term = PaymentTerm.objects.first()
        if not payment_term:
            payment_term = PaymentTerm.objects.create(text=DEFAULT_CLAUSES_TEXT)
        serializer = TextSerializer(payment_term, context={'request': request})
        return success_response(data=serializer.data)

    @transaction.atomic
    def post(self, request):
        payment_term = PaymentTerm.objects.first()
        serializer = TextSerializer(
            instance=payment_term,
            data=request.data,
            context={'request': request, 'model': PaymentTerm},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if payment_term is not None:
            send_notification_to_users.apply_async(
                kwargs={
                    'user_ids': None,
                    'notification_type': NotificationType.payment_terms_updated.value[0],
                    'title': PAYMENT_TERM_UPDATED_TITLE,
                    'body': PAYMENT_TERM_UPDATED_DESCRIPTION
                }
            )
        return success_response(data=serializer.data,
                                message='Terms updated successfully')


class DeviceTokenView(CustomAPIView):
    @transaction.atomic
    def post(self, request):
        serializer = DeviceTokenSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return success_response(message=DEVICE_TOKEN_SAVED)

    @transaction.atomic
    def delete(self, request):
        DeviceToken.objects.filter(user_id=request.user.id, device_type=request.data['device_type']).delete()
        return success_response(message=DEVICE_TOKEN_REMOVED)


class UserNotificationList(CustomListModelMixin, CustomGenericView):
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        UserNotification.objects.filter(user_id=request.user.id).update(is_read=True)
        CustomUser.objects.filter(id=request.user.id).update(unread_notification_count=0)
        return success_response(message=NOTIFICATION_MARKED_READ)


class UserNotificationDetail(CustomRetrieveModelMixin,
                             CustomUpdateModelMixin, CustomGenericView):
    queryset = UserNotification.objects.all()
    serializer_class = UserNotificationSerializer

    def get_queryset(self):
        return super().get_queryset().filter(user_id=self.request.user.id)

    def get(self, request, *args, **kwargs):
        if UserNotification.objects.filter(user_id=request.user.id, is_read=False, id=kwargs['pk']).exists():
            UserNotification.objects.filter(id=kwargs['pk']).update(is_read=True)
            CustomUser.objects.filter(id=request.user.id).update(
                unread_notification_count=F('unread_notification_count') - 1)
        return self.retrieve(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class CheckEmail(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        qs = CustomUser.objects.filter(email__iexact=request.data['email'])
        if request.user.is_authenticated:
            qs = qs.exclude(id=request.user.id)
        available = not qs.exists()
        return success_response(data={"available": available})


class ForgetPasswordAPI(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method in ('GET', 'POST'):
            self.permission_classes = (AllowAny,)
        super().initial(request, *args, **kwargs)

    # def get(self, request):
    #     user = CustomUser.objects.only('id', 'email', 'first_name', 'last_name').filter(
    #         email__iexact=request.query_params['email']).first()
    #     if user is not None:
    #         token = TokenBackend(
    #             settings.SIMPLE_JWT['ALGORITHM'],
    #             settings.SIMPLE_JWT['SIGNING_KEY']).encode({
    #             'email': user.email.lower(),
    #             'exp': int((timezone.now() + timezone.timedelta(days=1)).timestamp())
    #         })
    #         link = f"{'https' if request.is_secure() else 'http'}://{request.META['HTTP_HOST']}/reset-password/{token}"
    #         admin_contact = AdminContact.objects.first()
    #         send_mail_task.apply_async(kwargs={
    #             'subject': 'Reset password',
    #             'html_message': render_to_string('emails/reset_password.html', context={
    #                 'link': link,
    #                 'user_name': user.get_full_name(),
    #                 'admin_email': admin_contact.email if admin_contact else ''
    #             }),
    #             'recipient_list': [user.email],
    #         })
    #         return success_response(message=RESET_PASSWORD_LINK_SENT)
    #     return error_response(message=EMAIL_NOT_EXISTS)

    def post(self, request):

        """this is just decoding the otp and mobile number and verifying it"""
        otp_payload = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']
        ).decode(request.data['token'])

        if not (otp_payload['otp'] == request.data['otp'] or (
            settings.ENV == 'development' and request.data['otp'] == '111111')):
                raise CustomException(INVALID_CODE)
        
        mobile = phonenumber_validator('+'+request.data['mobile_number'])
        if not (otp_payload['mobile_number'] == mobile):
                raise CustomException(MOBILE_INVALID)
        if otp_payload['exp'] < timezone.now().timestamp():
            raise CustomException(EXPIRED_LINK)

        user = CustomUser.objects.get_by_natural_key(otp_payload['mobile_number'])
        serializer = UserPasswordSerializer(instance=user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message=PASSWORD_UPDATED)

    @transaction.atomic
    def put(self, request):
        if not check_password(request.data['old_password'], request.user.password):
            raise CustomException(OLD_PASSWORD_WRONG)
        if request.data['password'] == request.data['old_password']:
            raise CustomException(SAME_PASSWORD_ERROR)
        serializer = UserPasswordSerializer(instance=request.user, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message=PASSWORD_UPDATED)


class ProfileAPI(CustomAPIView):
    def get(self, request):
        user_data = CustomUserSerializer(request.user, context={'request': request}).data
        return success_response(data=user_data)

    @transaction.atomic
    def patch(self, request):
        if request.data.get('email') or request.data.get('mobile_number'):
            if not check_password(request.data['password'], request.user.password):
                raise CustomException(OLD_PASSWORD_WRONG)
        serializer = CustomUserSerializer(
            instance=self.request.user, data=request.data, context={
                'request': request}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message=UPDATE_SUCCESS)


class EmailVerify(CustomAPIView):
    permission_classes = (IsEmailNotVerified,)

    def get(self, request):
        subject = "Email verify"
        token = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']).encode({
            'email': request.user.email,
            'exp': int((timezone.now() + timezone.timedelta(days=1)).timestamp())
        })
        link = f"{'https' if request.is_secure() else 'http'}://{request.META['HTTP_HOST']}/verify-email/{token}"
        admin_contact = AdminContact.objects.first()
        send_mail_task.apply_async(
            kwargs={
                "recipient_list": [request.user.email],
                "subject": subject,
                "html_message": render_to_string('emails/email_verify.html', context={
                    'link': link,
                    'user_name': request.user.get_full_name(),
                    'admin_email': admin_contact.email if admin_contact else ''
                })
            }
        )
        return success_response(message=VERIFICATION_MAIL_SENT)


class VerifyEmail(View):
    def get(self, request, token):
        try:
            token_data = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).decode(token)
            user = CustomUser.objects.get(
                email__iexact=token_data['email'],
                is_email_verified=False)
            verified = True
            user.is_email_verified = True
            user.save(update_fields=['is_email_verified'])
        except BaseException:
            verified = False
        return render(request, 'email_verify.html', {'verified': verified})


class ResetPassword(View):
    def get(self, request, token):
        admin_contact = AdminContact.objects.first()
        try:
            token_data = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).decode(token)
            user = CustomUser.objects.get(email__iexact=token_data['email'])
            form = SetPasswordForm(user)
            return render(request, 'reset_password.html', {
                'form': form,
                'admin_email': admin_contact.email if admin_contact else ''
            })
        except TokenBackendError:
            messages.error(request, 'Link is invalid or it has been expired')
            return render(request, 'reset_password.html', context={
                'admin_email': admin_contact.email if admin_contact else ''
            })

    def post(self, request, token):
        admin_contact = AdminContact.objects.first()
        try:
            token_data = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).decode(token)
            user = CustomUser.objects.get(email__iexact=token_data['email'])
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Password updated successfully')
                return render(request, 'reset_password.html', context={
                    'admin_email': admin_contact.email if admin_contact else ''
                })
            else:
                return render(request, 'reset_password.html', {
                    'form': form,
                    'admin_email': admin_contact.email if admin_contact else ''
                })
        except TokenBackendError:
            messages.error(request, 'Link is invalid or it has been expired')
            return render(request, 'reset_password.html', context={
                'admin_email': admin_contact.email if admin_contact else ''
            })

class UserNotificationCountAPI(CustomAPIView):
    def get(self, request, *args, **kwargs):
        return success_response(data=self.request.user.unread_notification_count)




class LoginAPI(CustomAPIView):
    permission_classes = (AllowAny,)
    

    def post(self, request):
        user = None
        mobile = phonenumber_validator('+'+request.data['mobile_number'])
        if 'otp' not in request.data or not request.data['otp']:
            user = authenticate(
                request,
                username=mobile,
                password=request.data['password']
            )
        else:
            otp_payload = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).decode(request.data['token']
            )
            if not (otp_payload['otp'] == request.data['otp'] or (
                settings.ENV == 'development' and request.data['otp'] == '111111')):
                raise CustomException(INVALID_CODE)
            if not (otp_payload['mobile_number'] == mobile):
                raise CustomException(MOBILE_INVALID)
            
            username = otp_payload['mobile_number']
            user = CustomUser.objects.get_by_natural_key(username)

        if user is None:
            return error_response(message=CANNOT_LOGIN, code=status.HTTP_401_UNAUTHORIZED)
        CustomUser.objects.filter(id=user.id).update(last_login=timezone.now())
        user_data = CustomUserSerializer(user, context={'request': request}).data
        return success_response(data=user_data, message=LOGIN_SUCCESS, extra_data={'token': get_jwt_auth_token(user)})



class RegistrationView(CustomAPIView):
    permission_classes = (AllowAny,)
    throttle_scope = 'on_boarding'

    @transaction.atomic
    def post(self, request):
        otp_payload = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']).decode(request.data['token']
        )

        if not (otp_payload['otp'] == request.data['otp'] or (
                settings.ENV == 'development' and request.data['otp'] == '111111')):
            raise CustomException(INVALID_CODE)

        if not (otp_payload['mobile_number'] == request.data['mobile_number']):
            raise CustomException(MOBILE_INVALID)
        
        serializer = CustomUserSerializer(data=request.data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()


        #TODO IF WE NEED TO SEND EMAIL
        # link = f"{'https' if request.is_secure() else 'http'}://{request.META['HTTP_HOST']}/verify-email/{token}"
        # admin_contact = AdminContact.objects.first()
        # send_mail_task.apply_async(kwargs={
        #     'subject': 'Welcome to USICEF',
        #     'html_message': render_to_string('emails/welcome_user.html', context={
        #         'link': link,
        #         'user_name': user.get_full_name(),
        #         'admin_email': admin_contact.email if admin_contact else ''
        #     }),
        #     'recipient_list': [user.email],
        # })
        return success_response(data=serializer.data, extra_data={'token': get_jwt_auth_token(user)})





class RefreshTokenView(CustomGenericView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = TokenRefreshSerializer
    www_authenticate_realm = 'api'

    def get_authenticate_header(self, request):
        return '{0} realm="{1}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user_data = TokenBackend(
                settings.SIMPLE_JWT['ALGORITHM'],
                settings.SIMPLE_JWT['SIGNING_KEY']).decode(serializer.validated_data['access'])
            user = CustomUser.objects.get(id=user_data['user_id'])
            if not user.is_active:
                raise Exception(USER_NOT_ACTIVE)
        except Exception as e:
            raise InvalidToken(str(e))
        return success_response(extra_data=serializer.validated_data)

class OTPView(CustomAPIView):
    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = (AllowAny, )
            self.throttle_scope = 'OTP'
        super().initial(request, *args, **kwargs)

    def get(self, request):
        """
        to send OTP
        """
        otp = create_otp(6)
        mobile = '+'+ request.GET.get('mobile_number')
        mobile = phonenumber_validator(mobile)
        payload = {
            'mobile_number': mobile,
            'otp': otp,
            'exp': int((timezone.now() + timezone.timedelta(minutes=5)).timestamp())
        }
        token = TokenBackend(
            settings.SIMPLE_JWT['ALGORITHM'],
            settings.SIMPLE_JWT['SIGNING_KEY']).encode(payload)
        
        #implement the tulio otp sending option
        message = OTP_SENDING_TEXT.format(otp)
        send_transactional_sms(mobile, message)
        return success_response(message=CODE_SENT, data={'token': token})

    # @transaction.atomic
    # def post(self, request):
    #     """
    #     to change mobile number
    #     """
    #     otp_payload = TokenBackend(
    #         settings.SIMPLE_JWT['ALGORITHM'],
    #         settings.SIMPLE_JWT['SIGNING_KEY']).decode(request.data['token'])
    #     if str(request.user.id) != otp_payload['user']:
    #         raise CustomException(INVALID_TOKEN)
    #     if not (otp_payload['otp'] == request.data['otp'] or (settings.ENV == 'development' and request.data['otp'] == '111111')):
    #         raise CustomException(INVALID_CODE)
    #     request.user.is_mobile_verified = True
    #     request.user.save(update_fields=['is_mobile_verified'])
    #     return success_response(message=MOBILE_VERIFIED)


class FrequentlyAskedQuestionBaseView(CustomGenericView):
    permission_classes = (IsSuperUser,)
    queryset = FrequentlyAskedQuestion.objects.all()
    serializer_class = FrequentlyAskedQuestionSerializer

    def initial(self, request, *args, **kwargs):
        if request.method == 'GET':
            self.permission_classes = (AllowAny,)
        super().initial(request, *args, **kwargs)


class FrequentlyAskedQuestionList(FrequentlyAskedQuestionBaseView, CustomListModelMixin,
                                  CustomCreateModelMixin):

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FrequentlyAskedQuestionDetail(FrequentlyAskedQuestionBaseView, CustomRetrieveModelMixin,
                                    CustomUpdateModelMixin, CustomDestroyModelMixin):

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @transaction.atomic
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UserList(CustomAPIView, BaseListView):
    paginate_by = 20
    permission_classes = (IsSuperUser,)

    def get(self, request, *args, **kwargs):
        qs = CustomUser.objects.filter(is_superuser=False, is_staff=False, is_active=True)
        # TODO: Enforce this filter if CustomerUser model have a user_type field.
        # if request.query_params.get('type'):
        #     qs = qs.filter(current_user_type=request.query_params['type'])
        if request.query_params.get('term'):
            qs = qs.filter(email__icontains=request.query_params['term'])
        context = self.get_context_data(object_list=qs)
        return JsonResponse({
            'results': [
                {'id': str(obj.id), 'text': str(obj.email)}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })
    

""" m2 api -----------> """

"""base view of shop here we can also register the shop"""
class ShopListView(CustomGenericView,CustomListModelMixin,CustomCreateModelMixin):
    permission_classes = (IsAuthenticated,)
    queryset = ProprietorShop.objects.all()
    serializer_class = ShopSerializers
    distance_filter_field = 'location'
    filter_backends = (SearchFilter,DistanceToPointFilter,)
    search_fields = ('shop_name','user__id',)
    

    def initial(self, request, *args, **kwargs):
        if not request.method == "GET":
            print(request.method)
            self.permission_classes = (IsShopOwnerIsNot,)
        return super().initial(request, *args, **kwargs)
    
    """list all the shop details"""
    def get(self, request, *args, **kwargs):
        #here the list serializers is called
        self.serializer_class = ShopListSerializers
        return self.list(request, *args, **kwargs)
    
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


"""here we can retrieve and delete the shop data"""
class ShopDetailView(CustomGenericView,CustomRetrieveModelMixin,CustomDestroyModelMixin):
    permission_classes = (IsShopOwnerIsNot,)
    queryset = ProprietorShop.objects.all()
    serializer_class = ShopSerializers

    def initial(self, request, *args, **kwargs):
        if request.method == "GET":
            self.permission_classes = (IsAuthenticated,)
        return super().initial(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(
            id = kwargs['pk']
        ).only(
            'is_active',
            'is_job_live'
        ).first()

        if instance.is_active and instance.is_job_live:
            raise ValidationError({"user":CANNOTPERFORM})
        elif instance.is_active == False:
            raise  ValidationError({"user":"SHOP NOT EXISTS"})
        
        instance = self.get_queryset().filter(
            id = kwargs['pk'],
            is_active = True,
            is_job_live = False
        ).update(
            is_active = False
        )

        return success_response(
            message="SUCCESS"
        )
    
"""here we can list all the available vehicles"""
class VehicleListView(CustomGenericView,CustomListModelMixin,CustomCreateModelMixin):
    permission_classes = (IsDeliveryPersonOrNot,)
    queryset = VehicleDeliveryPerson.objects.filter(is_active = True)
    #todo change this to full vehicle serializers
    serializer_class = VehicleSerializers
    filter_backends = (SearchFilter,)
    search_fields = ('vehicle_number','vehicle_type','user__id',)

    def initial(self, request, *args, **kwargs):
        if request.method == "GET":
            self.permission_classes = (IsAuthenticated,)
        return super().initial(request, *args, **kwargs)
    
    """list all the delivery person details"""
    def get(self, request, *args, **kwargs):
        # here the list serializers is called
        self.serializer_class = VehicleListSerializers
        return self.list(request, *args, **kwargs)
    
    """register the vehicle details"""
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
class VehicleDetailView(CustomGenericView,CustomRetrieveModelMixin,CustomDestroyModelMixin):
    permission_classes = (IsDeliveryPersonOrNot,)
    queryset = VehicleDeliveryPerson.objects.all()
    serializer_class = VehicleSerializers

    def initial(self, request, *args, **kwargs):
        if request.method == "GET":
            self.permission_classes = (IsAuthenticated,)
        return super().initial(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        pass





    