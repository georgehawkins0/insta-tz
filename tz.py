from instagram_private_api import Client, ClientError, ClientLoginError, ClientCookieExpiredError, ClientLoginRequiredError
import yaml
from yaml.loader import FullLoader, Loader
import codecs
import json
import argparse
from tqdm import tqdm
import sys
import os
from datetime import datetime
from rich.console import Console

def get_password():
        try:
            password = yaml.load(open('./creds/creds.yml'), Loader=FullLoader)
            passwd = password['password']
            if passwd:
                return str(passwd)
            else:
                print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
                sys.exit()
        except FileNotFoundError:
            print("Error: file not found")
            print("\n")
        except TypeError as e:
            if str(e) == "string indices must be integers":
                print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
                sys.exit()

def get_username():
    try:
        username = yaml.load(open('./creds/creds.yml'), Loader=FullLoader)
        user = username['username']
        if user:
            return str(user)
        else:
            print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
            sys.exit()
    except FileNotFoundError:
        print("Error: file not found")
        print("\n")
    except TypeError as e:
        if str(e) == "string indices must be integers":
                print("Error in creds.yml. Are your credentials in the correct format? \nusername: <username> \npassword: <password>")
                sys.exit()

def to_json(python_object):
    if isinstance(python_object, bytes):
        return {'__class__': 'bytes',
                '__value__': codecs.encode(python_object, 'base64').decode()}
    raise TypeError(repr(python_object) + ' is not JSON serializable')

def from_json(json_object):
    if '__class__' in json_object and json_object['__class__'] == 'bytes':
        return codecs.decode(json_object['__value__'].encode(), 'base64')
    return json_object

def onlogin_callback(api, new_settings_file):
    cache_settings = api.settings
    with open(new_settings_file, 'w') as outfile:
        json.dump(cache_settings, outfile, default=to_json)
        print('SAVED: {0!s}'.format(new_settings_file))

def login():
    username = get_username()
    password = get_password()
    settings_file_path = "./creds/settings.json"
    device_id = None

    try:
        settings_file = settings_file_path
        if not os.path.isfile(settings_file):
            # settings file does not exist
            print('Unable to find file: {0!s}'.format(settings_file))

            # login new
            api = Client(
                username, password,
                on_login=lambda x: onlogin_callback(x, settings_file_path))
        else:
            try:
                with open(settings_file) as file_data:
                    cached_settings = json.load(file_data, object_hook=from_json)
                    print('Reusing settings: {0!s}'.format(settings_file))
                    device_id = cached_settings.get('device_id')
                    # reuse auth settings
                    api = Client(
                        username, password,
                        settings=cached_settings)

            except json.decoder.JSONDecodeError: # if the file is there but empty
                os.remove(settings_file)
                # login new
                api = Client(
                username, password,
                on_login=lambda x: onlogin_callback(x, settings_file_path))
                    


    except (ClientCookieExpiredError, ClientLoginRequiredError) as e:
        print('ClientCookieExpiredError/ClientLoginRequiredError: {0!s}'.format(e))

        # Login expired
        # Do relogin but use default ua, keys and such
        api = Client(
            username, password,
            device_id=device_id,
            on_login=lambda x: onlogin_callback(x, settings_file_path))

    except ClientError as err:
            e = json.loads(err.error_response)
            print(e['message'])
            print(err.msg)
            print("\n")
            if 'challenage' in e:
                print("Please follow link to complete the challange " + e['challange']['url'])
            sys.exit()

    return api

def check_following(target_id):
    if str(target_id) == api.authenticated_user_id:
        return True
    endpoint = 'users/{user_id!s}/full_detail_info/'.format(**{'user_id' : target_id})
    return api._call_api(endpoint)['user_detail']['user']['friendship_status']['following']

def get_posts(target_id):
    data = []
    res = api.user_feed(str(target_id))
    data.extend(res.get("items", []))

    next_max_id = res.get('next_max_id')
    while next_max_id:
        results = api.user_feed(
            str(target_id), max_id=next_max_id)
        data.extend(results.get('items', []))
        if args.limit: # if there is a limit
            if len(data) >= args.limit: # if the current post list is bigger or equal to limit then return it 
                return data
        tq.update(len(results.get('items', [])))
        next_max_id = results.get('next_max_id')

    return data

