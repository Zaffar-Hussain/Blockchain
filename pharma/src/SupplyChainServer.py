from flask import Flask, request, render_template, redirect, url_for, session
import os
import pypyodbc

from CountryModel import CountryModel
from RoleModel import RoleModel
from UserModel import UserModel
from Constants import connString
from StorageUnitModel import StorageUnitModel
from FoodManufactureModel import FoodManufactureModel
from FoodModel import FoodModel

import pandas as pd
import hashlib
import json
import threading
import time
import datetime 
import qrcode


app = Flask(__name__)
app.secret_key = "MySecret"
ctx = app.app_context()
ctx.push()




with ctx:
    pass

userName = ""
roleObject = None
globalRoleObject = None
message = ""
msgType = ""

def getIoTData():
    while True:
        iotdata = "010000143.031.0"
        deviceID = iotdata[0:3]
        storageUnitID = iotdata[3:7]
        temperature = iotdata[7:11]
        humidity = iotdata[11:15]
        createdDateTime = str(datetime.datetime.now()).split()[0]
        conn1 = pypyodbc.connect(connString, autocommit=True)
        cur1 = conn1.cursor()
        
        
        sqlcmd = "INSERT INTO DeviceDataDetails(deviceID, foodID,temperature, humidity, createdDateTime) VALUES('"+deviceID+"', '"+storageUnitID+"','"+temperature+"', '"+str(humidity)+"' ,'"+str(createdDateTime)+"')"
        cur1.execute(sqlcmd)
        cur1.commit()
        conn1.close()
        time.sleep(300)

t1 = threading.Thread(target=getIoTData, args=())
t1.start()


def initialize():
    global message, msgType
    message = ""
    msgType=""

def processRole(optionID):
    print(roleObject.canRole, roleObject.canUser,roleObject.canDeviceDataListing,">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>......")
    if optionID == 10 :
        if roleObject.canRole == False :
            return False
    if optionID == 20 :
        if roleObject.canUser == False :
            return False
    if optionID == 30 :
        if roleObject.canCountry == False :
            return False
    if optionID == 40 :
        if roleObject.canStorageUnit == False :
            return False
    if optionID == 50 :
        if roleObject.canManufacture == False :
            return False
    if optionID == 60 :
        if roleObject.canMedicine == False :
            return False
    if optionID == 70 :
        if roleObject.canBlockChainGeneration == False :
            return False
    if optionID == 80 :
        if roleObject.canBlockChainReport == False :
            return False
    if optionID == 90 :
        if roleObject.canDeviceDataReport == False :
            return False
    if optionID == 100 :
        if roleObject.canMedicineExpiryDateReport == False :
            return False
    if optionID == 110 :
        if roleObject.canMedicineReport == False :
            return False

    if optionID == 120 :
        if roleObject.canStorageUnitReport == False :
            return False
    if optionID == 130 :
        if roleObject.canManufactureReport == False :
            return False
    if optionID == 140 :
        if roleObject.canDeviceDataListing == False :
            return False
    if optionID == 150 :
        if roleObject.canBlockChainDiscrepancy == False :
            return False

    return True

@app.route('/')
def index():
    global userID, userName
    return render_template('Login.html')  # when the home page is called Index.hrml will be triggered.

@app.route('/processLogin', methods=['POST'])
def processLogin():
    global userID, userName, roleObject, globalRoleObject
    emailid= request.form['emailid']
    password= request.form['password']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM UserTable WHERE emailid = '"+emailid+"' AND password = '"+password+"' AND isActive = 1"; 
    
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    
    cur1.commit()
    if not row:
        return render_template('Login.html', processResult="Invalid Credentials")
    userID = row[0]
    emailid = row[3]
    
    cur2 = conn1.cursor()
    sqlcmd2 = "SELECT * FROM Role WHERE RoleID = '"+str(row[4])+"'"; 
    cur2.execute(sqlcmd2)
    row2 = cur2.fetchone()
   
    if not row2:
        return render_template('Login.html', processResult="Invalid Role")
    
    roleObject = RoleModel(row2[0], row2[1],row2[2],row2[3],row2[4],row2[5], row2[6],row2[7],row2[8],row2[9],row2[10], row2[11],row2[12],row2[13],row2[14],row2[15],row2[16])
    globalRoleObject = roleObject
    return render_template('Dashboard.html')


@app.context_processor
def inject_role():
    global globalUserObject, globalRoleObject

    return dict(globalRoleObject=globalRoleObject)


@app.route("/ChangePassword")
def changePassword():
    global userID, userName
    return render_template('ChangePassword.html')

@app.route("/ProcessChangePassword", methods=['POST'])
def processChangePassword():
    global userID, userName
    oldPassword= request.form['oldPassword']
    newPassword= request.form['newPassword']
    confirmPassword= request.form['confirmPassword']
    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM UserTable WHERE userName = '"+userName+"' AND password = '"+oldPassword+"'"; 
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template('ChangePassword.html', msg="Invalid Old Password")
    
    if newPassword.strip() != confirmPassword.strip() :
       return render_template('ChangePassword.html', msg="New Password and Confirm Password are NOT same")
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cur2 = conn2.cursor()
    sqlcmd2 = "UPDATE UserTable SET password = '"+newPassword+"' WHERE userName = '"+userName+"'"; 
    cur1.execute(sqlcmd2)
    cur2.commit()
    return render_template('ChangePassword.html', msg="Password Changed Successfully")


@app.route("/Dashboard")
def Dashboard():
    global userID, userName
    return render_template('Dashboard.html')






@app.route("/UserListing")

