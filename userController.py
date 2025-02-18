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
    
    command = f'''
        INSERT INTO {TABLENAME} VALUES ("{uniqueID}", "{Password}", "{Name}", "{Email}", "{Desc}")
        '''
    conn = sqlite3.connect(DBFPATH)
    cursor = conn.cursor()
    cursor.execute(command)
    conn.commit()

    


if __name__ == '__main__':
    # userRegistration("Ananda","aza@domain.com","A normal student","Satu2.")
    # userRegistration("Arya","cra@domain.org","A normal student too","Satu23")

    print(fetch_user_by_email("cr@domain.org"))
    # print(getUserDetailsByID("f466c5ad-d1f6-45d9-987b-f92598222f70"))
    pass