import dbManager
import datetime





def seeAssignment(assignmentID,ver):
    # workID, version, state, title, desc, fol_name, url
    # 0       1        2      3      4     5         6

    #get info
    result = dbManager.get_assignment_details(assignmentID=assignmentID,version=ver)

    return result
    return f'''
        Title   : {result[3]}
        For     : {result[10]}
        Desc    : {result[4]}
        Version : {result[1]}

    '''


def AssignmentHistory(assignmentID):
    result = dbManager.get_assignment_history(assignmentID=assignmentID)

    ret_temp = ''''''


    for i in result:
        # ret_temp += f"<a href=\"/Assignment/{workID}/{i}\">version {i}</a><br>"
        ret_temp += f'''Version {i}\n'''


    return ret_temp



def createAssignment(title:str,desc:str,duedate:str,userfrom:str,userfor:str):
    print(duedate)
    year,month,day,hour,minute = tuple(duedate.split("-"))

    #date to epoch
    epochdue = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)).timestamp()


    dbManager.new_assignment(title,desc,epochdue,userfrom,userfor)

def newRevision(AssignmentID:int,lastversion:int,desc:str,duedate:str):
    print(duedate)
    year,month,day,hour,minute = tuple(duedate.split("-"))

    #date to epoch
    epochdue = datetime.datetime(int(year),int(month),int(day),int(hour),int(minute)).timestamp()

    res = dbManager.new_revision(AssignmentID=AssignmentID,lastVersion=lastversion,desc=desc,duedateepoch=epochdue);
    return res

def submit(AssignmentID:int,version:int):
    dbManager.submit(AssignmentID=AssignmentID,version=version)

def accept(AssignmentID:int,version:int):
    dbManager.accept(AssignmentID=AssignmentID,version=version)



if __name__ == '__main__':
    while 1:
        inp = input("]|> ")

        cmd = inp.split(" ")
        
        if cmd[0] == "create":
            createAssignment(cmd[1],cmd[2],cmd[3],cmd[4],cmd[5])
        elif cmd[0] == "addrevise":
            newRevision(int(cmd[1]),int(cmd[2]),cmd[3],cmd[4])
        elif cmd[0] == "details":
            print(seeAssignment(cmd[1],cmd[2]))
        elif cmd[0] == "history":
            print(AssignmentHistory(cmd[1]))
        elif cmd[0] == "submit":
            submit(cmd[1],cmd[2]);
        elif cmd[0] == "accept":
            accept(cmd[1],cmd[2]);


        elif cmd[0] == "--e":
            break;
        