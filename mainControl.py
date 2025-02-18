import sqlite3
import time
import uuid
import essentials as esn
import varscollection 
import userController
import os


DBFPATH = 'database.db'
TABLENAME = 'workDBtrytwo'


# conn = sqlite3.connect('database.db');

def changeState(assignmentID:str, version:int, newState:str):
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {TABLENAME} SET STATE='{newState}',laststatechangedate={time.time()} WHERE assignmentID LIKE \"{assignmentID}\" AND version = {version}")
    conn.commit()



def get_assignment_history(assignmentID, usrIDrequest:str):
    command = f'''
        SELECT version,USERFROM,USERFOR FROM {TABLENAME} where assignmentID LIKE "{assignmentID}";  
    '''

    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    res = cursor.execute(command)
    if not res:
        # res = [0,"Not Found","Not Found",99999999.99,"Not Found"]
        # assignmentID, version, state, desc, fol_name, url
        res = [0]
    else:
        newres = []
        for x in res:
            i,usrFrom,usrFor = x;
            if usrIDrequest != str(usrFrom) and usrIDrequest != str(usrFor):
                # return "Access denied"
                return [0]
            newres.append(i)

        res  = newres


    return res #[Int]

def get_assignment_details(assignmentID, version, usrIDaccess:str):
    command = f'''
        SELECT * FROM "{TABLENAME}" WHERE assignmentID LIKE "{assignmentID}" AND version = {version}; 
    '''

    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    res = cursor.execute(command).fetchone()
    if not res:
        # res = [0,"Not Found","Not Found",99999999.99,"Not Found"]
        # assignmentID, version, state, desc, fol_name, url
        res = [0,0,"NF","NF","NF","NF",0,0,0,"NF","NF"]
    else:
        res = list(res)
        # change the state of the new
        # print(usrIDaccess,type(usrIDaccess))
        # print(res[9],type(res[9]))
        
        if usrIDaccess == str(res[9]): # jika yg memberi tugas mengakses, state tidak diganti
            pass
        elif usrIDaccess == str(res[10]):
            pass # jika yg menerima tugas mengakses, state diganti
            # changeState(assignmentID=assignmentID,version=version,newState='dikerjakan')
        else:
            return [0,0,"Permission Denied","Permission Denied","Permission Denied","Permission Denied",0,0,0,"Permission Denied","Permission Denied"]
 

 
        # cursor.execute(f"UPDATE {TABLENAME} SET STATE='working' WHERE assignmentID LIKE {assignmentID} AND version = {version}")
        # conn.commit()



    return res


def new_assignment(title:str,desc:str,duedateepoch:float,userfrom:str,userfor:str,emailfrom:str,emailfor:str,isForAnyone:bool=False):
    uniqueID = str(uuid.uuid4())

    if isForAnyone:
        uniqueID += '-2b55r5cs'
    # else: 
    #     userExist = userController.fetch_user_by_email(emailfor)
    #     if userExist[0] == "None":
    #         return "ERR: Target user does not exist"
    

    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    folName = f"{uniqueID}-v1"
    command = f'''
        INSERT INTO {TABLENAME} values ("{uniqueID}", 1, 'diberikan', '{title}', '{desc}', '{folName}', {time.time()}, {duedateepoch}, 0, '{userfrom}', '{userfor}','{emailfrom}','{emailfor}' );
    '''
    # print(command)
    res = cursor.execute(command)
    conn.commit()

    # folder creating
    file_loc = os.path.join(varscollection.SUBMIT_FOLDER_PATH,f"{uniqueID}-v1")
    
    if not os.path.exists(file_loc):
        os.mkdir(file_loc)


    esn.send_email(to_=[emailfor],subject="Assignment",msg=f""" New assignment has been added on:\n {varscollection.BASE_URL}/Assignment/{uniqueID}/1?ID={userfor} """)
    esn.send_email(to_=[emailfrom],subject="Assignment",msg=f""" New assignment has been added on:\n {varscollection.BASE_URL}/Assignment/{uniqueID}/1?ID={userfrom} """)

    return f"""{uniqueID}/1"""
    # return ("{uniqueID}", 1, 'diberikan', '{title}', '{desc}', '{folName}', {time.time()}, {duedateepoch}, 0, '{userfrom}', '{userfor}' )
    # return [uniqueID, 1, 'diberikan', title, desc, folName, time.time(), duedateepoch, 0, userfrom, userfor,emailfrom, emailfor ]





