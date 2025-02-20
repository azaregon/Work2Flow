import sqlite3
import time
import uuid
import essentials as esn
import varscollection 


DBFPATH = 'database.db'
TABLENAME = 'users'


def fetch_user_by_email(email:str):
    command = f'''
        SELECT * FROM {TABLENAME} WHERE Email LIKE "{email}";
    '''
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    res = cursor.execute(command).fetchone()
    conn.commit()

    return list(res) if res != None else ["None", "None", "None", "None", "None"]

def fetch_user_by_id(ID:str):
    command = f'''
        SELECT * FROM {TABLENAME} WHERE ID LIKE "{ID}";
    '''
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    res = cursor.execute(command).fetchone()
    conn.commit()

    return list(res) if res != None else ["None", "None", "None", "None", "None"]



def user_registration(Name:str,Email:str,Desc:str,Password:str):
    
    uniqueID = str(uuid.uuid4())

    if fetch_user_by_email(Email)[0] != "None":
        return f"ERR: user with email {Email} is already exist"
    
    command = f'''
        INSERT INTO {TABLENAME} VALUES ("{uniqueID}", "{Password}", "{Name}", "{Email}", "{Desc}")
        '''
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    cursor.execute(command)
    conn.commit()

    return "success"


def update_data(emailForFetch:str,newName:str="",newEmail:str="",newDesc:str=""):

    currData = fetch_user_by_email(emailForFetch)

    newName = newName if newName != "" else currData[2]
    newEmail = newEmail if newEmail != "" else currData[3]
    newDesc = newDesc if newDesc != "" else currData[4]

    dataNewEmail = fetch_user_by_email(newEmail)

    # Check if user exist
    if dataNewEmail[0] != "None" and dataNewEmail[3] != newEmail:
        return f"ERR: user with email {newEmail} is already exist"

    command = f'''
        UPDATE {TABLENAME} SET ID = "{currData[0]}", Password="{currData[1]}", Name="{newName}", Email="{newEmail}", Desc="{newDesc}" WHERE Email LIKE "{emailForFetch}";
        '''
    
    print(command)
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    cursor.execute(command)
    conn.commit()
    
    return "success"

    
    
    


if __name__ == '__main__':
#     user_registration("Ananda","aza@domain.com","A normal student","Satu2.")
#     user_registration("Arya","cra@domain.org","A normal student too","Satu23")
#     user_registration("Satya","mds@domain.id","A normal student too again","Satu234")
    print(update_data("aza@domain.com","Ananda","","A normal Student"))

    # print(fetch_user_by_email("cr@domain.org"))
    # print(getUserDetailsByID("f466c5ad-d1f6-45d9-987b-f92598222f70"))
    pass