"""Models package - re-exports all SQLAlchemy models"""

from app.models.patient import Patient, GenderEnum
from app.models.User import User
from app.models.camp import Camp
from app.models.camp_doctor import CampDoctor
from app.models.consultation import Consultation
from app.models.inventory import Inventory
from app.models.medicines import Medicine
from app.models.prescription import Prescription
from app.models.registration import Registration
from app.models.vitals import Vitals

__all__ = [
    "Patient",
    "GenderEnum",
    "Users",
    "Camp",
    "CampDoctor",
    "Consultation",
    "Doctor",
    "Inventory",
    "Medicine",
    "Prescription",
    "Registration",
    "Vitals",
]
