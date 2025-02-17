import flask
from werkzeug.utils import secure_filename
import os
from datetime import datetime


import controllerBridge as ctr
import varscollection
import essentials

app = flask.Flask(__name__)
app.secret_key = '98as12uayvwnoasm8as9das3dsas2wqeyw4cweqw7ec6qw98ewc69cqw8ne2cqwbb6qwnvqyey8asud'
# app.config['UPLOAD_FOLDER'] = './tmp/'



# @app.rout('/createAssignment')
# def home():


#     if flask.request.method == "GET" :
#         return 

def not_logged_in():
    print(flask.session.get("ID"))
    return flask.session.get("ID") == None
        # return flask.redirect("/login")

     
@app.route('/')
def home():
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')
    
    requesterID = str(flask.session.get("ID"))
    requesterData = ctr.fetchUserByID(requesterID)

    unfinishedDatas = ctr.getYourUnfinishedAssignment(yourUserID=requesterID)
    # print(unfinishedDatas)

    unfinishedDatasHTML = ''''''
    for unfinishedData in unfinishedDatas:
        if unfinishedData[2] != "Empty":
            unfinishedDatasHTML += f"""
                <tr>
                    <td>{unfinishedData[0]}</td>
                    <td>{unfinishedData[1]}</td>
                    <td>{unfinishedData[2]}</td>
                    <td>{unfinishedData[3]}</td>
                    <td>{datetime.fromtimestamp(unfinishedData[7]).strftime('%Y-%m-%d %H:%M:%S')}</td>
                    <td>{ctr.fetchUserByID(unfinishedData[9])[2]}</td>
                    <td>{f'<a href="{varscollection.BASE_PATH}/Assignment/{unfinishedData[0]}/{unfinishedData[1]}?ID={requesterID}"> Link </a>'}
                </tr>
            """

    return f''' 
        <h1>welcome {requesterData[2]} </h1><br>
        <div style="display:flex; gap:20px">
            <a href="{varscollection.BASE_PATH}/CreateAssignment"> Create new assignment</a>      
            <!--<a href="{varscollection.BASE_PATH}/assignmenttoother"> See your assignment to other</a>-->  
        </div>
        <br><br><br>

        <h3>Unfinished assignment:</h3> 
        <style>
        table,td,th {{border:1px solid black; padding:2px}}
        </style>
        <table >
            <tr>
                <th>Assignment ID</th>
                <th>Version</th>
                <th>STATE</th>
                <th>TITLE</th>
                <th>Due date</th>
                <th>from</th>
                <th>url</th>
            </tr>
            {unfinishedDatasHTML}
        </table>

        
        
            '''

@app.route('/login', methods=['GET','POST'])
def login():
    if flask.request.method == 'GET':
        return  f'''
        <form action="{varscollection.BASE_PATH}/login" method="post">
            
            <!--<input name="id" placeholder="Enter your ID"></input>-->

            <input name="email" placeholder="Enter your Email"></input>
            <input type="password" name="password" placeholder="Pwd"></input>

            <input type="submit"  value="Login"></input>
        </form>
                '''
    elif flask.request.method == 'POST':
        # print('LOGG')
        # loginID = flask.request.form.get("id")
        loginEmail = flask.request.form.get("email")
        loginPW = flask.request.form.get("password")

        # Check Dataa

        # userData = essentials.temp_login_system(loginID)
        userData = ctr.fetchUserByEmail(loginEmail)
        print(loginPW,userData[1],loginPW == userData[1])
        # [ID, PW, Name, Email, Desc]

        if loginPW != userData[1]:
            return flask.redirect(f'{varscollection.BASE_PATH}/login')



        flask.session['ID'] = userData[0]
        flask.session['EMAIL'] = userData[1]
        


        return flask.redirect('/')


@app.route("/dwnld/<assignmentID>/<version>/<filename>")
def download(assignmentID,version,filename):
    #Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')
    
    # downloaderID = str(flask.request.args.get("ID"))
    downloaderID = str(flask.session.get("ID"))

    dbres = ctr.seeAssignment(assignmentID=assignmentID,ver=version,userID=downloaderID)
    if downloaderID != str(dbres[9]) and downloaderID != str(dbres[10]):
        return '''Not permitted'''
    try:
        return flask.send_file(os.path.join(varscollection.SUBMIT_FOLDER_PATH,f'''{assignmentID}-v{version}''',filename),as_attachment=True) # download the file
    except:
        return '''file not found'''



