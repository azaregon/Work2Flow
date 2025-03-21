import mainControl
import userController

import datetime
import essentials as esn





def seeAssignment(assignmentID,ver,userID:str):
    # workID, version, state, title, desc, fol_name, url
    # 0       1        2      3      4     5         6

    #get info
    result = mainControl.get_assignment_details(assignmentID=assignmentID,version=ver,usrIDaccess=userID)

    return result

    return f'''
        Title   : {result[3]}
        For     : {result[10]}
        Desc    : {result[4]}
        Version : {result[1]}

    '''


def AssignmentHistory(assignmentID,user):
    result = mainControl.get_assignment_history(assignmentID=assignmentID,usrIDrequest=user)
    # if type(result) == str:
    #     print(result)
    #     return result 

    # ret_temp = ''''''


    # for i in result:
    #     # ret_temp += f"<a href=\"/Assignment/{workID}/{i}\">version {i}</a><br>"
    #     ret_temp += f'''Version {i}\n'''
    return result



def createAssignment(title:str,desc:str,duedate:str,userfrom:str,userfor:str,emailfrom:str,emailfor:str,isForAnyone:bool=False):
    print(duedate)
    year,month,day,hour,minute = tuple(duedate.split("-"))

    #date to epoch
    epochdue = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)).timestamp()

    res = mainControl.new_assignment(title,desc,epochdue,userfrom,userfor,emailfor=emailfor,emailfrom=emailfrom,isForAnyone=isForAnyone)
    return res 

def createAssignmentByRegisteredTargetEmail(title:str,desc:str,duedate:str,userfrom:str,emailfor:str):
    year,month,day,hour,minute = tuple(duedate.split("-"))
    #date to epoch
    epochdue = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)).timestamp()
    
    userDataFrom = fetchUserByID(userfrom)
    userDataFor = fetchUserByEmail(emailfor)

    if userDataFrom[0] == userDataFor[0]:
        return "ERR: Giver and Receiver cannot be the same person"
    
    if userDataFor[0] == "None":
        return "ERR: Target user does not exist"

    res = mainControl.new_assignment(title=title,desc=desc,duedateepoch=epochdue,userfrom=userfrom,userfor=userDataFor[0],emailfrom=userDataFrom[3],emailfor=emailfor,isForAnyone=False)
    return res 

def createAssignmentByRegisteredTargetID(title:str,desc:str,duedate:str,userfrom:str,userfor:str,emailfrom:str,emailfor:str,isForAnyone:bool=False):
    print(duedate)
    year,month,day,hour,minute = tuple(duedate.split("-"))

    #date to epoch
    epochdue = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)).timestamp()

    res = mainControl.new_assignment(title,desc,epochdue,userfrom,userfor,emailfor=emailfor,emailfrom=emailfrom,isForAnyone=isForAnyone)
    return res 
    

def newRevision(AssignmentID:int,lastversion:int,desc:str,duedate:str,user):
    print(duedate)
    year,month,day,hour,minute = tuple(duedate.split("-"))

    #date to epoch
    epochdue = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)).timestamp()

    res = mainControl.new_revision(AssignmentID=AssignmentID,lastVersion=lastversion,desc=desc,duedateepoch=epochdue,usrIDrequest=user);
    return res

def submit(AssignmentID:int,version:int,usrIDsubmitter):
    return mainControl.submit(AssignmentID=AssignmentID,version=version,usrIDsubmitter=usrIDsubmitter)

def acceptsubmit(AssignmentID:int,version:int,usrIDacceptsubmit):
    return mainControl.accept_submit(AssignmentID=AssignmentID,version=version,usrIDacceptsubmit=usrIDacceptsubmit)

def acceptassign(AssignmentID:int,version:int,usrIDacceptassign):
    return mainControl.accept_assign(AssignmentID=AssignmentID,version=version,usrIDacceptassign=usrIDacceptassign)

def getAssignmentCreatedByYouThatHasNotDoneYet(yourUserID:str):
    return mainControl.Assignment_Created_By_You_That_Has_Not_Done_Yet(yourUserID=yourUserID)

def getYourUnfinishedAssignment(yourUserID:str):
    return mainControl.Your_Unfinished_Assignment(yourUserID=yourUserID)

####

def fetchUserByEmail(Email:str):
    return userController.fetch_user_by_email(Email)

def fetchUserByID(ID:str):
    return userController.fetch_user_by_id(ID)

def userRegistration(Name:str,Email:str,Desc:str,Password:str):
    userController.user_registration(Name=Name,Email=Email,Desc=Desc,Password=Password)

def userUpdateData(emailForFetch:str,newName:str,newEmail:str,newDesc:str):
    return userController.update_data(emailForFetch=emailForFetch,newName=newName,newEmail=newEmail,newDesc=newDesc)

def fetchAllUser():
    return userController.get_all_user_data()





if __name__ == '__main__':
    while 1:
        user = input('login (user id) : ')
        user = str(user)
        while 1:
            inp = input("]|> ")

            cmd = inp.split(" ")
            
            if cmd[0] == "create":
                createAssignment(cmd[1],cmd[2],cmd[3],user,cmd[4])
            elif cmd[0] == "addrevise":
                print(newRevision(str(cmd[1]),int(cmd[2]),cmd[3],cmd[4],user))
            elif cmd[0] == "details":
                print(seeAssignment(cmd[1],cmd[2],user))
            elif cmd[0] == "history":
                print(AssignmentHistory(cmd[1],user))
            elif cmd[0] == "submit":
                print(submit(cmd[1],cmd[2],user));
            elif cmd[0] == "acceptsubmit":
                print(acceptsubmit(cmd[1],cmd[2],user))
            elif cmd[0] == "acceptassign":
                print(acceptassign(cmd[1],cmd[2],user))

            elif cmd[0] == "--e":
                break;
        