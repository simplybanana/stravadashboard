from flask import Flask, render_template, redirect,url_for,request,session
import DbThings
import Display
import os
import datetime
app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def base_url():
    return redirect(url_for('testing'))


@app.route('/login/', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        logincheck = DbThings.checkLoginData(request.form['username'],request.form['password'])
        if logincheck == -1:
            error = 'Invalid username or password'
        else:
            session['clientID'] = logincheck
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/createLogin/', methods=['GET', 'POST'])
def create_Login():
    error = None
    if request.method == 'POST':
        inDB = DbThings.checkLoginCreation(request.form['email'], request.form['clientID'])
        if inDB:
            error = 'Already Registered'
        else:
            try:
                Display.getAccessToken(request.form['clientID'], request.form['clientSecret'], request.form['refreshToken'])
                DbThings.insertData(request.form['email'], request.form['password'], request.form['clientID'],
                                    request.form['clientSecret'], request.form['refreshToken'])
                session['clientID'] = request.form['clientID']
                return redirect(url_for('dashboard'))
            except KeyError:
                error = 'Something went wrong. Check that data was inputted correctly'
    return render_template('createLogin.html', error=error)


@app.route('/dashboard/', methods=['Get','POST'])
def dashboard():
    clientID = session['clientID']
    clientSecret, refreshtoken, updated = DbThings.getOtherClientInfo(clientID)
    accesstoken = Display.getAccessToken(clientID,clientSecret,refreshtoken)
    if updated is None:
        date = datetime.datetime.now().timestamp()
        df = Display.activities(accesstoken,date,clientID,how='before')
        if not df.empty:
            DbThings.insertActivityData(df)
            DbThings.changeUpdatedDate(clientID,df['StartDate'][0])
    else:
        updated = DbThings.getUpdatedDate(clientID) + 1
        df = Display.activities(accesstoken,updated, clientID)
        if not df.empty:
            DbThings.insertActivityData(df)
            DbThings.changeUpdatedDate(clientID, df['StartDate'][0])
    unique_act = DbThings.getUniqueActivities(clientID)
    act_type = unique_act[0]
    if request.method == "POST":
        act_type = request.form.get("activityType",act_type)
    rows, el, ti, avg, avgE, avgT = DbThings.getRows(clientID, act_type)
    unique_act.remove(act_type)
    return render_template('dashboard.html',rows=rows.to_json(),el=el.to_json(),ti=ti.to_json(),avg=avg,avgE=avgE,avgT=avgT, unique_act=unique_act,act_type=act_type)


@app.route('/testing/', methods=['Get','POST'])
def testing():
    clientID = '50677'
    act_type = "Run"
    unique_act = DbThings.getUniqueActivities(clientID)
    if request.method == "POST":
        act_type = request.form.get("activityType","Run")
    rows,el,ti,avg,avgE,avgT = DbThings.getRows(clientID, act_type)
    unique_act.remove(act_type)
    return render_template('dashboard.html',rows=rows.to_json(),el=el.to_json(),ti=ti.to_json(),avg=avg,avgE=avgE,avgT=avgT, unique_act=unique_act, act_type=act_type)


if __name__ == '__main__':
    app.debug = True
    app.run()
    app.run(debug=True)