@app.route("/CreateAssignment",methods=['GET','POST'])
def createAssignment():
    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')
    
    if flask.request.method == "GET":
        return '''
        <body>
        <form method="post">
        
        <!--<input name="fromid" placeholder="Your id" ></input><br><br><br>-->
        <!--<input name="emailfrom" placeholder="Email you" ></input><br><br><br>-->

        <input name="title" placeholder="Title.."></input><br><br>
        <textarea name="desc" placeholder="Desc.."></textarea><br><br>
        
        <!--<input name="forid" placeholder="Target id" ></input><br><br><br>-->
        <!--<input name="emailfor" placeholder="Email for" ></input><br><br><br>-->

        <label for="outsideDBcheck">for user outside system</label>
        <input type="checkbox" name="outsideDBcheck" id="outsideDBcheck" onchange="abbc()">
        
        <br><br>
        <div id="changeTarget">
            <input type="text" name="targetID" id="tgtID" placeholder="enter receiver ID" >
            <input type="email" name="targetEmail" id="tgtEM" placeholder="enter receiver email" hidden>
        </div>

        <input name="duedate" id="duedate" type="datetime-local"  /><br><br>


        <button type="submit">Submit</button>
        </form>


        <script>

            function abbc() {   
            forOutsideDB = document.querySelector("#outsideDBCheck").checked
            if (forOutsideDB) {
                document.querySelector("#tgtEM").hidden = false;
                document.querySelector("#tgtEM").value ="";
                document.querySelector("#tgtID").hidden = true;
                document.querySelector("#tgtID").value = "";
            } else {
                document.querySelector("#tgtEM").hidden = true;
                document.querySelector("#tgtEM").value = "";
                document.querySelector("#tgtID").hidden = false;
                document.querySelector("#tgtID").value = "";
            
            }
            }
        </script>
        
        </body>
        '''
    elif flask.request.method == "POST":
        # userIDfrom = flask.request.form.get("fromid")
        # emailfrom = flask.request.form.get("emailfrom")
        userIDfrom = flask.session.get("ID")
        emailfrom = flask.session.get("EMAIL")
        
        title = flask.request.form.get("title")
        
        desc = flask.request.form.get("desc")

        if not flask.request.form.get("outsideDBcheck"):
            userIDfor = flask.request.form.get("targetID")
            userDataFor = ctr.fetchUserByID(userIDfor)
            emailfor = userDataFor[3]
            foranyone= False
        else:
            emailfor = flask.request.form.get("targetEmail")
            userIDfor = "0"
            foranyone= True

        # emailfor = flask.request.form.get("emailfor")

        duedate = flask.request.form.get("duedate").replace(":","-").replace("T","-")
        newAssignID  = ctr.createAssignment(title=title,desc=desc,duedate=duedate,userfrom=userIDfrom,userfor=userIDfor,emailfrom=emailfrom,emailfor=emailfor,isForAnyone=foranyone)

        
        file_loc = os.path.join(varscollection.SUBMIT_FOLDER_PATH,f"{newAssignID}-v1")
        
        if not os.path.exists(file_loc):
            os.mkdir(file_loc)

        return f'''{newAssignID}/1'''


@app.route('/AssignmentHistory/<assignmentID>')
def AssignmentHistory(assignmentID):
    # result = dbManager.get_assignment_history(workID=assignmentID)
    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    # requesterID = str(flask.request.args.get("ID"))
    requesterID = str(flask.sessions.get("ID"))

    print(requesterID)
    result = ctr.AssignmentHistory(assignmentID=assignmentID,user=requesterID)
                                   
    if result == [0]:
        return """ You have no access"""

    ret_temp = """"""

    for i in result:
        ret_temp += f"<a href=\"{varscollection.BASE_PATH}/Assignment/{assignmentID}/{i}?ID={requesterID}\">version {i}</a><br>"


    return ret_temp