def UserListing():
    global userID, userName, roleObject
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType="Error"
        return redirect(url_for('Error'))
    canRole = processRole(20)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType="Error"
        return redirect(url_for('Error'))


    initialize()
    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd1 = "SELECT userID,  emailID,userName, roleID FROM UserTable WHERE userName LIKE '"+searchData+"%'"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break

        conn3 = pypyodbc.connect(connString, autocommit=True)
        cursor3 = conn3.cursor()
        print("dbrow[3]", dbrow[3])
        temp = str(dbrow[3])
        sqlcmd3 = "SELECT * FROM Role WHERE roleID = '"+temp+"'"
        print(sqlcmd3)
        cursor3.execute(sqlcmd3)
        rolerow = cursor3.fetchone()

        roleObj = None
        if rolerow:
           roleModel = RoleModel(rolerow[0], rolerow[1])
        else:
           print("Role Row is Not Available")

        row = UserModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3], roleModel=roleModel)

        records.append(row)
    cursor.close()
    conn.close()
    return render_template('UserListing.html', records=records, searchData=searchData, roleObject=roleObject)


@app.route("/UserOperation")
def UserOperation():

    global userID, userName

    global message, msgType, roleObject
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access User"
        msgType="Error"
        return redirect(url_for('Information'))

    operation = request.args.get('operation')
    unqid = ""
    roleModel=""


    rolesDDList = []

    conn4 = pypyodbc.connect(connString, autocommit=True)
    cursor4 = conn4.cursor()
    sqlcmd4 = "SELECT * FROM Role"
    cursor4.execute(sqlcmd4)
    print("sqlcmd4???????????????????????????????????????????????????????/", sqlcmd4)
    while True:
        roleDDrow = cursor4.fetchone()
        if not roleDDrow:
            break
        print("roleDDrow[1]>>>>>>>>>>>>>>>>>>>>>>>>>", roleDDrow[1])
        roleDDObj = RoleModel(roleDDrow[0], roleDDrow[1])
        rolesDDList.append(roleDDObj)


    row = UserModel(0)

    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM UserTable WHERE UserID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        dbrow = cursor.fetchone()
        if dbrow:

            conn3 = pypyodbc.connect(connString, autocommit=True)
            cursor3 = conn3.cursor()
            temp = str(dbrow[4])
            sqlcmd3 = "SELECT * FROM Role WHERE RoleID = '"+temp+"'"
            cursor3.execute(sqlcmd3)
            rolerow = cursor3.fetchone()
            roleModel = RoleModel(0)
            if rolerow:
               roleModel = RoleModel(rolerow[0],rolerow[1])
            else:
               print("Role Row is Not Available")
            print(dbrow)
            row = UserModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], roleModel=roleModel)

    return render_template('UserOperation.html', row = row, operation=operation, rolesDDList=rolesDDList )




@app.route("/ProcessUserOperation",methods = ['POST'])
def processUserOperation():
    global userName, userID
    operation = request.form['operation']
    unqid = request.form['unqid'].strip()
    if operation != "Delete":
        emailid= request.form['emailid']
        password=request.form['password']
        userName= request.form['userName']
        roleID=request.form['roleID']
        isActive = 0
        if request.form.get("isActive") != None :
            isActive = 1
        roleID= request.form['roleID']


    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()


    if operation == "Create" :
        sqlcmd = "INSERT INTO UserTable(emailid, password,userName, roleID, isActive) VALUES('"+emailid+"', '"+password+"','"+userName+"', '"+str(roleID)+"' ,'"+str(isActive)+"')"
    if operation == "Edit" :
        sqlcmd = "UPDATE UserTable SET  emailid = '"+emailid+"', password = '"+password+"',userName='"+userName+"',  roleID = '"+str(roleID)+"',isActive = '"+str(isActive)+"' WHERE UserID = '"+unqid+"'"
    if operation == "Delete" :

        sqlcmd = "DELETE FROM UserTable WHERE UserID = '"+unqid+"'"

    if sqlcmd == "" :
        return redirect(url_for('Information'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    return redirect(url_for("UserListing"))







'''
    Role Operation Start
'''

@app.route("/RoleListing")
def RoleListing():

    global message, msgType
    print("roleObject>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", roleObject)
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('Information'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))

    searchData = request.args.get('searchData')
    print(searchData)
    if searchData == None:
        searchData = "";
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM Role WHERE roleName LIKE '"+searchData+"%'"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        row2 = cursor.fetchone()
        if not row2:
            break

        row = RoleModel(row2[0], row2[1],row2[2],row2[3],row2[4],row2[5], row2[6],row2[7],row2[8],row2[9],row2[10], row2[11],row2[12],row2[13],row2[14],row2[15])


        records.append(row)

    return render_template('RoleListing.html', records=records, searchData=searchData)

@app.route("/RoleOperation")
def RoleOperation():

    global message, msgType
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('/'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))

    operation = request.args.get('operation')
    unqid = ""
    row = RoleModel(0, "",0,0,0,0)
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()


        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM Role WHERE RoleID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            row2 = cursor.fetchone()
            if not row2:
                break
            row = RoleModel(row2[0], row2[1],row2[2],row2[3],row2[4],row2[5], row2[6],row2[7],row2[8],row2[9],row2[10], row2[11],row2[12],row2[13],row2[14],row2[15],row2[16])


    return render_template('RoleOperation.html', row = row, operation=operation )