def new_revision(AssignmentID,lastVersion,desc:str,duedateepoch:float,usrIDrequest:str):
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()

    lastVersionData = get_assignment_details(AssignmentID,lastVersion,usrIDaccess=usrIDrequest)

    if usrIDrequest != str(lastVersionData[9]):
        return "ERR: You are not the owner of this assignment"
    
    
    if str(lastVersionData[2]).upper() == "SELESAI":
        return "ERR: assignment is done, cannot request revision"
    
    if str(lastVersionData[2]).upper() == "REVISI":
        return "ERR: new Revision or Version of this assignment is online, check history"

    if str(lastVersionData[2]).upper() == "DIKERJAKAN" or str(lastVersionData[2]).upper() == "DIBERIKAN":
        return "ERR: Assignment is not yet submitted, cannot add revision"

    newVersion = lastVersion + 1

    folName = f"{AssignmentID}-v{newVersion}"
    print(folName)
    title = lastVersionData[3]
    userfrom = lastVersionData[9]
    userfor = lastVersionData[10]

    emailfrom = lastVersionData[11]
    emailfor = lastVersionData[12]

    # change the old version to "revisi"
    changeState(assignmentID=AssignmentID,version=lastVersion,newState="revisi")

    command = f'''
        INSERT INTO {TABLENAME} values ("{AssignmentID}", {newVersion}, 'DIBERIKAN', '{title}', '{desc}', '{folName}', {time.time()}, {duedateepoch}, 0, '{userfrom}', '{userfor}', '{emailfrom}','{emailfor}'  )
    '''
    res = cursor.execute(command)
    conn.commit()

    file_loc = os.path.join(varscollection.SUBMIT_FOLDER_PATH,f"{AssignmentID}-v{newVersion}")
        
    if not os.path.exists(file_loc):
        os.mkdir(file_loc)


    esn.send_email(to_=[emailfor],subject="Assignment",msg=f""" New revision request of your assignment has been added on:\n {varscollection.BASE_URL}/Assignment/{AssignmentID}/{newVersion}?ID={userfor} """)
    esn.send_email(to_=[emailfrom],subject="Assignment",msg=f""" New revision request of your assignment has been added on:\n {varscollection.BASE_URL}/Assignment/{AssignmentID}/{newVersion}?ID={userfrom} """)


    return f"{AssignmentID}/{newVersion}"


def submit(AssignmentID:str,version:int,usrIDsubmitter:str):
    data = get_assignment_details(AssignmentID,version=version,usrIDaccess=usrIDsubmitter)
    if str(data[10]) == usrIDsubmitter :
        if str(data[2]).upper() == "DIKERJAKAN":
            changeState(assignmentID=AssignmentID,version=version,newState="menunggu-review")
            esn.send_email(to_=[data[11]],subject="Submitted",msg=f""" File has been submitted on\n assignment: {data[0]},\n version: {data[1]}\n Link:\n {varscollection.BASE_URL}/Assignment/{data[0]}/{data[1]}?ID={data[9]} """)
            esn.send_email(to_=[data[12]],subject="Submitted",msg=f""" File has been submitted on\n assignment: {data[0]},\n version: {data[1]}\n Link:\n {varscollection.BASE_URL}/Assignment/{data[0]}/{data[1]}?ID={data[10]} """)

            return "the assignment is menunggu-review"
        else:
            return "you are not permitted to submit right now"
    else:
        return "You are not permitted to submit in this assginment"

