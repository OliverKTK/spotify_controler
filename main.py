import json, webbrowser
import requests as r
from requests_oauthlib import OAuth2Session

CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
REDIRECT_URI = "https://localhost:8888/callback"

def get_auth():
    auth_url = "https://accounts.spotify.com/authorize?"
    token_url = "https://accounts.spotify.com/api/token"
    scope = ["streaming", "app-remote-control", "user-read-playback-state", "user-read-currently-playing", "user-modify-playback-state"]
    spotify = OAuth2Session(CLIENT_ID, scope=scope, redirect_uri=REDIRECT_URI)
    authorization_url, state = spotify.authorization_url(auth_url)
    webbrowser.open(authorization_url)
    #print('Access: ', authorization_url)

    redirect_response = input("Paste URL: ")

    auth = r.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
    token = spotify.fetch_token(token_url, auth=auth, authorization_response=redirect_response)
    return token["access_token"]

def get_auth_header(token):
    return {"Authorization": "Bearer "+ token}

#-----------------------------------------------

def search_artist(artist_name):
    url = "https://api.spotify.com/v1/search"
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = r.get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("There are no artist with this name")
        return None
    return json_result[0]

#-----------------------------------------------

def playback_state():
    url = "https://api.spotify.com/v1/me/player"
    result = r.get(url,headers=headers)
    try:
        json_result = json.loads(result.content)
        try:
            test = json_result['error']
            return 1
        except:
            return json_result
    except:
        return 0

def being_played(playback_state):
    playback_state_device = playback_state['device']
    playback_state_track = playback_state['item']
    if playback_state["is_playing"] == True:
        print(f"\nPlaing in {playback_state_device['name']}      Volume: {playback_state_device['volume_percent']}\nTrack: {playback_state_track['name']}")
        print("Musicians: ",end="")
        for i in range(len(playback_state_track['artists'])):
            if i+1 == len(playback_state_track['artists']):    
                print(f"{playback_state_track['artists'][i]['name']}")
            else:    
                print(f"{playback_state_track['artists'][i]['name']}, ",end="")
    else:
        print("Not playing anything right now...")

def choose_available_device():
    url = "https://api.spotify.com/v1/me/player/devices"
    result = r.get(url, headers=headers)
    json_result = json.loads(result.content)['devices']
    print("Available Devices:")
    for i in range(len(json_result)):
        print(f"{i+1}. {json_result[i]['name']} - {json_result[i]['type']}")
    choice = int(input("Select the device you wish to connect: "))-1
    device_id = json_result[choice]['id']
    return device_id

def change_device():
    transfer_playback(choose_available_device())
    start_resume_playback()
#-----------------------------------------------

def start_resume_playback():  
    url = "https://api.spotify.com/v1/me/player/play"
    result = r.put(url, headers=headers)
    return result

def pause_playback():
    url = "https://api.spotify.com/v1/me/player/pause"
    result = r.put(url,headers=headers)
    return result

def next_playback():
    url = "https://api.spotify.com/v1/me/player/next"
    result = r.post(url, headers=headers)
    return result

def prev_playback():
    url = "https://api.spotify.com/v1/me/player/previous"
    result = r.post(url, headers=headers)
    return result

def volume_playback(volume):
    url = f"https://api.spotify.com/v1/me/player/volume?volume_percent={volume}"
    result = r.put(url, headers=headers)
    return result

def shuffle_playback(option):
    if option == True:
        url = f"https://api.spotify.com/v1/me/player/shuffle?state=true"
    else:
        url = "https://api.spotify.com/v1/me/player/shuffle?state=false"
    result = r.put(url,headers=headers)
    return result

def transfer_playback(device_id):
    url = "https://api.spotify.com/v1/me/player"
    data = {'device_ids': [device_id]}
    headers = {'Authorization': 'Bearer '+token, 'Content-Type': 'application/json'}
    result = r.put(url, headers=headers, json=data)
    try:
        json_result = json.loads(result.content)
        return json_result
    except:
        return result

def queue_playback():
    url = "https://api.spotify.com/v1/me/player/queue"
    result = r.get(url, headers=headers)
    json_result = json.loads(result.content)
    if json_result['currently_playing'] != None:
        print("Playing: ")
        print(f"    {json_result['currently_playing']['name']} - ", end='')
        for j in range(len(json_result['currently_playing']['artists'])):
                if j+1 == len(json_result['currently_playing']['artists']): 
                    print(f"{json_result['currently_playing']['artists'][j]['name']}")
                else:
                    print(f"{json_result['currently_playing']['artists'][j]['name']}, ", end='')
        print("Queue:")
        for i in range(3):
            print(f"    {i+1}. {json_result['queue'][i]['name']} - ",end='')
            for j in range(len(json_result['queue'][i]['artists'])):
                if j+1 == len(json_result['queue'][i]['artists']): 
                    print(f"{json_result['queue'][i]['artists'][j]['name']}")
                else:
                    print(f"{json_result['queue'][i]['artists'][j]['name']}, ", end='')
    else:
        print('Not playing anything')


#artist_result = search_artist(token, "potsu")
#artist_id = artist_result["id"]


with open("spotify api/token.json", "r+") as f:

    token = json.load(f)['token']
    headers = get_auth_header(token)
    state = playback_state()
    if (state == 0):
        
        device_id = choose_available_device()
        try:
            test = transfer_playback(device_id)['error']['status']
            new_token = get_auth()
            if token != new_token:
                token = new_token
                json_token = {"token" : token}
                f.seek(0)
                json.dump(json_token, f) 
                f.close()
        except:
            print("Now connected to a device")
            transfer_playback(device_id)
            start_resume_playback()
        
    elif (state == 1):
        new_token = get_auth()
        if token != new_token:
            token = new_token
            json_token = {"token" : token}
            f.seek(0)
            json.dump(json_token, f) 
            f.close()
      

headers = get_auth_header(token)
state = playback_state()
#queue_playback()
#change_device()
#start_resume_playback()
#pause_playback()
#next_playback()
#prev_playback()
#volume_playback(25)
#shuffle_playback(True)
being_played(state)