@app.route("/ProcessRoleOperation", methods=['POST'])
def ProcessRoleOperation():
    global message, msgType
    if roleObject == None:
        message = "Application Error Occurred"
        msgType="Error"
        return redirect(url_for('/'))
    canRole = processRole(10)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType="Error"
        return redirect(url_for('Information'))


    print("ProcessRole")

    operation = request.form['operation']
    if operation != "Delete" :
        roleName = request.form['roleName']
        canRole = 0
        canUser = 0
        canCountry = 0
        canStorageUnit = 0
        canManufacture = 0
        canMedicine=0

        canBlockChainGeneration = 0
        canBlockChainReport = 0
        canDeviceDataReport = 0
        canMedicineExpiryDateReport = 0
        canMedicineReport = 0
        canStorageUnitReport = 0
        canManufactureReport = 0
        canDeviceDataListing = 0
        canBlockChainDiscrepancy = 0
        if request.form.get("canBlockChainGeneration") != None :
            canBlockChainGeneration = 1
        if request.form.get("canBlockChainReport") != None :
            canBlockChainReport = 1
        if request.form.get("canDeviceDataReport") != None :
            canDeviceDataReport = 1
        if request.form.get("canMedicineExpiryDateReport") != None :
            canMedicineExpiryDateReport = 1
        if request.form.get("canMedicineReport") != None :
            canMedicineReport = 1
        if request.form.get("canStorageUnitReport") != None :
            canStorageUnitReport = 1
        if request.form.get("canManufactureReport") != None :
            canManufactureReport = 1
        if request.form.get("canDeviceDataListing") != None :
            canDeviceDataListing = 1

        if request.form.get("canRole") != None :
            canRole = 1
        if request.form.get("canUser") != None :
            canUser = 1
        if request.form.get("canCountry") != None :
            canCountry = 1
        if request.form.get("canStorageUnit") != None :
            canStorageUnit = 1
        if request.form.get("canManufacture") != None :
            canManufacture = 1
        if request.form.get("canMedicine") != None :
            canMedicine = 1
        if request.form.get("canBlockChainDiscrepancy") != None :
            canBlockChainDiscrepancy = 1


    print(1)
    unqid = request.form['unqid'].strip()
    print(operation)
    conn3 = pypyodbc.connect(connString, autocommit=True)
    cur3 = conn3.cursor()


    sqlcmd = ""
    if operation == "Create" :
        sqlcmd = "INSERT INTO Role (roleName, canRole, canUser, canCountry, canStorageUnit, canManufacture," \
                 "canMedicine, canBlockChainGeneration,canBlockChainReport, canDeviceDataReport, canMedicineExpiryDateReport, " \
                 "canMedicineReport, canStorageUnitReport, canManufactureReport, canDeviceDataListing, canBlockChainDiscrepancy) " \
                 "VALUES ('"+roleName+"', '"+str(canRole)+"', '"+str(canUser)+"', '"+str(canCountry)+"', " \
                  "'"+str(canStorageUnit)+"', '"+str(canManufacture)+"', '"+str(canMedicine)+"', " \
                "'" + str(canBlockChainGeneration) + "', '" + str(canBlockChainReport) + "', '" + str(canDeviceDataReport) + "', " \
                "'" + str(canMedicineExpiryDateReport) + "', '" + str(canMedicineReport) + "', '" + str(canStorageUnitReport) + "', " \
                "'" + str(canManufactureReport) + "', '" + str(canDeviceDataListing) + "', '"+str(canBlockChainDiscrepancy)+"')"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE Role SET roleName = '"+roleName+"', canRole = '"+str(canRole)+"', canUser = '"+str(canUser)+"', " \
                "canCountry = '"+str(canCountry)+"', canStorageUnit = '"+str(canStorageUnit)+"', canManufacture = '"+str(canManufacture)+"', " \
                "canMedicine = '"+str(canMedicine)+"', " \
                "canBlockChainGeneration = '" + str(canBlockChainGeneration) + "', canBlockChainReport = '" + str(canBlockChainReport) + "', " \
                "canDeviceDataReport = '" + str(canDeviceDataReport) + "', " \
                "canMedicineExpiryDateReport = '" + str(canMedicineExpiryDateReport) + "', canMedicineReport = '" + str(canMedicineReport) + "', canStorageUnitReport = '" + str(canStorageUnitReport) + "', " \
                "canManufactureReport = '" + str(canManufactureReport) + "', canDeviceDataListing = '" + str(canDeviceDataListing) + "', canBlockChainDiscrepancy = '"+str(canBlockChainDiscrepancy)+"' WHERE RoleID = '"+unqid+"'"
    if operation == "Delete" :
        conn4 = pypyodbc.connect(connString, autocommit=True)
        cur4 = conn4.cursor()
        sqlcmd4 = "SELECT roleID FROM UserTable WHERE roleID = '"+unqid+"'"
        cur4.execute(sqlcmd4)
        dbrow4 = cur4.fetchone()
        if dbrow4:
            message = "You can't Delete this Role Since it Available in Users Table"
            msgType="Error"
            return redirect(url_for('Information'))

        sqlcmd = "DELETE FROM Role WHERE RoleID = '"+unqid+"'"
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Information'))
    cur3.execute(sqlcmd)
    cur3.commit()

    return redirect(url_for('RoleListing'))

'''
    Role Operation End
'''

@app.route("/CountryListing")

def CountryListing():
    global userID, userName, roleObject
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(30)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))

    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM CountryDetails"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = CountryModel(dbrow[0], dbrow[1], dbrow[2])
        records.append(row)
    return render_template('CountryListing.html', records=records)


@app.route("/CountryOperation")
def CountryOperation():
    operation = request.args.get('operation')
    unqid = ""

    row = CountryModel(0, "", "")

    row = None
    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM CountryDetails WHERE countryID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row =CountryModel(dbrow[0], dbrow[1], dbrow[2])

    return render_template('CountryOperation.html', row = row, operation=operation )




@app.route("/ProcessCountryOperation",methods = ['POST'])
def processCountryOperation():
    operation = request.form['operation']
    if operation != "Delete" :
        countryName= request.form['countryName']


        isActive=0
        if request.form.get("isActive") != None :
            isActive = 1


    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()


    if operation == "Create" :
        sqlcmd = "INSERT INTO CountryDetails(countryName,isActive) VALUES('"+countryName+"' ,'"+str(isActive)+"' )"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE CountryDetails SET countryName = '"+countryName+"'  WHERE countryID = '"+unqid+"'"
    if operation == "Delete" :
        print("delete")
        sqlcmd = "DELETE FROM CountryDetails WHERE countryID = '"+unqid+"'"
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('UploadDataListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("CountryListing"))



@app.route("/StorageUnitListing")

def StorageUnitListing():
    global userID, userName, roleObject
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(40)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM StorageUnitDetails"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = StorageUnitModel(dbrow[0], dbrow[1], dbrow[2],dbrow[3],dbrow[4], dbrow[5], dbrow[6],dbrow[7],dbrow[8], dbrow[9], dbrow[10],dbrow[11],dbrow[12], dbrow[13], dbrow[14],dbrow[15],dbrow[16])
        records.append(row)
    return render_template('StorageUnitListing.html', records=records)

@app.route("/StorageUnitOperation")
def StorageUnitOperation():
    operation = request.args.get('operation')
    unqid = ""
    print("inside storage")
    row = StorageUnitModel(0, "", "","","","", "","","","", "","","","", "","","")
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM CountryDetails ORDER BY countryName"
    cursor.execute(sqlcmd1)
    countries=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        country = CountryModel(dbrow[0], dbrow[1])
        countries.append(country)


    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM StorageUnitDetails WHERE storageUnitID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = StorageUnitModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3],dbrow[4], dbrow[5], dbrow[6],dbrow[7],dbrow[8], dbrow[9], dbrow[10],dbrow[11],dbrow[12], dbrow[13], dbrow[14],dbrow[15],dbrow[16])



    return render_template('StorageUnitOperation.html', row = row, operation=operation,countries=countries )




