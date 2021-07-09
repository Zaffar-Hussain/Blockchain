class FoodModel:
    # instance attribute
    def __init__(self, foodID, foodName="", usage="", substances="", temperature=0, humidity=0, expiryDate =None, price=0 ,manufactureID=0, storageUnitID=0,  isBlockChainGenerated=False, hash="", prevHash="", timestamp=None):
        self.foodID=foodID
        self.foodName=foodName
        self.usage = usage
        self.substances = substances
        self.temperature = temperature
        self.humidity = humidity
        self.expiryDate = expiryDate
        self.price = price
        self.manufactureID = manufactureID
        self.storageUnitID = storageUnitID
        
        self.isBlockChainGenerated = isBlockChainGenerated
        self.hash = hash
        self.prevHash = prevHash
        self.timestamp =timestamp
        

