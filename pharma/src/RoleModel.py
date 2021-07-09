class RoleModel:
    # instance attribute
    def __init__(self, roleID, roleName="", canRole=False,canUser=False, canCountry=False, canStorageUnit=False,
                 canManufacture=False, canMedicine=False, canBlockChainGeneration=None,
                 canBlockChainReport=False, canDeviceDataReport=False, canMedicineExpiryDateReport=False, canMedicineReport=False,
                 canStorageUnitReport=False, canManufactureReport=False, canDeviceDataListing=False, canBlockChainDiscrepancy=False):
        self.roleID=roleID
        self.roleName=roleName
        self.canRole = canRole
        self.canUser = canUser
        self.canCountry=canCountry
        self.canStorageUnit=canStorageUnit
        self.canManufacture=canManufacture
        self.canMedicine=canMedicine
        self.canBlockChainGeneration = canBlockChainGeneration
        self.canBlockChainReport = canBlockChainReport
        self.canDeviceDataReport = canDeviceDataReport
        self.canMedicineExpiryDateReport = canMedicineExpiryDateReport
        self.canMedicineReport = canMedicineReport
        self.canStorageUnitReport = canStorageUnitReport
        self.canManufactureReport = canManufactureReport
        self.canDeviceDataListing = canDeviceDataListing
        self.canBlockChainDiscrepancy = canBlockChainDiscrepancy