@app.route("/ProcessStorageUnitOperation",methods = ['POST'])
def processStorageUnitOperation():
    operation = request.form['operation']
    if operation != "Delete" :
        storageUnitName= request.form['storageUnitName']
        address1 = request.form['address1']
        address2= request.form['address2']
        city = request.form['city']
        state= request.form['state']
        pincode = request.form['pincode']
        countryID= request.form['countryID']
        phone1 = request.form['phone1']
        phone2= request.form['phone2']
        mobileNumber = request.form['mobileNumber']
        emailID1= request.form['emailID1']
        emailID2 = request.form['emailID2']
        contactPersonName= request.form['contactPersonName']
        contactPersonNumber= request.form['contactPersonNumber']
        contactPersonEmailID = request.form['contactPersonEmailID']
        isActive = 0
        if request.form.get("isActive") != None :
            isActive = 1

    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()


    if operation == "Create" :
        sqlcmd = "INSERT INTO StorageUnitDetails(storageUnitName,address1,address2,city,state,pincode,countryID,phone1,phone2,mobileNumber,emailID1,emailID2,contactPersonName,contactPersonNumber,contactPersonEmailID,isActive) VALUES('"+storageUnitName+"' ,'"+address1+"','"+address2+"' ,'"+city+"','"+state+"' ,'"+str(pincode)+"','"+countryID+"' ,'"+phone1+"','"+phone2+"' ,'"+mobileNumber+"','"+emailID1+"' ,'"+emailID2+"','"+contactPersonName+"' ,'"+contactPersonNumber+"','"+contactPersonEmailID+"','"+str(isActive)+"' )"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE StorageUnitDetails SET storageUnitName ='"+storageUnitName+"',address1 = '"+address1+"',address2 = '"+address2+"',city = '"+city+"',state = '"+state+"',pincode = '"+pincode+"',countryID = '"+countryID+"',phone1 = '"+phone1+"',phone2 ='"+phone2+"',mobileNumber='"+mobileNumber+"',emailID1='"+emailID1+"',emailID2='"+emailID2+"',contactPersonName='"+contactPersonName+"',contactPersonNumber = '"+contactPersonNumber+"',contactPersonEmailID='"+contactPersonEmailID+"',isActive='"+str(isActive)+"'   WHERE storageUnitID = '"+unqid+"'"
    if operation == "Delete" :
        print("delete")
        sqlcmd = "DELETE FROM StorageUnitDetails WHERE storageUnitID = '"+unqid+"'"
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('UploadDataListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("StorageUnitListing"))




@app.route("/FoodManufactureListing")

def FoodManufactureListing():
    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(50)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM FoodManufactureDetails"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = FoodManufactureModel(dbrow[0], dbrow[1], dbrow[2],dbrow[3],dbrow[4], dbrow[5], dbrow[6],dbrow[7],dbrow[8], dbrow[9], dbrow[10],dbrow[11],dbrow[12], dbrow[13], dbrow[14],dbrow[15],dbrow[16],dbrow[17],dbrow[18],dbrow[19],dbrow[20])
        records.append(row)
    return render_template('FoodManufactureListing.html', records=records)


@app.route("/FoodManufactureOperation")
def FoodManufactureOperation():
    print("helllooooo")
    operation = request.args.get('operation')
    unqid = ""

    row = FoodManufactureModel(0, "", "","","","", "","","","", "","","","", "","","")
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM CountryDetails ORDER BY countryName"
    cursor.execute(sqlcmd1)
    countries=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        country = CountryModel(dbrow[0], dbrow[1])
        countries.append(country)


    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM FoodManufactureDetails WHERE manufactureID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = FoodManufactureModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3],dbrow[4], dbrow[5], dbrow[6],dbrow[7],dbrow[8], dbrow[9], dbrow[10],dbrow[11],dbrow[12], dbrow[13], dbrow[14],dbrow[15],dbrow[16],dbrow[17],dbrow[18],dbrow[19],dbrow[20])
    return render_template('FoodManufactureOperation.html', row = row, operation=operation,countries=countries )



