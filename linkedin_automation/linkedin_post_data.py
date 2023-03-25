import requests
from datetime import datetime
# from datetime import date, datetime, timedelta
from dateutil import tz


def handler(pd: "pipedream"):
    # Steam API Key Connection - PipeDream
    steam_api_key = "insert your steam api key here"
    steam_id = "insert your steam id here"

    # Wakatime Token Connection - PipeDream
    token = f'{pd.inputs["wakatime"]["$auth"]["oauth_access_token"]}'
    authorization = f'Bearer {token}'
    headers = {"Authorization": authorization}

    # I create an empty array to be used in the linkedin post
    data = {}

    # Wakatime User Data
    userdata = requests.get(
        'https://wakatime.com/api/v1/users/current', headers=headers)

    # * Dates
    # ! Converting UTC to User Timezone
    from_zone = tz.gettz('UTC')
    # ! User Timezone
    to_zone = tz.gettz(userdata.json()['data']['timezone'])

    # ! Today
    today_utc = datetime.today().replace(tzinfo=from_zone)
    # ! Today in User Timezone
    today_user_timezone = today_utc.astimezone(to_zone)

    # ! Wakatime User Creation Date
    created_at_utc = datetime.strptime(
        userdata.json()['data']['created_at'], '%Y-%m-%dT%H:%M:%S%z')

    # ! Days in Wakatime
    created_at_utz = created_at_utc.astimezone(to_zone)
    daysinwaka = today_user_timezone - created_at_utz

    # Sumario de Hoy
    summaries = requests.get('https://wakatime.com/api/v1/users/current/summaries?start='+today_user_timezone.strftime(
        '%Y-%m-%d')+'&end='+today_user_timezone.strftime('%Y-%m-%d'), headers=headers).json()
    # All Time Since Today
    atoday = requests.get(
        'https://wakatime.com/api/v1/users/current/all_time_since_today', headers=headers)

    editors = ''
    languages = ''
    operating_systems = ''

    # Listing Editors, Languages and Operating Systems

    for i in summaries['data'][0]['editors']:
        editors += '- ' + i['name'] + ' ' + i['text'] + '\n'

    for i in summaries['data'][0]['languages']:
        languages += '- ' + i['name'] + ' ' + i['text'] + '\n'

    for i in summaries['data'][0]['operating_systems']:
        operating_systems += '- ' + i['name'] + ' ' + i['text'] + '\n'

    # Adding Wakatime Data to the array
    data['atoday'] = atoday.json()['data']['text']
    data['daysinwaka'] = daysinwaka.days
    data['location'] = userdata.json()['data']['city']['title']
    data['fullname'] = userdata.json()['data']['full_name']
    data['todayicoded'] = summaries['cumulative_total']['text']
    data['todayeditors'] = editors
    data['todaylanguages'] = languages
    data['todayos'] = operating_systems

    # Steam User Data
    steam_user_data = requests.get(
        'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='+steam_api_key+'&steamids=' + steam_id)

    steam_created_at = datetime.fromtimestamp(
        steam_user_data.json()['response']['players'][0]['timecreated'])

    data['steam_created_at'] = steam_created_at

    # Export the data for use in next steps
    return data


"""
Hi! I'm {{steps.wakatime.$return_value.fullname}} and you'll sure be seeing this a lot every day 😅

📅 This is day {{steps.wakatime.$return_value.daysinwaka}} since i started using @wakatime and so far i got {{steps.wakatime.$return_value.atoday}} coding with wakatime.

Some time ago i've started to do the #100DaysOfCode challenge, and i really liked the idea of measuring how much i'm using my time everyday to practice the things i love to do with code.


So here's a little summary of what i did today:

⏱ I coded {{steps.wakatime.$return_value.todayicoded}} towards my @WakaTime goal of coding 1 hr per day.

📓 For my coding sessions i used these editors:

{{steps.wakatime.$return_value.todayeditors}}

📜 The languages that i used were:

{{steps.wakatime.$return_value.todaylanguages}}

🖥 And the OS that i used:

{{steps.wakatime.$return_value.todayos}}


This is a simple post automatization that i did with pipedream.com working with the wakatime api, so i can show some useless info like the amount of hours i have code since i created my wakatime account or the last editor i used with wakatime.

If you want to use my code for this automatization, here it is: https://gist.github.com/Akrista/709ab17e5b7ef2cf7d3cb31f59f76de6
It's not perfect, so if you have any sugestion on how to improve it, please tell me in the comments or in github.

https://github.com/akrista
https://linktr.ee/akrista
https://akrista.github.io/
https://wakatime.com/@akrista

#personaldevelopment #productivity #Training #programing
"""
