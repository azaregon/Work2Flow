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
    print(str(flask.session.get("ID")))
    return flask.session.get("ID") == None
        # return flask.redirect("/login")

     
@app.route('/')
def home():
    print(not_logged_in())
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')
    
    print(flask.session['ID'],flask.session['EMAIL'])
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
                    <td>{ctr.fetchUserByID(str(unfinishedData[9]))[2]}</td>
                    <td>{f'<a href="{varscollection.BASE_PATH}/Assignment/{unfinishedData[0]}/{unfinishedData[1]}?ID={requesterID}"> Link </a>'}
                </tr>
            """

    return f''' 
        <h1>welcome {requesterData[2]} </h1>
        <a href="{varscollection.BASE_PATH}/Profile">Your profile</a>
        <span> -- -- </span>
        <a href="{varscollection.BASE_PATH}/logout">logout</a><br><br>
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
        <body onload="OLoad()">
            <form action="{varscollection.BASE_PATH}/login" method="post">
                
                <!--<input name="id" placeholder="Enter your ID"></input>-->

                <input name="email" id="Emailinp" placeholder="Enter your Email"></input>
                <input type="password" id="PWDinp" name="password" placeholder="Pwd"></input>

                <input type="submit"  value="Login"></input>
            </form>
            <script>
                function qSelect(query) {{
                    return document.querySelector(query)
                }}

                function OLoad() {{
                    const queryString = window.location.search;
                    const urlParams = new URLSearchParams(queryString);
                    qSelect("#Emailinp").value = urlParams.get('beforeEmail'); 
                    window.history.replaceState({{}}, document.title,   window.location.origin + window.location.pathname);

                }}
            </script>

            <br> <span>{flask.get_flashed_messages()}</span>
        </body>
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
            flask.flash("email or password not match")
            return flask.redirect(f'{varscollection.BASE_PATH}/login?beforeEmail={loginEmail}')



        flask.session['ID'] = userData[0]
        flask.session['EMAIL'] = userData[3]
        


        return flask.redirect(f'{varscollection.BASE_PATH}/')


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
        return f'''
        <body onload="OLoad()">
        <form method="post">
        
        <!--<input name="fromid" placeholder="Your id" ></input><br><br><br>-->
        <!--<input name="emailfrom" placeholder="Email you" ></input><br><br><br>-->

        <input name="title" id="AsgTitle" placeholder="Title.."></input><br><br>
        <textarea name="desc" id="AsgDesc" placeholder="Desc.."></textarea><br><br>
        
        <!--<input name="" placeholder="Target id" ></input><br><br><br>-->
        <!--<input name="emailfor" placeholder="Email for" ></input><br><br><br>-->

        <!--<label for="outsideDBcheck" hidden>for user outside system</label>-->
        <input type="checkbox" name="outsideDBcheck" id="outsideDBcheck" hidden>
        
        <br><br>

        <!--<input type="text" name="targetID" id="tgtID" placeholder="enter receiver ID" >-->
        <input type="email" name="targetEmail" id="tgtEM" placeholder="enter receiver email" ><br>


        <input name="duedate" id="AsgDuedate" type="datetime-local"   /><br><br>


        <button type="submit">Submit</button>
        </form>

        <br><br>
        <div id="messages">
            <span>{flask.get_flashed_messages() if len(flask.get_flashed_messages()) > 0 else ""}</span>
        <div>
        
        <script>
            function qSelect(query) {{
                return document.querySelector(query)
            }}

            function OLoad() {{
                var a = new Date();
                var a = new Date(a - (a.getTimezoneOffset() * 60 * 1000) + 1000*60*60*24*2);
                a.setSeconds(null);
                a.setMilliseconds(null);
                document.querySelector('#AsgDuedate').value = a.toISOString().slice(0,-1);


                const queryString = window.location.search;
                const urlParams = new URLSearchParams(queryString);
                qSelect("#AsgTitle").value = urlParams.get('titleBefore'); 
                qSelect("#AsgDesc").value = urlParams.get('descBefore');
                if (urlParams.get('dueDateBefore') != null){{
                    qSelect("#AsgDuedate").value = urlParams.get('dueDateBefore');
                }} 
                window.history.replaceState({{}}, document.title,   window.location.origin + window.location.pathname);

            }}
        </script>
        </body>
        '''
    elif flask.request.method == "POST":
        # userIDfrom = flask.request.form.get("fromid")
        # emailfrom = flask.request.form.get("emailfrom")
        userIDfrom = str(flask.session.get("ID"))
        # emailfrom = flask.session.get("EMAIL")
        
        title = flask.request.form.get("title")
        
        desc = flask.request.form.get("desc")

        duedatePure = flask.request.form.get("duedate")
        duedate = duedatePure.replace(":","-").replace("T","-")
        # emailfor = flask.request.form.get("emailfor")

        if not flask.request.form.get("outsideDBcheck"):
            userEmailFor = flask.request.form.get("targetEmail")
            foranyone= False
        else: # For later use
            userEmailFor = flask.request.form.get("targetEmail")
            foranyone= True

        createResult  = ctr.createAssignmentByRegisteredTargetEmail(title=title,desc=desc,duedate=duedate,userfrom=userIDfrom,emailfor=userEmailFor)

        if createResult[:3] == "ERR":
            flask.flash(createResult)
            return flask.redirect(f'{varscollection.BASE_PATH}/CreateAssignment?dueDateBefore={duedatePure}&descBefore={desc}&titleBefore={title}')
            # return f'''
            #     <h3> Target user not found </h3><br>
            #     <a href="{varscollection.BASE_PATH}/CreateAssignment">Back</a>
            # '''

        

        # return f'''{createResult}'''
        return flask.redirect(f'{varscollection.BASE_PATH}/Assignment/{createResult}/AdminView')


@app.route('/AssignmentHistory/<assignmentID>')
def AssignmentHistory(assignmentID):
    # result = dbManager.get_assignment_history(workID=assignmentID)
    # Auth
    if not_logged_in():
        return flask.redirect(f'{varscollection.BASE_PATH}/login')

    # requesterID = str(flask.request.args.get("ID"))
    requesterID = str(flask.session.get("ID"))

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
    


    if accesserID == str(result[9]) :
       template = f''' {baseTemplate}<br><br>
                    <a href="{varscollection.BASE_PATH}/Assignment/{assignmentID}/{version}/AdminView">Go to admin view</a>
       
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


@app.route("/Assignment/<assignmentID>/<version>/AdminView")
def seeAssignmentAdmin(assignmentID,version):
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

    # print(accesserID,result[9],result[10])
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
    elif accesserID == str(result[9]):
        return baseTemplate
    elif accesserID == str(result[10]):
        template =  f'''
            you are not permitted to see the admin page, go here to see yours<br>
            <a href="{varscollection.BASE_PATH}/Assignment/{assignmentID}/{version}">GO here</a>
        '''
    else:
        return ''' you are not related with this assignement'''

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

    userID = str(flask.session.get("ID"))
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
        requesterID = str(flask.session.get("ID"))

        assignmentID = flask.request.form.get("aid")
        version = int(flask.request.form.get("ver"))
        desc = flask.request.form.get("desc")
        duedate = flask.request.form.get("duedate").replace(":","-").replace("T","-")

        result  = ctr.newRevision(AssignmentID=assignmentID,lastversion=version,desc=desc,duedate=duedate,user=requesterID)
        if result[:3] == "ERR":
            return result


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
        submitterID = str(flask.session.get("ID"))

        
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
        sumbisFinishAcceptID = str(flask.session.get("ID"))
        
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

@app.route("/Profile")
def seeProfile():
    userData = ctr.fetchUserByID(flask.session.get("ID"))
    return f'''
    <body>
        <h1>Profile page</h1>
        <a href="{varscollection.BASE_PATH}/updateProfile">Edit profile</a>

        <ul>
            <li><b>name:</b> {userData[2]}</li>
            <li><b>email:</b> {userData[3]}</li>
            <li><b>desc:</b> {userData[4]}</li>
        </ul>
        
    </body>

    '''


@app.route('/updateProfile',methods=['GET','POST'])
def updateProfile():

    if flask.request.method == 'GET':
        return f'''
            <body>
                <h1>Edit Profile</h1>
                <span> enter only you want to edit</span><br>

                <form action="{varscollection.BASE_PATH}/updateProfile" method="post">
                
                    <input name="newName" id="newName" placeholder="enter new name"></input><br><br>
                    <input type="email" name="newEmail" id="newEmail" placeholder="enter new email"></input><br><br>
                    <textarea name="newDesc" id="newDesc" placeholder="enter new desc"></textarea><br><br>
                    <input type="submit"></input>
                </form>

                <script>
                    function qSelect(query) {{
                        return document.querySelector(query)
                    }}

                    function OLoad() {{
                        const queryString = window.location.search;
                        const urlParams = new URLSearchParams(queryString);
                        qSelect("#newName").value = urlParams.get('newName'); 
                        qSelect("#newEmail").value = urlParams.get('newEmail'); 
                        qSelect("#newDesc").value = urlParams.get('newDesc'); 
                        window.history.replaceState({{}}, document.title,   window.location.origin + window.location.pathname);

                    }}
                </script>
            </body>
        '''
    elif flask.request.method == 'POST':
        currUserData = ctr.fetchUserByID(flask.session.get('ID'))

        newName = flask.request.form.get("newName")

        newEmail = flask.request.form.get("newEmail")

        newDesc = flask.request.form.get("newDesc")

        print(newName,newEmail,newDesc)

        res = ctr.userUpdateData(flask.session.get('EMAIL'),newName=newName,newDesc=newDesc,newEmail=newEmail)
        print(res)
        if res[:3] == "ERR":
            return flask.redirect(f'{varscollection.BASE_PATH}/updateProfile?newName={newName}&newEmail={newEmail}&newDesc={newDesc}')

        if newEmail != "":
            flask.session['EMAIL'] = newEmail
            
        return flask.redirect(f'{varscollection.BASE_PATH}/Profile')



@app.route('/logout')
def logout():
    flask.session.clear()
    return flask.redirect(f'{varscollection.BASE_PATH}/login')





if __name__ == '__main__':
    app.run(debug=1)