@app.route("/ProcessPharmaceuticalManufactureOperation",methods = ['POST'])
def processPharmaceuticalManufactureOperation():
    print("hiiiiiiii")
    operation = request.form['operation']
    if operation != "Delete" :
        manufactureName= request.form['manufactureName']
        address1 = request.form['address1']
        address2= request.form['address2']
        city = request.form['city']
        state= request.form['state']
        pincode = request.form['pincode']
        countryID= request.form['countryID']
        phone1 = request.form['phone1']
        phone2= request.form['phone2']

        mobileNumber = request.form['mobileNumber']
        emailID1= request.form['emailID1']
        emailID2 = request.form['emailID2']
        website = request.form['website']
        contactPersonName= request.form['contactPersonName']
        contactPersonNumber= request.form['contactPersonNumber']
        contactPersonEmailID = request.form['contactPersonEmailID']
        gstNumber= request.form['gstNumber']
        tanNumber= request.form['tanNumber']
        pharmaLicenseNumber = request.form['pharmaLicenseNumber']
        isActive = 0
        if request.form.get("isActive") != None :
            isActive = 1

    unqid = request.form['unqid'].strip()

    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()


    if operation == "Create" :
        sqlcmd = "INSERT INTO FoodManufactureDetails(manufactureName,address1,address2,city,state,pincode,countryID,phone1,phone2,mobileNumber,emailID1,emailID2,website, contactPersonName,contactPersonNumber,contactPersonEmailID,gstNumber,tanNumber,pharmaLicenseNumber,isActive) VALUES('"+manufactureName+"' ,'"+address1+"','"+address2+"' ,'"+city+"','"+state+"' ,'"+str(pincode)+"','"+countryID+"' ,'"+phone1+"','"+phone2+"' ,'"+mobileNumber+"','"+emailID1+"' ,'"+emailID2+"','"+website+"', '"+contactPersonName+"' ,'"+contactPersonNumber+"','"+contactPersonEmailID+"','"+gstNumber+"','"+tanNumber+"','"+pharmaLicenseNumber+"','"+str(isActive)+"' )"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE FoodManufactureDetails SET manufactureName ='"+manufactureName+"',address1 = '"+address1+"',address2 = '"+address2+"',city = '"+city+"',state = '"+state+"',pincode = '"+pincode+"',countryID = '"+countryID+"',phone1 = '"+phone1+"',phone2 ='"+phone2+"',mobileNumber='"+mobileNumber+"',emailID1='"+emailID1+"',emailID2='"+emailID2+"',website='"+website+"', contactPersonName='"+contactPersonName+"',contactPersonNumber = '"+contactPersonNumber+"',contactPersonEmailID='"+contactPersonEmailID+"',gstNumber='"+gstNumber+"',tanNumber='"+tanNumber+"',pharmaLicenseNumber='"+pharmaLicenseNumber+"',isActive='"+str(isActive)+"'  WHERE manufactureID = '"+unqid+"'"
    if operation == "Delete" :
        print("delete")

        sqlcmd = "DELETE FROM FoodManufactureDetails WHERE manufactureID = '"+unqid+"'"

    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('UploadDataListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("FoodManufactureListing"))








@app.route("/FoodListing")

def FoodListing():
    global userID, userName, roleObject
    global errorResult, errType
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(60)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM FoodDetails"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()

        if not dbrow:
            break
        row =FoodModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3], dbrow[4], dbrow[5], dbrow[6], dbrow[7], dbrow[8], dbrow[9])
        records.append(row)
    return render_template('FoodListing.html', records=records)


@app.route("/FoodOperation")
def MedicineListingOperation():

    operation = request.args.get('operation')
    unqid = ""

    row = FoodModel(0, "", "","" , "", "","", "", "")
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM StorageUnitDetails ORDER BY storageUnitName"
    cursor.execute(sqlcmd1)
    storageUnits=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        sunit = StorageUnitModel(dbrow[0], dbrow[1])
        storageUnits.append(sunit)

    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM FoodManufactureDetails ORDER BY manufactureName"
    cursor.execute(sqlcmd1)
    manufactures=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        manu = FoodManufactureModel(dbrow[0], dbrow[1])
        manufactures.append(manu)


    if operation != "Create" :
        unqid = request.args.get('unqid').strip()
        conn2 = pypyodbc.connect(connString, autocommit=True)
        cursor = conn2.cursor()
        sqlcmd1 = "SELECT * FROM FoodDetails WHERE foodID = '"+unqid+"'"
        cursor.execute(sqlcmd1)
        while True:
            dbrow = cursor.fetchone()
            if not dbrow:
                break
            row = FoodModel(dbrow[0], dbrow[1], dbrow[2], dbrow[3],dbrow[4], dbrow[5], str(dbrow[6]).split()[0],dbrow[7],dbrow[8], dbrow[9])
    return render_template('FoodOperation.html', row = row, operation=operation,storageUnits=storageUnits, manufactures=manufactures )




@app.route("/ProcessMedicineOperation",methods = ['POST'])
def ProcessMedicineOperation():
    print("inside ")
    operation = request.form['operation']
    if operation != "Delete" :
        foodName= request.form['foodName']
        usage= request.form['usage']
        substances= request.form['substances']
        temperature= request.form['temperature']
        humidity= request.form['humidity']
        expiryDate= request.form['expiryDate']
        price= request.form['price']
        manufactureID= request.form['manufactureID']
        storageUnitID= request.form['storageUnitID']


    unqid = request.form['unqid'].strip()
    print("process Food")

    conn1 = pypyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()


    if operation == "Create" :
        sqlcmd = "INSERT INTO FoodDetails(foodName, usage, substances, temperature, humidity, expiryDate, price, manufactureID, storageUnitID) VALUES('"+foodName+"' ,'"+usage+"' ,'"+substances+"' , '"+str(temperature)+"' ,'"+str(humidity)+"'  ,'"+str(expiryDate)+"'  ,'"+str(price)+"'  ,'"+str(manufactureID)+"'  ,'"+str(storageUnitID)+"' )"
    if operation == "Edit" :
        print("edit inside")
        sqlcmd = "UPDATE FoodDetails SET foodName = '"+foodName+"', usage = '"+usage+"', substances = '"+substances+"', temperature = '"+str(temperature)+"', humidity = '"+str(humidity)+"', expiryDate = '"+str(expiryDate)+"', price = '"+str(price)+"', manufactureID = '"+str(manufactureID)+"', storageUnitID = '"+str(storageUnitID)+"'  WHERE foodID = '"+unqid+"'"
    if operation == "Delete" :
        print("delete")
        sqlcmd = "DELETE FROM FoodDetails WHERE foodID = '"+unqid+"'"
    print(operation, sqlcmd)
    if sqlcmd == "" :
        return redirect(url_for('Error'))
    cur1.execute(sqlcmd)
    cur1.commit()
    conn1.close()
    #return render_template('UploadDataListing.html', processResult="Success!!!. Data Uploaded. ")
    return redirect(url_for("FoodListing"))






@app.route("/BlockChainGeneration")
def BlockChainGeneration():


    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(70)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))

    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM FoodDetails WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    sqlcmd = "SELECT COUNT(*) FROM FoodDetails WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksNotCreated = dbrow[0]
    return render_template('BlockChainGeneration.html', blocksCreated = blocksCreated, blocksNotCreated = blocksNotCreated)


