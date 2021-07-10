from .clinic_base import ClinicBase
from . import cardiology, dentistry, dermatology, ear_nose_throat, gastroenterology, neurology, nutrition, oncology, ophthalmology,  urology
from .cardiology import Cardiology
from .dentistry import Dentistry
from .dermatology import Dermatology
from .ear_nose_throat import EarNoseThroat
from .gastroenterology import Gastroenterology
from .neurology import Neurology
from .nutrition import Nutrition
from .oncology import Oncology
from .ophthalmology import Ophthalmology
from .urology import Urology

# cardiology
# dentistry
# dermatology
# ear_nose_throat
# gastroenterology
# neurology
# nutrition
# oncology
# ophthalmology
# urology

list_clinic = [Cardiology(), Dentistry(), Dermatology(), EarNoseThroat(),
               Gastroenterology(), Neurology(), Nutrition(), Oncology(), Ophthalmology(), Urology()]

def get_clinic_by_id(id_clinic)->ClinicBase:
    if 0 > id_clinic or id_clinic >= 10:
        return None
    return list_clinic[id_clinic-1]