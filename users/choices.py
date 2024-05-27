from django.db.models import TextChoices


class SPECIALIZATION_CHOICES(TextChoices):
    GENERAL_PHYSICIAN = "General Physician"
    DERMATOLOGIST = "Dermatologist"
    CARDIOLOGIST = "Cardiologist"


class STATUS_CHOICES(TextChoices):
    AVAILABLE = "Available"
    BUSY = "Busy"
    ON_LEAVE = "On Leave"


class GENDER_CHOICES(TextChoices):
    MALE = "M"
    Female = "F"


class SMOKING_STATUS(TextChoices):
    YES = "Y"
    NO = "N"


class ALCOHOL_CONSUMPTION(TextChoices):
    YES = "Y"
    NO = "N"


class PREFERRED_LANGUAGE(TextChoices):
    ENGLISH = "English"
    YORUBA = "Yoruba"
    IGBO = "Igbo"
    HAUSA = "Hausa"


class GENOTYPES(TextChoices):
    AA = "AA"
    AB = "AB"
    BB = "BB"
    AO = "AO"
    BO = "BO"
    OO = "OO"
    SS = "SS"
    AS = "AS"
    SC = "SC"
    CC = "CC"
    AC = "AC"


class BLOODGROUP(TextChoices):
    A = "A"
    B = "B"
    AB = "AB"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"
