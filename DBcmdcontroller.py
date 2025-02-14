import sqlite3




conn = sqlite3.connect('database.db');



while True:
    inp = input(">> ")
    try:
        
        cursor = conn.cursor()
        res= cursor.execute(inp)
        conn.commit()

        if inp.split(" ")[0].upper() == "SELECT":
            for i in res:
                print(i)
    except Exception as e:
        print(e)



    if inp == "--e":

        conn.close()

    
        break;