@app.route("/Assignment/<assignmentID>/<version>")
def seeAssignment(assignmentID,version):
    # workID, version, state, title, desc, fol_name, create, due, laststatechange, from, for
    # 0       1        2      3      4     5         6       7    8               9      10
    

    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    # accesserID = str(flask.request.args.get('ID'))
    accesserID = str(flask.session.get('ID'))


    print(accesserID)


    #get info
    # result = dbManager.get_work_details(workID=workID,version=ver)
    result = ctr.seeAssignment(assignmentID=assignmentID,ver=version,userID=accesserID)

    print(accesserID,result[9],result[10])
    if result[2]  == "Permission Denied":
        return f'''
            <h1>Permission Denied</h1>
        '''
    
    #file listing

    fileList = os.listdir(os.path.join(varscollection.SUBMIT_FOLDER_PATH,f'''{assignmentID}-v{version}'''))
    fileListHTML = """"""
    for filename in fileList:
        fileListHTML += f"""
            <li><a href="{varscollection.BASE_PATH}/dwnld/{assignmentID}/{version}/{filename}?ID={accesserID}">{filename}</a></li>
        """


    baseTemplate = f'''
        <h1>{result[3]}-v{result[1]}</h1>

        <a href="{varscollection.BASE_PATH}/AssignmentHistory/{assignmentID}?ID={accesserID}"> see other version</a>

        <h2>{result[4]}</h2>

        <ul>
            {fileListHTML}
        </ul>

    '''

    template = f'''{baseTemplate}'''
    


    if accesserID == str(result[9]) and str(result[2]).upper() == 'MENUNGGU-REVIEW':
        template = f'''{baseTemplate}<br><br><br><br><br>
            <style>
                #reviseToggle + #reviseForm {{ display:none;}}
                #reviseToggle:checked + #reviseForm {{ display:block;}}
            </style>
            <form id="reviseForm" method="post" action="{varscollection.BASE_PATH}/acceptSubmis">
                <input type="hidden" name="submitterID" value="{accesserID}"></input>
                <input type="hidden" name="aid" value="{result[0]}"></input>
                <input type="hidden" name="ver" value="{result[1]}"></input>
               
                <button type="submit" name="feedback" value="AcceptSubmission">Mark assignment done</button> 
            </form>

            <input id="reviseToggle" name="reviseToggle" type="checkbox">
                <label for="reviseToggle">Add Revision</label> 
            </input><br>
            <form id="reviseForm" method="post" action="{varscollection.BASE_PATH}/revise">
                <input type="hidden" name="requesterID" value="{accesserID}"></input>
                <input type="hidden" name="aid" value="{result[0]}"></input>
                <input type="hidden" name="ver" value="{result[1]}"></input>
                <br><br>
                <div style="border: 2px solid black; padding:10px;"  >
                    <textarea name="desc" placeholder="Desc.."></textarea><br><br>
                    <input name="duedate" id="duedate" type="datetime-local" /><br><br>
                </div>
                
                <button type="submit" name="feedback" value="Revise">Revise</button> 
            </form>
        '''
    elif accesserID == str(result[10]) and str(result[2]).upper() == 'DIBERIKAN':
        template = f'''{baseTemplate}<br><br><br><br><br>
            <form method="post" action="{varscollection.BASE_PATH}/acceptassignment">
                <input type="hidden" name="requesterID" value="{accesserID}"></input>
                <input type="hidden" name="aid" value="{result[0]}"></input>
                <input type="hidden" name="ver" value="{result[1]}"></input>

                <button type="submit" name="feedback" value="Accept">Accept assignment</button> 
            </form>
        '''
    elif accesserID == str(result[10]) and str(result[2]).upper() == 'DIKERJAKAN':
        # FOR THE SUBMIT

        template = f'''{baseTemplate}<br><br><br><br><br>
            <form method="post" action="{varscollection.BASE_PATH}/submitfiles" enctype="multipart/form-data">
                <input type="hidden" name="submitterID" value="{accesserID}"></input>
                <input type="hidden" name="aid" value="{result[0]}"></input>
                <input type="hidden" name="ver" value="{result[1]}"></input>


                <input type="file" name="fileup" multiple required />

                <button type="submit" name="feedback" value="Submit">Submit assignment</button> 
            </form>
        '''

        # template = f'''{baseTemplate}<br><br><br><br><br>
        #     <form>
        #         <button type="submit" name="feedback" value="Accept">Accept</button> 
        #     </form>
        # '''

        

    return template



@app.route('/acceptassignment',methods=['POST','GET'])
def acceptAssignment():
    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    userID = flask.session.get("ID")
    # userID = flask.request.form.get("requesterID")

    aid = flask.request.form.get("aid")
    version = flask.request.form.get("ver")
    
    res = ctr.acceptassign(AssignmentID=aid,version=version,usrIDacceptassign=userID)

    return flask.redirect(f"{varscollection.BASE_PATH}/Assignment/{aid}/{version}?ID={userID}")


