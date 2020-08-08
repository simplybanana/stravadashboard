import sqlite3
import hashlib
import Display
import datetime
import pandas as pd


class DB(object):
    def __init__(self):
        self.conn = sqlite3.connect('Strava.db')
        self.c = self.conn.cursor()


def createdb():
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE login
        (email text, password text, clientID text, clientSecret text, refreshToken text, Updated timestamp, PRIMARY KEY(email,clientID))
    ''')
    c.execute('''
            CREATE TABLE activities
            (activityID int PRIMARY KEY, clientID int, Name text, Distance float, Time float, ElevationGain float, Type text, StartDate timestamp)
        ''')
    conn.commit()
    conn.close()


def insertData(email, password, clientID, clientSecret, refreshToken, Updated=None):
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    Epassword = hashlib.sha256(password.encode()).hexdigest()
    info = [(email,Epassword,clientID,clientSecret,refreshToken,Updated)]
    c.executemany("INSERT INTO login VALUES (?,?,?,?,?,?)", info)
    conn.commit()
    conn.close()


def checkLoginData(email,password):
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    encryptpass = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT clientID FROM login WHERE email=? AND password=?',(email,encryptpass,))
    clientID = c.fetchall()
    if not clientID:
        return -1
    else:
        return clientID[0][0]


def checkLoginCreation(email, clientID):
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    c.execute('SELECT clientID FROM login WHERE email=? AND clientID=?', (email, clientID,))
    clientID = c.fetchall()
    if clientID:
        return True
    else:
        return False


def getUpdatedDate(clientID):
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    c.execute('SELECT Updated FROM login WHERE clientID=?', (clientID,))
    date = c.fetchall()
    return date[0][0]


def changeUpdatedDate(clientid, date):
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    c.execute('UPDATE login SET Updated=? WHERE clientID=?', (date,clientid,))
    conn.commit()
    conn.close()


def getOtherClientInfo(clientid):
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    c.execute('SELECT * FROM login WHERE clientID=?', (clientid,))
    clientData = c.fetchall()
    return clientData[0][3], clientData[0][4], clientData[0][5]


def insertActivityData(df):
    df = df[['activityID','clientID','Name','Distance','Time','ElevationGain','Type','StartDate']]
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    for i in range(len(df)):
        info = tuple(df.iloc[i])
        c.execute('INSERT or IGNORE INTO activities VALUES (?,?,?,?,?,?,?,?)',info)
    conn.commit()
    conn.close()


def getRows(clientid,typeID):
    conn = sqlite3.connect('Strava.db')
    conn.row_factory = sqlite3.Row
    """
    c = conn.cursor()
    c.execute('SELECT * FROM activities WHERE clientID=? Order by StartDate Desc', (clientid,))
    rows = c.fetchall()
    return rows"""
    df = pd.read_sql_query('Select sum(Distance) as [Distance], sum(Time) as [Time], sum(ElevationGain) as [ElevationGain], Type, date(StartDate,\'unixepoch\') as [Date] '
                           'from activities where clientID=:id and Type=:typeID '
                           'group by Type,[Date]'
                           'order by StartDate DESC',
                           con=conn,params={"id": clientid, "typeID": typeID})
    df['Date'] = pd.to_datetime(df['Date'])
    df['WeekOf'] = df.apply(lambda x: x['Date'] - datetime.timedelta(days=x['Date'].weekday()), axis=1).dt.date
    df['WeekOf'] = pd.to_datetime(df['WeekOf'])
    df['WeekOf'] = df['WeekOf'].dt.strftime("%Y-%m-%d")
    df["Day"] = df['Date'].dt.dayofweek
    df["Distance"] = round(df["Distance"]/1609,2)
    df["ElevationGain"] = round((df["ElevationGain"] / 1609)*5820, 2)
    df["Time"] = round(df["Time"]/60,2)
    df1 = pd.pivot_table(df,index='Day',columns=['WeekOf'],values='Distance').sort_values(by=['Day'],ascending=True)
    df1.fillna(0,inplace=True)
    df1 = df1.reindex(sorted(df1.columns,reverse=True),axis=1)
    df2 = pd.pivot_table(df, index='Day', columns=['WeekOf'], values='ElevationGain').sort_values(by=['Day'], ascending=True)
    df2.fillna(0, inplace=True)
    df2 = df2.reindex(sorted(df2.columns, reverse=True), axis=1)
    df3 = pd.pivot_table(df, index='Day', columns=['WeekOf'], values='Time').sort_values(by=['Day'],ascending=True)
    df3.fillna(0, inplace=True)
    df3 = df3.reindex(sorted(df3.columns, reverse=True), axis=1)
    avg = df['Distance'].mean()
    avg1 = df['ElevationGain'].mean()
    avg2 = df['Time'].mean()
    return df1, df2, df3, avg, avg1, avg2


def getUniqueActivities(clientID):
    conn = sqlite3.connect('Strava.db')
    conn.row_factory = lambda cursor, row: row[0]
    c = conn.cursor()
    c.execute('SELECT DISTINCT TYPE FROM activities WHERE clientID=?', (clientID,))
    rows = c.fetchall()
    return rows


if __name__ == '__main__':
    #createdb()
    email = 'first@test.com'
    password = '123'
    client_id = "50677"
    client_secret = "8f2dbb6395c6817cd38abd9405b9c6012c5d5700"
    refresh_token = "22e6ac168de54a1e11189148455a43c33618d77c"
    #updated = datetime.datetime(2020,7,27,15,0,0).timestamp()
    #insertData(email,password,client_id,client_secret,refresh_token)
    """
    conn = sqlite3.connect('Strava.db')
    c = conn.cursor()
    print(checkLoginData('test1@test.com','test123'))
    a = Display.activities(Display.getAccessToken(client_id, client_secret, refresh_token),
                   datetime.datetime(2020, 7, 29, 8, 9, 0).timestamp(), client_id, how="before")
    #insertActivityData(a)
    for i in range(len(a)):
        print(a.iloc[i])
    for row in c.execute('Select * from activities'):
        print(row)"""
    #a,b,c,avg,avg1,avg2 = getRows(client_id,"Run")
    #print(b.to_json())
    d = getUniqueActivities(client_id)
    test = 'Run'
    d.remove(test)
    print(d)
    for item in d:
        print(item)