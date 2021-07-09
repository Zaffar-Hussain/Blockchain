class UserModel:
    # instance attribute
    def __init__(self, userID,  emailid="", password="",userName="",  roleID=0 , isActive=False,roleModel=None):
        self.userID=userID
       
        self.emailid = emailid
        self.password=password
        self.userName=userName
        self.roleID = roleID
        
        self.isActive=isActive
        self.roleModel=roleModel
        