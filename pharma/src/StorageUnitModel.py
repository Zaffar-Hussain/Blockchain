class StorageUnitModel:
    # instance attribute
    def __init__(self, storageUnitID,storageUnitName="",address1="",address2="",city="",state="",pincode="",countryID="",phone1="",phone2="",mobileNumber="",emailID1="",emailID2="",contactPersonName="",contactPersonNumber="",contactPersonEmailID="",isActive=True, countryModel = None):
        self.storageUnitID=storageUnitID
        self.storageUnitName=storageUnitName
        self.address1 = address1
        self.address2=address2
        self.city=city
        self.state = state
        self.pincode=pincode
        self.countryID=countryID
        self.phone1 = phone1
        self.phone2=phone2
        self.mobileNumber=mobileNumber
        self.emailID1 = emailID1
        self.emailID2=emailID2
        self.contactPersonName=contactPersonName
        self.contactPersonNumber = contactPersonNumber
        self.contactPersonEmailID=contactPersonEmailID
        self.isActive=isActive
        self.countryModel = countryModel
       
        