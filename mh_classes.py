import data_enums as dae


class MetaHuman:
    def __init__(self, mh_name:str,ethnic_group:dae.EthnicGroup,age_category:dae.AgeCategory,gender:dae.Genders):
        self.mh_name = mh_name
        self.ethnic_group = ethnic_group
        self.age_category = age_category
        self.gender = gender