@app.route("/revise",methods=['GET','POST'])
def createRevision():
    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    if flask.request.method == "POST":
        # requesterID = flask.request.form.get("requesterID")
        requesterID = flask.session.get("ID")

        assignmentID = flask.request.form.get("aid")
        version = int(flask.request.form.get("ver"))
        desc = flask.request.form.get("desc")
        duedate = flask.request.form.get("duedate").replace(":","-").replace("T","-")

        result  = ctr.newRevision(AssignmentID=assignmentID,lastversion=version,desc=desc,duedate=duedate,user=requesterID)
        if result[:3] == "ERR":
            return result

        file_loc = os.path.join(varscollection.SUBMIT_FOLDER_PATH,f"{assignmentID}-v{version+1}")
        
        if not os.path.exists(file_loc):
            os.mkdir(file_loc)

        # return f'''{newAssignID}/{int(version)+1}'''
        return flask.redirect(f"{varscollection.BASE_PATH}/Assignment/{result}?ID={requesterID}")
    


@app.route("/submitfiles", methods=["GET","POST"])
def submitFiles():

    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    if flask.request.method == "POST":    
        assignmentID = flask.request.form.get("aid")
        version = flask.request.form.get("ver")
        
        # submitterID = flask.request.form.get("submitterID")
        submitterID = flask.session.get("ID")

        
        # print('fileup' in flask.request.files)
        # print(flask.request.files)
        dbSubmit = ctr.submit(AssignmentID=assignmentID,version=version,usrIDsubmitter=submitterID)
        if 'fileup' in flask.request.files and dbSubmit == "the assignment is menunggu-review":
            files = flask.request.files.getlist('fileup')
            fol_name = f"{assignmentID}-v{version}"
            file_loc = os.path.join(varscollection.SUBMIT_FOLDER_PATH,fol_name)
            
            if not os.path.exists(file_loc):
                os.mkdir(file_loc)
            
            # print(flask.request.files)
            # print(flask.request.files.getlist('fileup'))
            for file in files:
                filename = secure_filename(file.filename)
                print(file_loc,filename)
                file.save(os.path.join(file_loc,filename))

            # return ctr.submit(AssignmentID=assignmentID,version=version,usrIDsubmitter=submitterID)
            # return "success"
            return flask.redirect(f"{varscollection.BASE_PATH}/Assignment/{assignmentID}/{version}?ID={submitterID}")
            # return flask.redirect('')

        return dbSubmit



@app.route("/acceptSubmis",methods=["POST"])
def acceptSubmis():
        # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    if flask.request.method == "POST":
        assignmentID = flask.request.form.get("aid")
        version = flask.request.form.get("ver")
        # sumbisFinishAcceptID = flask.request.form.get("submitterID")
        sumbisFinishAcceptID = flask.session.get("ID")
        
        print(sumbisFinishAcceptID)
        result = ctr.acceptsubmit(AssignmentID=assignmentID,version=version,usrIDacceptsubmit=str(sumbisFinishAcceptID))
    return result






# Assignment Giver Dashboard

@app.route("/Assignmenttoother")
def assignmentToOther():
        # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')



    # requesterID = str(flask.request.args.get("ID"))
    requesterID = str(flask.session.get("ID"))

    datas = ctr.getAssignmentCreatedByYouThatHasNotDoneYet(yourUserID=requesterID)
    print(datas)

    datasHTML = ''''''
    for data in datas:
        datasHTML += f"""
            <tr>
                <td>{data[0]}</td>
                <td>{data[1]}</td>
                <td>{data[2]}</td>
                <td>{data[3]}</td>
                <td>{datetime.fromtimestamp(data[7]).strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{data[10]}</td>
                <td>{f'<a href="{varscollection.BASE_PATH}/Assignment/{data[0]}/{data[1]}?ID={requesterID}"> Link </a>'}
            </tr>
        """


    return f"""
        <style>
        table,td,th {{border:1px solid black; padding:2px}}
        </style>
        <table >
            <tr>
                <th>Assignment ID</th>
                <th>Version</th>
                <th>STATE</th>
                <th>TITLE</th>
                <th>Due date</th>
                <th>for</th>
                <th>url</th>
            </tr>
            {datasHTML}
        </table>
    """



@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect(f'{varscollection.BASE_PATH}/login')


if __name__ == '__main__':
    app.run(debug=1)

