class CountryModel:
    # instance attribute
    def __init__(self, countryID,countryName="",isActive=True):
        self.countryID=countryID
        self.countryName=countryName
        self.isActive = isActive
        