def accept_submit(AssignmentID:str,version:int,usrIDacceptsubmit:str): # Accept the submission
    data = get_assignment_details(AssignmentID,version=version,usrIDaccess=usrIDacceptsubmit)
    if str(data[9]) == usrIDacceptsubmit and str(data[2]).upper() == "MENUNGGU-REVIEW":
        changeState(assignmentID=AssignmentID,version=version,newState="selesai")
        esn.send_email(to_=[data[11]],subject="Submitted",msg=f""" assignment: {data[0]}, version: {data[1]} has been finished\n Link: {varscollection.BASE_URL}/Assignment/{data[0]}/{data[1]}?ID={data[9]}""")
        esn.send_email(to_=[data[12]],subject="Submitted",msg=f""" assignment: {data[0]}, version: {data[1]} has been finished\n Link: {varscollection.BASE_URL}/Assignment/{data[0]}/{data[1]}?ID={data[10]}""")

        return "the assignment is selesai"
    else:
        return "You have no access to make submission in this assignment"


def accept_assign(AssignmentID:str,version:int,usrIDacceptassign:str): # Accept the givenassignment 
    
    print(usrIDacceptassign)
    data = get_assignment_details(AssignmentID,version=version,usrIDaccess=usrIDacceptassign)
    print(data)
    if str(data[10]) == usrIDacceptassign:
        changeState(assignmentID=AssignmentID,version=version,newState="dikerjakan")
        esn.send_email(to_=[data[11]],subject="Submitted",msg=f""" assignment: {data[0]}, version: {data[1]}\n is on work\n Link: {varscollection.BASE_URL}/Assignment/{data[0]}/{data[1]}?ID={data[9]}""")
        esn.send_email(to_=[data[12]],subject="Submitted",msg=f""" assignment: {data[0]}, version: {data[1]}\n is on work\n Link: {varscollection.BASE_URL}/Assignment/{data[0]}/{data[1]}?ID={data[10]}""")

        return "assignment accepted"
    elif str(data[9]) == usrIDacceptassign:
        return "You are the assignment giver"
    else:
        return "The assignment is not for you"
    

def Assignment_Created_By_You_That_Has_Not_Done_Yet(yourUserID:str):
    command = f''' 
        SELECT * FROM "{TABLENAME}" WHERE USERFROM LIKE "{str(yourUserID)}" AND STATE NOT LIKE "selesai" AND STATE NOT LIKE "revisi"; 
    '''

    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    res = cursor.execute(command)
    if not res:
        # res = [0,"Not Found","Not Found",99999999.99,"Not Found"]
        # assignmentID, version, state, desc, fol_name, url
        res = [[0,0,"NF","NF","NF","NF",0,0,0,"NF","NF"]]
    else:
        restemporary = []
        for i in res:
            restemporary.append(list(i))
        res = restemporary

        print(res)
        if len(res) == 0:
            return [[0,0,"Empty","Empty","Empty","Empty",0,0,0,"Empty","Empty"]]
        # print(res)
        # change the state of the new
        # print(usrIDaccess,type(usrIDaccess))
        # print(res[9],type(res[9]))
        
        # if yourUserID == str(res[9]): # jika yg memberi tugas mengakses, state tidak diganti
        #     pass
        # elif yourUserID == str(res[10]):
        #     pass # jika yg menerima tugas mengakses, state diganti
        #     # changeState(assignmentID=assignmentID,version=version,newState='dikerjakan')
        # else:
        #     return [[0,0,"Permission Denied","Permission Denied","Permission Denied","Permission Denied",0,0,0,"Permission Denied","Permission Denied"]]
 
    return res

def Your_Unfinished_Assignment(yourUserID:str):
    command = f''' 
        SELECT * FROM "{TABLENAME}" WHERE USERFOR LIKE "{str(yourUserID)}" AND STATE NOT LIKE "selesai" AND STATE NOT LIKE "revisi"; 
    '''

    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    res = cursor.execute(command)
    if not res:
        # res = [0,"Not Found","Not Found",99999999.99,"Not Found"]
        # assignmentID, version, state, desc, fol_name, url
        res = [[0,0,"NF","NF","NF","NF",0,0,0,"NF","NF"]]
    else:
        restemporary = []
        for i in res:
            restemporary.append(list(i))
        res = restemporary

        print(res)
        if len(res) == 0:
            return [[0,0,"Empty","Empty","Empty","Empty",0,0,0,"Empty","Empty"]]
    return res