@app.route("/ProcessBlockchainGeneration", methods=['POST'])
def ProcessBlockchainGeneration():

    global errorResult, errType



    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM FoodDetails WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    blocksCreated = 0
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    prevHash = ""
    print("blocksCreated", blocksCreated)
    if blocksCreated != 0 :
        connx = pypyodbc.connect(connString, autocommit=True)
        cursorx = connx.cursor()
        sqlcmdx = "SELECT * FROM FoodDetails WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY foodID"
        cursorx.execute(sqlcmdx)
        dbrowx = cursorx.fetchone()
        print(2)
        if dbrowx:
            foodID = dbrowx[0]
            conny = pypyodbc.connect(connString, autocommit=True)
            cursory = conny.cursor()
            sqlcmdy = "SELECT Hash FROM FoodDetails WHERE foodID < '"+str(foodID)+"' ORDER BY foodID DESC"
            cursory.execute(sqlcmdy)
            dbrowy = cursory.fetchone()
            if dbrowy:
                print(3)
                prevHash = dbrowy[0]
                print("prevHash1111", prevHash)
            cursory.close()
            conny.close()
        cursorx.close()
        connx.close()
    print("prevHash1111", prevHash)
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT * FROM FoodDetails WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY foodID"
    cursor.execute(sqlcmd)

    while True:
        sqlcmd1 = ""
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        unqid = str(dbrow[0])

        block_serialized = json.dumps(str(dbrow[1])+" "+str(dbrow[2])+" "+str(dbrow[3])+" "+str(dbrow[4])+" "+str(dbrow[5])+" "+str(dbrow[6])+" "+str(dbrow[7])+" "+str(dbrow[8])+" "+str(dbrow[9]), sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()
        timestamp = str(datetime.datetime.now()).split()[0]
        conn1 = pypyodbc.connect(connString, autocommit=True)
        cursor1 = conn1.cursor()
        sqlcmd1 = "UPDATE FoodDetails SET timestamp = '"+timestamp+"', isBlockChainGenerated = 1, hash = '"+block_hash+"', prevHash = '"+prevHash+"' WHERE foodID = '"+unqid+"'"
        cursor1.execute(sqlcmd1)
        cursor1.close()
        conn1.close()
        prevHash = block_hash
    return render_template('BlockchainGenerationResult.html')


@app.route("/BlockChainReport")
def BlockChainReport():

    global errorResult, errType

    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(80)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))

    initialize()
    conn = pypyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()

    sqlcmd1 = "SELECT * FROM FoodDetails WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break


        row = FoodModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10],dbrow[11],dbrow[12],dbrow[13])
        print(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10],dbrow[11],dbrow[12],dbrow[13])
        records.append(row)
        print("row", row)
    return render_template('BlockChainReport.html', records=records)




@app.route("/BlockChainDiscrepancy")
def BlockchainDiscrepancy():
    global globalUserObject, globalRoleObject


    initialize()
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor2 = conn2.cursor()
    sqlcmd2 = "SELECT * FROM FoodDetails ORDER BY foodID"
    cursor2.execute(sqlcmd2)
    records = []
    while True:
        dbrow = cursor2.fetchone()
        if not dbrow:
            break
        block_serialized = json.dumps(
            str(dbrow[1]) + " " + str(dbrow[2]) + " " + str(dbrow[3]) + " " + str(dbrow[4]) + " " + str(
                dbrow[5]) + " " + str(dbrow[6]) + " " + str(dbrow[7]) + " " + str(dbrow[8]) + " " + str(dbrow[9]),
            sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()
        print(block_hash, dbrow[11])
        pdict = {
                'foodName': dbrow[1],
                'usage': dbrow[2],
                'substances': dbrow[3],
                'temperature': dbrow[4],
                'humidity': dbrow[5],
                'expiryDate': dbrow[6],
                'price': dbrow[7],


                'hash': dbrow[11],
                'hash1': block_hash

            }
        records.append(pdict)
    cursor2.close()
    conn2.close()
    return render_template('BlockchainDiscrepancy.html', records=records)






@app.route("/DeviceDataListing")
def DeviceDataListing():
    global userID, userName

    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(140)

    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = '''SELECT createdDateTime, DeviceDataDetails.temperature, DeviceDataDetails.humidity, storageUnitName, uniqueID,  manufactureName, foodName, expiryDate  FROM DeviceDataDetails 
            INNER JOIN FoodDetails ON FoodDetails.foodID = DeviceDataDetails.foodID
            INNER JOIN StorageUnitDetails ON StorageUnitDetails.storageUnitID = FoodDetails.storageUnitID 
            INNER JOIN FoodManufactureDetails ON FoodManufactureDetails.manufactureID = FoodDetails.manufactureID
            ORDER BY createdDateTime DESC'''
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        col = []
        col.append(dbrow[0])
        col.append(dbrow[1])
        col.append(dbrow[2])
        col.append(dbrow[3])


        records.append(col)

        qrCodeFileName = str(dbrow[4])+".png"
        col.append(qrCodeFileName)

        if os.path.exists('static/QRCODE_DATA/'+qrCodeFileName):
            pass
        else:
            #img = qrcode.make("Storage Unit Name : "+dbrow[3]+"\n Temperature : "+str(dbrow[1])+" \n Humidity : "+str(dbrow[2])+ " \n Created DateTime : "+str(dbrow[0]))
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data("Manufacture Name : "+dbrow[5]+"\n Storage Unit Name : "+dbrow[3]+"\n Food Name : "+dbrow[6]+"\n Temperature : "+str(dbrow[1])+" \n Humidity : "+str(dbrow[2])+"\n Expiry Date : "+str(dbrow[7])+ " \n Created DateTime : "+str(dbrow[0]))
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            f = os.path.join('static/QRCODE_DATA', qrCodeFileName)
            img.save(f)

    cursor.close()
    conn2.close()


    return render_template('DeviceDataListing.html', records=records)







@app.route("/DeviceDataReport")
def DeviceDataReport():
    global userID, userName

    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(90)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM FoodDetails ORDER BY foodName"
    cursor.execute(sqlcmd1)
    medicines=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        med = FoodModel(dbrow[0], dbrow[1])
        medicines.append(med)




    return render_template('DeviceDataReport.html', medicines=medicines)


@app.route("/GenerateDeviceDataReport", methods=['POST'])
def GenerateDeviceDataReport():

    foodID= request.form['foodID']


    where = ""
    if foodID == "All":
        pass
    else:
        where = " WHERE DeviceDataDetails.foodID = '"+str(foodID)+"' "


    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = '''SELECT createdDateTime, DeviceDataDetails.temperature, DeviceDataDetails.humidity, storageUnitName, manufactureName, foodName, expiryDate  FROM DeviceDataDetails 
            INNER JOIN FoodDetails ON FoodDetails.foodID = DeviceDataDetails.foodID
            INNER JOIN StorageUnitDetails ON StorageUnitDetails.storageUnitID = FoodDetails.storageUnitID 
            INNER JOIN FoodManufactureDetails ON FoodManufactureDetails.manufactureID = FoodDetails.manufactureID '''+where+''' ORDER BY createdDateTime DESC'''
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        col = []
        col.append(dbrow[0])
        col.append(dbrow[1])
        col.append(dbrow[2])
        col.append(dbrow[3])
        col.append(dbrow[4])
        col.append(dbrow[5])
        col.append(dbrow[6])


        records.append(col)


    cursor.close()
    conn2.close()

    df1 = pd.DataFrame(records,
                       index=None,
                       columns=['Created Date', "Temperature", "Humidity", "Storage Unit Name", "Manufacture Name", "Food Name", "Expiry Date"])
    df1.to_excel("DeviceDataReport.xlsx")

    return redirect(url_for('DeviceDataReport'))











@app.route("/FoodExpiryDateReport")
def FoodExpiryDateReport():
    global userID, userName
    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(100)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))

    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM StorageUnitDetails ORDER BY storageUnitName"
    cursor.execute(sqlcmd1)
    storageunits=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        sunit = StorageUnitModel(dbrow[0], dbrow[1])
        storageunits.append(sunit)

    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM FoodManufactureDetails ORDER BY manufactureName"
    cursor.execute(sqlcmd1)
    manufactures=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        manu = FoodManufactureModel(dbrow[0], dbrow[1])
        manufactures.append(manu)


    return render_template('FoodExpiryDateReport.html', storageunits=storageunits, manufactures=manufactures)


