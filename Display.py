import urllib3
import requests
import pandas as pd
import datetime


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def getAccessToken(clientid,clientsecret,refreshtoken):
    auth_url = "https://www.strava.com/oauth/token?"
    auth_param = {
        "client_id": clientid,
        "client_secret": clientsecret,
        "refresh_token": refreshtoken,
        "grant_type": "refresh_token"
    }
    access_token = requests.post(auth_url,data=auth_param).json()['access_token']
    return access_token


def activities(access_token,Updateddate,clientid,how="after"):
    activities_url = "https://www.strava.com/api/v3/athlete/activities?"
    if how == "after":
        activities_param = {
            "access_token": access_token,
            "after": Updateddate,
            "per_page": "200"
        }
        activities1 = requests.get(activities_url, params=activities_param).json()
        actdf = pd.DataFrame()
        if len(activities1) >= 1:
            for i in range(len(activities1)):
                date = (datetime.datetime.strptime(activities1[i]['start_date_local'],
                                                   "%Y-%m-%dT%H:%M:%SZ") - datetime.datetime(1970, 1,
                                                                                             1)).total_seconds()
                temp = {'activityID': float(activities1[i]['id']),
                        'clientID': clientid,
                        'Name': activities1[i]['name'],
                        'Distance': activities1[i]['distance'],
                        'Time': float(activities1[i]['moving_time']),
                        'ElevationGain': activities1[i]['total_elevation_gain'],
                        'Type': activities1[i]['type'],
                        'StartDate': date}
                tempdf = pd.DataFrame(temp, index=[i])
                actdf = actdf.append(tempdf, ignore_index=True)
        return actdf
    else:
        activities_param = {
            "access_token": access_token,
            "before": Updateddate,
            "per_page": "200",
            "page": 1
        }
        activities1 = requests.get(activities_url, params=activities_param).json()
        actdf = pd.DataFrame()
        while len(activities1) >= 1:
            for i in range(len(activities1)):
                date = (datetime.datetime.strptime(activities1[i]['start_date_local'],"%Y-%m-%dT%H:%M:%SZ") - datetime.datetime(1970, 1, 1)).total_seconds()
                temp = {'activityID': float(activities1[i]['id']),
                        'clientID': clientid,
                        'Name': activities1[i]['name'],
                        'Distance': activities1[i]['distance'],
                        'Time': float(activities1[i]['moving_time']),
                        'ElevationGain': activities1[i]['total_elevation_gain'],
                        'Type': activities1[i]['type'],
                        'StartDate': date}
                tempdf = pd.DataFrame(temp, index=[i])
                actdf = actdf.append(tempdf, ignore_index=True)
            activities_param["page"] += 1
            activities1 = requests.get(activities_url, params=activities_param).json()
        return actdf


if __name__ == '__main__':
    client_id = "50677"
    client_secret = "8f2dbb6395c6817cd38abd9405b9c6012c5d5700"
    refresh_token = "22e6ac168de54a1e11189148455a43c33618d77c"
    a = activities(getAccessToken(client_id,client_secret,refresh_token),datetime.datetime(2020,7,29,8,9,0).timestamp(),client_id,how="before")
    print(a)