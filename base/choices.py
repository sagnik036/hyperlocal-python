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
    PR = ("PR","PROPRIETOR")
    DP = ("DP","DELIVERYPERSON")

class VehicleType(ChoiceEnum):
    TW = ("TW","TWO-WHEELER")
    THW = ("THW","THREE-WHEELER")
    FW = ("FW","FOUR-WHEELER")
    OT = ("OT","OTHER")