@app.route("/GenerateMedicineExpiryDateReport", methods=['POST'])
def GenerateMedicineExpiryDateReport():
    global userID, userName

    storageUnitID= request.form['storageUnitID']
    manufactureID= request.form['manufactureID']

    where = " WHERE expiryDate < '"+str(datetime.datetime.now()).split()[0]+"'  "
    if storageUnitID == "All":
        if storageUnitID == "All":
            pass
        else:
            where = " AND FoodDetails.manufactureID = '"+str(manufactureID)+"' "
    else:
        where = " AND FoodDetails.storageUnitID = '"+str(storageUnitID)+"' "
        if storageUnitID == "All":
            pass
        else:
            where = " AND FoodDetails.manufactureID = '"+str(manufactureID)+"' "

    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = '''SELECT foodName, usage, substances, temperature, humidity, expiryDate, price, manufactureName, storageUnitName  FROM FoodDetails 
            INNER JOIN FoodManufactureDetails ON FoodManufactureDetails.manufactureID = FoodDetails.manufactureID 
            INNER JOIN StorageUnitDetails ON StorageUnitDetails.storageUnitID = FoodDetails.storageUnitID '''+where+''' ORDER BY foodName'''
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        col = []
        col.append(dbrow[0])
        col.append(dbrow[1])
        col.append(dbrow[2])
        col.append(dbrow[3])
        col.append(dbrow[4])
        col.append(dbrow[5])
        col.append(dbrow[6])
        col.append(dbrow[7])
        col.append(dbrow[8])


        records.append(col)


    cursor.close()
    conn2.close()

    df1 = pd.DataFrame(records,
                       index=None,
                       columns=['Food Name', 'Usage', "Substances", "Temperature", "Humidity", "Expiry Date", "Price", "Manufacture Name", "Storage Unit Name"])
    df1.to_excel("FoodExpiryDateReport.xlsx")

    return redirect(url_for('FoodExpiryDateReport'))



@app.route("/FoodReport")
def FoodReport():
    global userID, userName

    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(110)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))

    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM StorageUnitDetails ORDER BY storageUnitName"
    cursor.execute(sqlcmd1)
    storageunits=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        sunit = StorageUnitModel(dbrow[0], dbrow[1])
        storageunits.append(sunit)

    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM FoodManufactureDetails ORDER BY manufactureName"
    cursor.execute(sqlcmd1)
    manufactures=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        manu = FoodManufactureModel(dbrow[0], dbrow[1])
        manufactures.append(manu)


    return render_template('FoodReport.html')



@app.route("/GenerateMedicineReport", methods=['POST'])
def GenerateMedicineReport():
    global userID, userName

    storageUnitID= request.form['storageUnitID']
    manufactureID= request.form['manufactureID']

    where = ""
    if storageUnitID == "All":
        where = ""
        if storageUnitID == "All":
            where = ""
        else:
            where = " WHERE FoodDetails.manufactureID = '"+str(manufactureID)+"' "
    else:
        where = " WHERE FoodDetails.storageUnitID = '"+str(storageUnitID)+"' "
        if storageUnitID == "All":
            pass
        else:
            where = " AND FoodDetails.manufactureID = '"+str(manufactureID)+"' "

    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = '''SELECT foodName, usage, substances, temperature, humidity, expiryDate, price, manufactureName, storageUnitName  FROM FoodDetails 
            INNER JOIN FoodManufactureDetails ON FoodManufactureDetails.manufactureID = FoodDetails.manufactureID 
            INNER JOIN StorageUnitDetails ON StorageUnitDetails.storageUnitID = FoodDetails.storageUnitID '''+where+''' ORDER BY foodName'''
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        col = []
        col.append(dbrow[0])
        col.append(dbrow[1])
        col.append(dbrow[2])
        col.append(dbrow[3])
        col.append(dbrow[4])
        col.append(dbrow[5])
        col.append(dbrow[6])
        col.append(dbrow[7])
        col.append(dbrow[8])


        records.append(col)


    cursor.close()
    conn2.close()

    df1 = pd.DataFrame(records,
                       index=None,
                       columns=['Food Name', 'Usage', "Substances", "Temperature", "Humidity", "Expiry Date", "Price", "Manufacture Name", "Storage Unit Name"])
    df1.to_excel("FoodReport.xlsx")

    return redirect(url_for('FoodReport'))




