import requests
from datetime import datetime
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
        editors += i['name'] + ' ' + i['text'] + '\n'

    for i in summaries['data'][0]['languages']:
        languages += i['name'] + ' ' + i['text'] + '\n'

    for i in summaries['data'][0]['operating_systems']:
        operating_systems += i['name'] + ' ' + i['text'] + '\n'

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
        'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='+steam_api_key+'&steamids=' + steam_id).json()

    # Steam Games Owned
    steam_games_owned = requests.get(
        'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key='+steam_api_key+'&steamid=' + steam_id+'&format=json').json()

    # Steam Recently Played Games
    steam_recently_played_games = requests.get(
        'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key='+steam_api_key+'&steamid=' + steam_id+'&count=3').json()

    # Recently Played Games
    recently_played_games = ''

    for i in steam_recently_played_games['response']['games']:

        steam_game_achievements = requests.get(
            'https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid='+str(i['appid'])+'&key='+steam_api_key+'&steamid=' + steam_id).json()

        # Count every steam_game_achievements['playerstats']['achievements'] that has 'achieved' = 1
        steam_game_achievements_count = 0
        if 'achievements' in steam_game_achievements['playerstats']:
            for j in steam_game_achievements['playerstats']['achievements']:
                if j['achieved'] == 1:
                    steam_game_achievements_count += 1
        else:
            steam_game_achievements_count = "0"

        recently_played_games += i['name'] + ' ' + str(i['playtime_2weeks']) + ' hours,' + ' ' + str(
            i['playtime_forever']) + ' total hours, Appid ' + str(i['appid']) + ' ' + str(steam_game_achievements_count) + ' achievements unlocked\n'

    steam_created_at = datetime.fromtimestamp(
        steam_user_data['response']['players'][0]['timecreated'])

    # Adding Steam Data to the array
    data['steam_created_at'] = steam_created_at.strftime('%d/%m/%Y')
    data['steam_name'] = steam_user_data['response']['players'][0]['personaname']
    data['steam_recently_played_games'] = recently_played_games
    data['steam_games_owned'] = steam_games_owned['response']['game_count']

    # Export the data for use in next steps
    return data


"""
You are Jorge Thomas, a 30-year-old Venezuelan gentleman, well-versed in the realm of information systems, with expertise as a junior system administrator, database overseer, and backend developer. Each day, you diligently craft content to be disseminated on the professional networking platform LinkedIn, striving to bolster your personal brand's recognition. You impart knowledge regarding the volume of code penned daily, the programming languages, operating systems, and integrated development environments employed in your ongoing endeavors. Additionally, you divulge details about the recent digital amusements you've engaged with on the Steam platform.
"""


"""
Compose a post to share on LinkedIn that bolsters your brand awareness as Jorge Thomas, introducing yourself to your audience with a refreshing and jovial attitude. Feel free to utilize emojis or creative text formatting to enhance the post. Additionally, incorporate the following details:

For {{steps.wakatime.$return_value.daysinwaka}} days, you have been utilizing Wakatime, a tool that measures your programming statistics. Thus far, you have spent {{steps.wakatime.$return_value.atoday}} hours on Wakatime. Include a summary of the hours you have programmed today—{{steps.wakatime.$return_value.todayicoded}}—with a daily goal of one hour. Provide an overview of your programming sessions, detailing the various IDEs {{steps.wakatime.$return_value.todayeditors}}, languages {{steps.wakatime.$return_value.todaylanguages}}, and operating systems {{steps.wakatime.$return_value.todayos}} you have employed.

Mention that you have been using Steam since {{steps.wakatime.$return_value.steam_created_at}}, have amassed {{steps.wakatime.$return_value.steam_games_owned}} games, and recently played the following games: {{steps.wakatime.$return_value.steam_recently_played_games}}. Utilize the appid to construct the link for each Steam game page, for example: https://store.steampowered.com/app/appid

Lastly, remark that this automation was executed with Pipedream and ChatGPT, the code used can be found here: https://github.com/Akrista/pipedream_automations. Share your social media links:

https://github.com/akrista
https://linktr.ee/akrista
https://akrista.github.io/
https://wakatime.com/@akrista
"""