def can_crawl(target_id=None,username=None):
    if not target_id:
        content =  api.username_info(username)
        target_id = content['user']['pk']
        is_private = content['user']['is_private']
        following = check_following(target_id)
    else:
        content =  api.user_info(target_id)
        target_id = content['user']['pk']
        is_private = content['user']['is_private']
        following = check_following(target_id)
    if is_private and not following:
        return False
    return True

def get_id(username):
    content =  api.username_info(username)
    id = content['user']['pk']
    return id

def get_number_of_posts(username=None,target_id=None):
    if not target_id:
        content =  api.username_info(username)
        target_id = content['user']['pk']
    content = api.user_info(str(target_id))
    return int(content["user"]["media_count"])

def timezonen(hoursDict):
    GMTBEDTIME=25
    GMTBEDTIME_T = 1
    lowest=float("infinity")
    for hour in hoursDict:
        hour = int(hour)
        total = 0
        total+=hoursDict[hour]
        total+=hoursDict[(hour+1)%24]
        total+=hoursDict[(hour+2)%24]
        total+=hoursDict[(hour+3)%24]
        total+=hoursDict[(hour+4)%24] # mod because it will go to hour 25, 26 ect which is 1 and 2am
        if lowest>total:
            lowest = total
            bedtime = hour

    if bedtime >11:
        timezone = GMTBEDTIME-bedtime
    else:
        timezone = GMTBEDTIME_T-bedtime
    if timezone>-1:
        sign="+"
    else:
        sign=""
    return("Estimated timezone: gmt {}{}".format(sign,timezone))

def clear():
    # for windows screen
    if sys.platform.startswith('win'):
        os.system('cls')
    # for mac or linux          
    else:
        os.system('clear')

def banner():
    clear()
    pc.print("""
        ██╗███╗  ██╗ ██████╗████████╗ █████╗     ████████╗███████╗
        ██║████╗ ██║██╔════╝╚══██╔══╝██╔══██╗    ╚══██╔══╝╚════██║
        ██║██╔██╗██║╚█████╗    ██║   ███████║       ██║     ███╔═╝
        ██║██║╚████║ ╚═══██╗   ██║   ██╔══██║       ██║   ██╔══╝
        ██║██║ ╚███║██████╔╝   ██║   ██║  ██║       ██║   ███████╗
        ╚═╝╚═╝  ╚══╝╚═════╝    ╚═╝   ╚═╝  ╚═╝       ╚═╝   ╚══════╝
                    Instagram user OSINT/SOCMINT
                      github.com/georgehawkins0\n\n""",style="bold red")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analysis of user post time.")
    parser.add_argument('-t', '--target', type=str, default=None, help="Target username")
    parser.add_argument('-l', '--limit', type=int, default=None, help="Post limit to crawl.")
    parser.add_argument('-p', '--percent', action='store_true',help='Display percentages on the hour frequency graph')
    args = parser.parse_args()

    api = login()
    pc = Console()

    if args.target:
        banner()
        #if can_crawl(username=args.target):
        if True:
            times = []
            target_id = get_id(args.target)
            if args.limit:
                total = args.limit
            else:
                total = get_number_of_posts(target_id=target_id)
            tq = tqdm(total=total,desc="Fetching posts")
            # getting posts:
            posts = get_posts(target_id)
            d = {n: 0 for n in range(24)}
            for post in posts:
                timestamp = post["taken_at"]
                dt_object = datetime.fromtimestamp(timestamp)
                d[dt_object.hour] +=1

            tq.update(total-tq.n)
            tq.close()

            # visual
            total = len(posts)
            if args.percent:
                print("Hour      %   Frequency\n")
            else:
                print("Hour   Frequency")
            for row in d:
                percent = round((d[row]/total)*100)
                if args.percent:
                    percent_space = (9-len(str(row)))*" "
                    block_space = (5-len(str(percent)))*" "
                    print("{}{}{}{}".format(row,percent_space,f"{percent}%",block_space),end="")
                else:
                    print("{}{}".format(row,(7-len(str(row)))*" "),end="")

                print("█"*d[row])
            
            tz = timezonen(d)
            print("\n",tz)
            print(f"\n\n Analysis of @{args.target}")
            
        else:
            print("Cannot crawl user. Perhaps you are not following them? ")