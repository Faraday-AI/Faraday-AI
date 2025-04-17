from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class FitnessLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    ELITE = "elite" 