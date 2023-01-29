from enum import Enum


class ChoiceEnum(Enum):
    @classmethod
    def get_value(cls, member):
        return cls[member].value[0]

    @classmethod
    def get_choices(cls):
        return tuple(x.value for x in cls)


class NotificationType(ChoiceEnum):
    tnc_updated = ('TNC', 'Terms and conditions updated')
    payment_terms_updated = ('PTU', 'Payment terms updated')
    privacy_policy_updated = ('PPU', 'Privacy policy updated')
    admin = ('ADMIN', 'Sent by admin')


class DeviceType(ChoiceEnum):
    ios = ('IOS', 'Iphone')
    android = ('ANDROID', 'Android')
    web = ('WEB', 'Web')


class UserType(ChoiceEnum):
    a = ("1","PROPRIETOR")
    b = ("2","DELIVERYPERSON")

class VehicleType(ChoiceEnum):
    a = ("1","TWO-WHEELER")
    b = ("2","THREE-WHEELER")
    c = ("3","FOUR-WHEELER")
    d = ("4","OTHER")