@app.route("/StorageUnitReport")
def StorageUnitReport():
    global userID, userName

    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(120)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))


    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM CountryDetails ORDER BY countryName"
    cursor.execute(sqlcmd1)
    countries=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        country = CountryModel(dbrow[0], dbrow[1])
        countries.append(country)


    return render_template('StorageUnitReport.html', countries=countries)

@app.route("/GenerateStorageUnitReport", methods=['POST'])
def GenerateStorageUnitReport():
    global userID, userName

    countryID= request.form['countryID']

    where = ""
    if countryID == "All":
        where = ""
    else:
        where = " WHERE StorageUnitDetails.countryID = '"+str(countryID)+"' "

    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT storageUnitID, storageUnitName,address1,address2,city,state,pincode,StorageUnitDetails.countryID,phone1,phone2,mobileNumber,emailID1,emailID2,contactPersonName,contactPersonNumber,contactPersonEmailID,StorageUnitDetails.isActive, StorageUnitDetails.countryID, countryName  FROM StorageUnitDetails INNER JOIN CountryDetails ON CountryDetails.countryID = StorageUnitDetails.countryID "+where+" ORDER BY countryName, storageUnitName"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        col = []
        col.append(dbrow[18])
        col.append(dbrow[1])
        col.append(dbrow[2])
        col.append(dbrow[3])
        col.append(dbrow[4])
        col.append(dbrow[5])
        col.append(dbrow[6])

        col.append(dbrow[8])
        col.append(dbrow[9])
        col.append(dbrow[10])
        col.append(dbrow[11])
        col.append(dbrow[12])
        col.append(dbrow[13])
        col.append(dbrow[14])
        col.append(dbrow[15])
        col.append(dbrow[16])


        records.append(col)


    cursor.close()
    conn2.close()

    df1 = pd.DataFrame(records,
                       index=None,
                       columns=['Country Name', 'Storage Unit Name', "Address 1", "Address2", "City", "State", "Pincode", "Phone 1", "Phone 2", "Mobile Number", "Email ID1", "Email ID2", "Contact Person Name", "Contact Person Mobile Number", "Contact Person Email ID", "Is Active"])
    df1.to_excel("StorageUnitReport.xlsx")

    return redirect(url_for('StorageUnitReport'))



@app.route("/ManufactureReport")
def ManufactureReport():
    global userID, userName

    global errorResult, errType
    global userID, userName, roleObject
    if roleObject == None:
        errorResult = "Application Error Occurred"
        errType = "Error"
        return redirect(url_for('Error'))
    canRole = processRole(130)
    if canRole == False:
        errorResult = "You Don't Have Permission to Access User"
        errType = "Error"
        return redirect(url_for('Error'))


    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM CountryDetails ORDER BY countryName"
    cursor.execute(sqlcmd1)
    countries=[]
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        country = CountryModel(dbrow[0], dbrow[1])
        countries.append(country)
        
        
    return render_template('ManufactureReport.html', countries=countries)



@app.route("/GenerateManufactureReport", methods=['POST'])
def GenerateManufactureReport():
    global userID, userName
    
    countryID= request.form['countryID']
    
    where = ""
    if countryID == "All":
        where = ""
    else:
        where = " WHERE FoodManufactureDetails.countryID = '"+str(countryID)+"' "
    
    conn2 = pypyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT manufactureID, manufactureName,address1,address2,city,state,pincode,FoodManufactureDetails.countryID,phone1,phone2,mobileNumber,emailID1,emailID2,contactPersonName,contactPersonNumber,contactPersonEmailID,FoodManufactureDetails.isActive, FoodManufactureDetails.countryID, countryName  FROM FoodManufactureDetails INNER JOIN CountryDetails ON CountryDetails.countryID = FoodManufactureDetails.countryID "+where+" ORDER BY countryName, manufactureName"
    print(sqlcmd1)
    cursor.execute(sqlcmd1)
    records = []
    
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        col = []
        col.append(dbrow[18])
        col.append(dbrow[1])
        col.append(dbrow[2])
        col.append(dbrow[3])
        col.append(dbrow[4])
        col.append(dbrow[5])
        col.append(dbrow[6])
        
        col.append(dbrow[8])
        col.append(dbrow[9])
        col.append(dbrow[10])
        col.append(dbrow[11])
        col.append(dbrow[12])
        col.append(dbrow[13])
        col.append(dbrow[14])
        col.append(dbrow[15])
        col.append(dbrow[16])
        

        records.append(col)
        
        
    cursor.close()
    conn2.close()
    
    df1 = pd.DataFrame(records,
                       index=None,
                       columns=['Country Name', 'Manufacture Name', "Address 1", "Address2", "City", "State", "Pincode", "Phone 1", "Phone 2", "Mobile Number", "Email ID1", "Email ID2", "Contact Person Name", "Contact Person Mobile Number", "Contact Person Email ID", "Is Active"])
    df1.to_excel("ManufactureReport.xlsx")
    
    return redirect(url_for('ManufactureReport'))




@app.route("/Information")
def Information():
    global message, msgType
    return render_template('Information.html', msgType=msgType, message = message)


@app.route("/Error")
def Error():
    global errorResult, errType
    print(errorResult, errType, "++++++++++++++++++++++++++++++++++++++++++++")
    return render_template('Error.html', errType=errType, errorResult = errorResult)


if __name__ == "__main__":
    app.run()

