from django.utils import timezone
from django.core.management.utils import get_random_string


def get_extension(filename):
    return f".{filename.split('.')[-1]}"


def get_random_name(filename):
    return f'{get_random_string()}-{int(timezone.now().timestamp() * 1000)}{get_extension(filename)}'


def handle_tnc_document(instance, filename):
    new_filename = f'tnc/{instance.id.hex}/{get_random_name(filename)}'
    return new_filename


def handle_privacy_policy_document(instance, filename):
    new_filename = f'privacy_policy/{instance.id.hex}/{get_random_name(filename)}'
    return new_filename


def handle_payment_term_document(instance, filename):
    new_filename = f'payment_term/{instance.id.hex}/{get_random_name(filename)}'
    return new_filename

def handle_legal_doccuments(instance , filename):
    new_filename = f'legal/{instance.id.hex}/{get_random_name(filename)}'
    return new_filename

def handle_images(instance , filename):
    new_filename = f'images/{instance.id.hex}/{get_random_name(filename)}'
    return new_filename
