import discord
import asyncio
import os
import sys
import importlib
import datetime
import time
import platform
import pymysql
import io
import csv
import requests_async as requests
import json
import psutil

from matplotlib import pyplot as plt
from pytz import timezone

def is_manager(user_id):
    if platform.system() == "Windows":
        file = open(directory + "\\user_info\\Manager.txt",mode='r')
    elif platform.system() == "Linux":
        file = open(directory + "/user_info/Manager.txt",mode='r')
    else:
        return False
    cache1 = file.readlines()
    file.close()
    if user_id in cache1:
    	return True
    return False

def is_admin(message):
    for role in message.author.roles:
        if role.permissions.administrator:
            return True
    return False 

def is_banned(user_id,message):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect .cursor()
    sql_prefix = "select * from BLACKLIST"
    cur.execute(sql_prefix)
    banned_list = cur.fetchall()
    connect.close()
    for banned in banned_list:
        print(banned[0])
        if banned[0] == int(user_id):
            if message.content[1:].startswith("블랙리스트 여부"):
                log_info(message.guild.name,message.channel,str(message.author),str(message.author) + '잘못된 유저가 접근하고 있습니다!(' + message.content + ')')
                embed = discord.Embed(title="권한 거부(403)", color=0x00aaaa)
                embed.add_field(name="권한이 거부되었습니다.", value="당신은 블랙리스트로 등록되어 있습니다.", inline=False)
                coro = message.channel.send(embed=embed)
                asyncio.run_coroutine_threadsafe(coro, client.loop)
            return True
    return False

def log_info(guild, channel, user, message):
    Ftime = time.strftime('%Y-%m-%d %p %I:%M:%S', time.localtime(time.time()))
    print("[시간: " + str(Ftime) + " | " + str(guild) + " | " + str(channel) + " | " + str(user) + "]: " + str(message))
    log = open("log.txt","a",encoding = 'utf-8')
    log.write("[시간: " + str(Ftime) + " | " + str(guild) + " | " + str(channel) + " | " + str(user) + "]: " + str(message) + "\n")
    log.close()
    #log_info(message.guild,message.channel,message.author,message.content)

#쓸때없는거(?)같은 괜찮은거
def change_data(B):
    B_lens = len(str(B))
    if B_lens >= 17:
        return round(B/1000000000000000,2), "PB"
    elif B_lens  >= 13:
        return round(B/1000000000000,2), "TB"
    elif B_lens >= 10:
        return round(B/1000000000,2), "GB"
    elif B_lens >= 7:
        return round(B/1000000,2), "MB"
    elif B_lens >= 4:
        return round(B/1000,2), "KB"
    else:
        return round(B,2), "B"

#자동업데이트가 필요한 함수들입니다. autopost1, autopost2
async def autopost1():
    await client.wait_until_ready()
    while not client.is_closed():
        await client.change_presence(status=discord.Status.online, activity=discord.Game("[접두어]help, [접두어]도움말 를 이용하여, 명령어를 알아보세요!"))
        await asyncio.sleep(3.0)
        total = 0
        for i in range(len(client.guilds)):
            total += len(client.guilds[i].members)
        await client.change_presence(status=discord.Status.online, activity=discord.Game("활동중인 서버갯수: " + str(len(client.guilds)) + "개, 유저수" + str(total) + "명"))
        await asyncio.sleep(3.0)
        await client.change_presence(status=discord.Status.online, activity=discord.Game("PUBG봇은 현재 OBT를 시행중입니다. 오류 발생시 신고해주시기 바랍니다."))
        await asyncio.sleep(3.0)
        await client.change_presence(status=discord.Status.online, activity=discord.Game("접두어를 잊어먹을 경우 !=접두어 정보를 통하여 얻을수 있습니다!"))
        await asyncio.sleep(3.0)
     
async def autopost2(time):
    a_time = int(time) * 60
    await client.wait_until_ready()
    while not client.is_closed():
        response = await requests.get("https://steamcommunity.com/app/578080")
        if response.status_code == 200:
            html = response.text
            players = html.split('<span class="apphub_NumInApp">')[1].split('</span>')[0]
            players = players.replace("In-Game","").replace(" ","").replace(",","")
            global DB_players
            for i in range(len(DB_players)-1):
                DB_players[i] = DB_players[i+1]
                DB_datetime[i] = DB_datetime[i+1]
            DB_players[len(DB_players)-1] = int(players)
            DB_datetime[len(DB_players)-1] = datetime.datetime.now().strftime('%H:%M')
            print("그래프에 반영합니다. 시간" + datetime.datetime.now().strftime('%H:%M') + ",유저수: " + str(players) + "명")
        else:
            print("그래프에 반영을 실패했습니다. 시간" + datetime.datetime.now().strftime('%H:%M'))
        await asyncio.sleep(a_time)

#동기적으로 처리할수 있는 전적검색 유형의 함수
def ranking(rank,lng): #랭킹별 티어 분석
    if rank == "0":
        if lng == 0:
            return "무티어","assets" + type_software + "Rank" + type_software + "unranked.png"
        else:
            return "Unranked"
    title = int(rank[0])
    if len(rank.replace('-','')) == 2:
        level = int(rank.replace('-','')[1])
    else:
        level = 0
    level_l = [""," I"," II"," III"," IV","V"]
    picture_l = ["unranked","bronze","silver","gold","platinum","diamond","elite","master","grandmaster"]
    if lng == 0:
        title_ko = ["초심","견습","경험","숙련","전문","달인","생존자","유일한 생존자"]
        return title_ko[title] + level_l[level],"assets" + type_software + "Rank" + type_software + picture_l[title] + ".png"
    elif lng == 1:
        title_en = ["Beginner","Novice","Experienced","Skilled","Specialist","Expert","Survivor","Lone Survivor"]
        return title_en[title] + level_l[level], "assets" + type_software + "Rank" + type_software + picture_l[title] + ".png"
    else:
        return "Not Found","assets" + type_software + "Rank" + type_software + picture_l[0] + ".png"

def time_num(playtime): #시간 계산, 불필요한 월단위, 일단위 등의 제거
    if playtime.month == 1:
        if playtime.day == 1:
            if playtime.hour == 0:
                if  playtime.minute == 0:
                    return str(playtime.second)  + "초"
                else:
                    return str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
            else:
                return str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
        else:
            return str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"
    else:
        return str(playtime.month-1)  + "일 " + str(playtime.day-1)  + "일 " + str(playtime.hour)  + "시간 " + str(playtime.minute)  + "분 " + str(playtime.second)  + "초"

async def response_num(response,message,update_msg,update): #에러 발생시, 코드를 통하여 분석
    a_num = int(response.status_code)
    if a_num == 200:
        return
    elif a_num == 400:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="닉네임을 입력해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 401:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="DB 불러오는것을 실패하였습니다. 잠시후 다시시도 해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 404:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="해당 유저를 찾을수 없습니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 415:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="콘텐츠 지정이 잘못되었습니다. 봇 제작자에게 문의해주시기 바랍니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    elif a_num == 429:
        if update:
            await update_msg.delete()
        embed = discord.Embed(title="에러",description="너무 많은 요청이 들어왔습니다. 잠시후 다시시도해주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    else:
        embed = discord.Embed(title="에러",description="알수없는 에러가 발생하였습니다. 관리자에게 문의해주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
    return

if platform.system() == "Windows":
    type_software = '\\'
elif platform.system() == "Linux":
    type_software = '/'
directory = os.path.dirname(os.path.abspath(__file__))
db_f = open(directory + type_software + "data" + type_software + "bot_info.json",mode='r')
db = db_f.read()
db_f.close()
db_json = json.loads(db)

db_ip = db_json["mysql"]["ip"]
db_user = db_json["mysql"]["user"]
db_pw = db_json["mysql"]["password"]
db_name = db_json["mysql"]["database"]

connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8') #클라이언트 API키 불러오기.
cur = connect.cursor()
cur.execute("SELECT * from PUBG_BOT")
client_list = cur.fetchall()
token = client_list[0][0]
pubg_token = client_list[0][2]
connect.close()

client = discord.Client()
header = {
  "Authorization": "Bearer " + pubg_token,
  "Accept": "application/vnd.api+json"
}

sample1 = { #마지막업데이트값의 샘플값입니다.
  "matches":{
    "years":0,
    "months":0,
    "days":0,
    "hours":0,
    "minutes":0
  },
  "normal":{
    "years":0,
    "months":0,
    "days":0,
    "hours":0,
    "minutes":0
  },
  "ranked":{
    "years":0,
    "months":0,
    "days":0,
    "hours":0,
    "minutes":0
  }
}

DB_players = [0] * 12
DB_datetime = ["starting"] * 12

async def matches(message,platform,update,update_msg,match,player_id,season):
    if update == 1:
         match_id = match
    elif update == 0:
        embed = discord.Embed(title="PUBG",description="최근 검색하실 전적을 고르시기 바랍니다.", color=0xffd619)
        msg1 = await message.channel.send(embed=embed)
        def check1(reaction,user):
            for i in range(5):
                if str(i+1) + "️⃣" == reaction.emoji:
                    return user.id == message.author.id and msg1.id==reaction.message.id
        for i in range(5):
            await msg1.add_reaction(str(i+1) +  "\U0000FE0F\U000020E3")
        reaction, user = await client.wait_for('reaction_add', check=check1)
        count = 1
        for i in range(5):
            if str(i+1) + "️⃣" == reaction.emoji:
                count = i
                break
        try:
            await msg1.clear_reactions()
        except discord.Forbidden:
            embed = discord.Embed(title="\U000026A0경고!",description="디스코드봇에게 \"메세지 관리\"권한을 부여해주시기 바랍니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
        if platform == "Kakao":
            url1 = "https://api.pubg.com/shards/kakao/players/" + player_id
        else:
            url1 = "https://api.pubg.com/shards/steam/players/" + player_id
        response1 = await requests.get(url1,headers=header)
        json_players = response1.json()
        match_id = json_players["data"]["relationships"]["matches"]["data"][count]["id"]
    def player(html,return_value,find_value):
        if type(html) == dict:
            json_data = html
        else:
            json_data = json.loads(html)
        included = json_data["included"]
        for i in range(len(included)-1):
            if included[i]["type"] == "participant":
                if find_value == "id" and included[i]["id"] == return_value:
                    return included[i]
                elif find_value == "id":
                    continue
                elif included[i]["attributes"]["stats"][find_value] == return_value:
                    return included[i]
    if platform == "Kakao":
        url2 = "https://api.pubg.com/shards/kakao/matches/" + match_id
    elif platform == "Steam":
        url2 = "https://api.pubg.com/shards/steam/matches/" + match_id
    response2 = await requests.get(url2,headers=header)
    json_data = response2.json()
    map_cache = json_data["data"]["attributes"]["mapName"]
    included1 = player(json_data,player_id,"playerId")
    user_id = included1["id"]
    timeSurvived = included1["attributes"]["stats"]["timeSurvived"]
    deals = included1["attributes"]["stats"]["damageDealt"]
    kills = included1["attributes"]["stats"]["kills"]
    assists = included1["attributes"]["stats"]["assists"]
    DBNOs = included1["attributes"]["stats"]["DBNOs"]
    distance = round((included1["attributes"]["stats"]["walkDistance"]+included1["attributes"]["stats"]["swimDistance"]+included1["attributes"]["stats"]["rideDistance"])/1000,3)
    deathType = included1["attributes"]["stats"]["deathType"]
    playtime = datetime.datetime.fromtimestamp(float(timeSurvived),timezone('UTC'))
    r_playtime = time_num(playtime)
    deathT = ["alive", "byplayer", "byzone", "suicide", "logout"]
    deathA = ["생존","유저","블루존","자살","로그 아웃"]
    map_name={
        "Desert_Main": "미라마",
        "DihorOtok_Main": "비켄디",
        "Erangel_Main": "에란겔",
        "Baltic_Main": "에란겔 (리마스터)",
        "Range_Main": "캠프 자칼",
        "Savage_Main": "사녹",
        "Summerland_Main": "카라킨"
    }
    for i in range(5):
        if deathType == deathT[i]:
            deathType = deathA[i]
            break
    included = json_data["included"]
    for i in range(len(included)-1):
        if included[i]["type"] == "roster":
            party = included[i]["relationships"]["participants"]["data"]
            a_tf = False
            for j in range(len(party)):
                if party[j]["id"] == user_id:
                    a_tf = True
                    break
            if a_tf:
                rank = included[i]["attributes"]["stats"]["rank"]
                break
    if not a_tf:
        team_member = "멤버를 불러오지 못했습니다."
    team_member = ""
    for i in range(len(party)):
        player_m = player(json_data,party[i]["id"],"id")
        team_member = team_member + "," + str(player_m["attributes"]["stats"]["name"])
    embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
    if platform == "Steam":
        icon = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "steam.png")
        embed.set_author(icon_url="attachment://steam.png",name=message.content.split(" ")[1] + "님의 전적")
    elif platform == "Kakao":
        icon = discord.File(directory + type_software + "assets" + type_software + "Icon" + type_software + "kakao.jpg")
        embed.set_author(icon_url="attachment://kakao.jpg",name=message.content.split(" ")[1] + "님의 전적")
    embed.add_field(name="팀원:",value=team_member.replace(',','',1),inline=False)
    embed.add_field(name="맵:",value=map_name[map_cache],inline=True)
    embed.add_field(name="킬/어시:",value=str(kills) + "회/" + str(assists) + "회",inline=True)
    embed.add_field(name="DBNOs:",value=str(DBNOs) + "회",inline=True)
    embed.add_field(name="결과:",value=deathType + "(" + str(rank) + "위)",inline=True)
    embed.add_field(name="이동한 거리:",value=str(distance) + "km",inline=True)
    embed.add_field(name="딜량:",value=str(round(deals,2)),inline=True)
    if update:
        await update_msg.delete()
    msg2 = await message.channel.send(embed=embed)
    try:
        await msg1.delete()
    except:
        pass
    for i in range(2):
        await msg2.add_reaction(str(i+1) + "\U0000FE0F\U000020E3")
    msg3 = await message.channel.send("\U00000031\U0000FE0F\U000020E3 : 종합전적 확인하기 \U00000032\U0000FE0F\U000020E3 : 메뉴중지")
    author = message.author
    message_id = msg2.id
    def check2(reaction, user):
        for i in range(2):
            if str(i+1) + "\U0000FE0F\U000020E3" == reaction.emoji:
                return user == author and message_id == reaction.message.id
    reaction,user = await client.wait_for('reaction_add', check=check2)
    if reaction.emoji == "\U00000032\U0000FE0F\U000020E3":
        await msg2.clear_reactions()
        await msg3.delete()
        return
    elif reaction.emoji == "\U00000031\U0000FE0F\U000020E3":
        await msg2.clear_reactions()
        await msg3.delete()
        if platform == "Kakao":
            url = "https://api.pubg.com/shards/kakao/players/" + player_id + "/seasons/" + season
        else:
            url = "https://api.pubg.com/shards/steam/players/" + player_id + "/seasons/" + season
        response1 = await requests.get(url,headers=header)
        if response1.status_code == 200:
            html = response1.text
        else:
            await response_num(response1,message,msg2,True)
            return
        #종합 전적 검색 함수
        return
    return

async def player(nickname,message):
    response = await requests.get("https://api.pubg.com/shards/steam/players?filter[playerNames]=" + nickname, headers=header)
    if response.status_code == 200:
        json_data = response.json()
    else:
        await response_num(response, message, None, False)
        return "False"
    return json_data["data"][0]["id"]

async def player_info(message,nickname):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    try:
        sql = "select id,platform from player where name=" + str(nickname)
        cur.execute(sql)
        cache = cur.fetchall()
        pubg_id = cache[0][0]
        pubg_platform = cache[0][1]
    except:
        embed = discord.Embed(title="플랫폼 선택!",description="해당 계정의 플랫폼을 선택해주세요.\n초기에 한번만 눌러주시면 됩니다.", color=0xffd619)
        msg = await message.channel.send(embed=embed)
        xbox = "<:XBOX:718482204035907586>"
        playstation = "<:PS:718482204417720400>"
        steam = "<:Steam:698454004656504852>"
        kakao = "<:kakao:718482204103278622>"
        stadia = "<:Stadia:718482205575348264>"
        await msg.add_reaction(xbox)
        await msg.add_reaction(playstation)
        await msg.add_reaction(steam)
        await msg.add_reaction(kakao)
        await msg.add_reaction(stadia)
        emoji = [xbox,playstation,steam,kakao,stadia]
        def check2(reaction,user):
            for i in range(5):
                if str(reaction.emoji)==str(emoji[i]):
                    return user == message.author
        try:
            reaction,user = await client.wait_for('reaction_add',check=check2,timeout=20)
        except asyncio.TimeoutError:
            embed = discord.Embed(title="에러!",description="입력시간이 초과되었습니다!", color=0xaa0000)
            await message.channel.send(embed=embed)
        count = 0
        for i in range(5):
            if str(reaction.emoji)==str(emoji[i]):
                count = i
        pubg_platform = count
        pubg_id = await player(nickname,message)
        sql = """insert into player(id,name,last_update,platform)
                values (%s, %s, %s, %s)"""
        cur.execute(sql, (pubg_id,nickname,json.dumps(sample1),count))
        connect.commit()
    finally:
        connect.close()
    return pubg_id, pubg_platform

async def season_status(player_id,season):
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    cur = connect.cursor()
    try:
        sql = "select html from NORMAL_STATUS where id=" + str(player_id) + "and season=" + str(season)
        cur.execute(sql)
        cache = cur.fetchone()
        return cache[0]
    except:
        url = "https://api.pubg.com/shards/steam/players/" + str(player_id) + "/seasons/" + str(season)
        response = await requests.get(url,headers=header)
        return_value = response.json()
        sql = """insert into NORMAL_STATUS(id,html)
                values (%s, %s, %s)"""
        cur.execute(sql, (player_id,return_value,season))
        connect.commit()
        return return_value

async def profile_total(message,pubg_platform,pubg_type,pubg_json,season,player_id):
    list_message = message.content.split(" ")
    embed = discord.Embed(color=0xffd619)
    game_mode = ["solo","duo","squad"]
    list_name = ["솔로(Solo)","듀오(Duo)","스쿼드(Squad)"]
    count = 3

async def profile(message,perfix):
    list_message = message.content.split(" ")
    nickname = ""
    helper = "**" + perfix + "전적[솔로|듀오|스쿼드(랭크 제외,선택) 혹은 1인칭|3인칭(랭크 경우,선택)] [1인칭|3인칭 혹은 일반|랭크] [닉네임(선택)] [시즌(선택)]**:"
    try:
        pubg_type = list_message[1]
    except:
        embed = discord.Embed(title="에러",description=helper + " 1인칭, 3인칭 혹은 일반, 랭크 중에서 선택하여 주세요.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    try:
        nickname = list_message[2]
    except:
        embed = discord.Embed(title="닉네임 작성 요청!",description="닉네임을 작성해주세요!\n취소를 하고싶으시다면 \"" + perfix + "취소\"를 적어주세요.", color=0xffd619)
        msg1 = await message.channel.send(embed=embed)
        def check1(m):
            return message.author.id == m.author.id and message.channel.id == m.channel.id
        try:
            a_nickname = await client.wait_for('message',check=check1,timeout=20)
            nickname = a_nickname.content
            if nickname == perfix + "취소":
                return
        except asyncio.TimeoutError:
            embed = discord.Embed(title="에러!",description="입력시간이 초과되었습니다!", color=0xaa0000)
            await message.channel.send(embed=embed)
    pubg_id, pubg_platform = await player_info(message,nickname)
    if pubg_type == "랭크":
        if list_message[0] == "전적":
        elif list_message[0] == "전적1인칭":
        elif list_message[0] == "전적3인칭":
    elif pubg_type == "1인칭":
        pubg_json = season_status(player_id,season)
        if list_message[0] == "전적":
            profile_total(message,pubg_platform,"fpp",pubg_json,season,player_id)
        elif list_message[0] == "전적솔로":
            profile_mode(message,pubg_platform,"solo-fpp",pubg_json,season,player_id)
        elif list_message[0] == "전적듀오":
            profile_mode(message,pubg_platform,"duo-fpp",pubg_json,season,player_id)
        elif list_message[0] == "전적스쿼드":
            profile_mode(message,pubg_platform,"squad-fpp",pubg_json,season,player_id)
    elif pubg_type == "일반" or pubg_type == "3인칭":
        if list_message[0] == "전적":
            profile_total(message,pubg_platform,"tpp",pubg_json,season,player_id)
        elif list_message[0] == "전적솔로":
            profile_mode(message,pubg_platform,"solo",pubg_json,season,player_id)
        elif list_message[0] == "전적듀오":
            profile_mode(message,pubg_platform,"duo",pubg_json,season,player_id)
        elif list_message[0] == "전적스쿼드":
            profile_mode(message,pubg_platform,"squad",pubg_json,season,player_id)
    else:
        embed = discord.Embed(title="에러",description=helper + " 1인칭,3인칭,일반,랭크 중에서 골라주세요. 일반 그리고 3인칭과는 같은 기능입니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        return

@client.event
async def on_ready():
    log_info('Discord API','system-log','PUBG_BOT','디스코드 봇 로그인이 완료되었습니다.')
    log_info('Discord API','system-log','PUBG_BOT',"디스코드봇 이름:" + client.user.name)
    log_info('Discord API','system-log','PUBG_BOT',"디스코드봇 ID:" + str(client.user.id))
    log_info('Discord API','system-log','PUBG_BOT',"디스코드봇 버전:" + str(discord.__version__))
    print('------------')
    answer = ""
    total = 0
    for i in range(len(client.guilds)):
        answer = answer + str(i+1) + "번째: " + str(client.guilds[i]) + "(" + str(client.guilds[i].id) + "):"+ str(len(client.guilds[i].members)) +"명\n"
        total += len(client.guilds[i].members)
    log_info('Discord API','guilds-log','PUBG_BOT',"방목록: \n" + answer + "방의 종합 멤버:" + str(total) + "명")

@client.event
async def on_message(message):
    author_id = message.author.mention.replace("<@","",).replace(">","").replace("!","")
    list_message = message.content.split(' ')
    if message.author == client.user or message.author.bot:
        return
    connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
    try:
        cur = connect .cursor()
        sql_prefix = "select * from SERVER_INFO where ID=" + str(message.guild.id)
        cur.execute(sql_prefix)
        cache = cur.fetchall()
        perfix = cache[0][1]
    except:
        perfix = "!="
    connect.close()
    if message.content.startswith(perfix + '전적'):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        await profile(message,perfix)
        return
    if message.content.startswith(perfix + '접두어') or message.content.startswith('!=접두어') :
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        if message.guild == None:
            embed = discord.Embed(title="접두어",description="DM에서는 접두어 기능을 사용하실수 없습니다.", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        try:
            mode = list_message[1]
        except:
            if perfix == "=":
                embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
            else:
                embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        else:
            connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
            cur = connect .cursor()
            if mode == "설정":
                if not(is_admin(message) or is_manager(author_id)):
                    embed = discord.Embed(title="접두어",description=message.guild.name + "봇 주인 혹은 서버 관리자외에는 접두어를 변경할 권한이 없습니다.", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.close()
                    return
                try:
                    n_perfix = list_message[2]
                    if len(n_perfix) > 4 or len(list_message) > 3 or n_perfix.find('\t') != -1 or n_perfix.find('\n') != -1 :
                        if perfix == "=":
                            embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n사용금지 단어가 포함되어 있습니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                        else:
                            embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n사용금지 단어가 포함되어 있습니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                        await message.channel.send(embed=embed)
                        connect.close()
                        return
                except:
                    if perfix == "=":
                        embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                    else:
                        embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.commit()
                    connect.close()
                    return
                sql_T = "select EXISTS (select * from SERVER_INFO where ID=" + str(message.guild.id) + ") as success"
                cur.execute(sql_T)
                c_TF = cur.fetchall()[0][0]
                if c_TF == 0:
                    sql = "insert into SERVER_INFO(ID,PERFIX) values (%s, %s)"
                    cur.execute(sql,(message.guild.id,n_perfix))
                else:
                    sql = "update SERVER_INFO set PERFIX='" + n_perfix + "' where ID=" + str(message.guild.id)
                    cur.execute(sql)
                embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 " + n_perfix + "(명령어)으로 성공적으로 설정되었습니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                connect.commit()
                connect.close()
            elif mode == "초기화":
                if not(is_admin(message) or is_manager(author_id)):
                    embed = discord.Embed(title="접두어",description=message.guild.name + "봇 주인 혹은 서버 관리자외에는 접두어를 변경할 권한이 없습니다.", color=0xffd619)
                    await message.channel.send(embed=embed)
                    connect.close()
                    return
                sql_T = "select EXISTS (select * from SERVER_INFO where ID=" + str(message.guild.id) + ") as success"
                cur.execute(sql_T)
                c_TF = cur.fetchall()[0][0]
                if c_TF == 0:
                    embed = discord.Embed(title="접두어",description="접두어가 이미 기본설정(!=)으로 되어 있습니다...", color=0xffd619)
                else:
                    sql = "update SERVER_INFO set PERFIX='!=' where ID=" + str(message.guild.id)
                    cur.execute(sql)
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 !=(명령어)으로 성공적으로 초기화가 완료되었습니다.", color=0xffd619)
                    connect.commit()
                connect.close()
                await message.channel.send(embed=embed)
            elif mode == "정보":
                try:
                    sql_perfix = "select * from SERVER_INFO where ID=" + str(message.guild.id)
                    cur.execute(sql_perfix)
                    c_perfix = cur.fetchall()
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 " + str(c_perfix[0][1]) + "(명령어)입니다.", color=0xffd619)
                except:
                    embed = discord.Embed(title="접두어",description=message.guild.name + "서버의 접두어는 !=(명령어)입니다.", color=0xffd619)
                await message.channel.send(embed=embed)
                connect.close()
                return
            else:
                if perfix == "=":
                    embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다.", color=0xffd619)
                else:
                    embed = discord.Embed(title="에러",description="!=접두어 [설정/초기화/정보] [접두어(설정시 한정)] 혹은 " + perfix + "접두어 [설정/초기화/정보] [접두어(설정시 한정)]\n위와 같이 작성해주시기 바랍니다.\n 접두어를 설정시 \\n,\\t,(공백) 를 사용하시면 안됩니다. 또한 5자 미만으로 하셔야 합니다. 이점 참조하시기 바랍니다", color=0xffd619)
                connect.close()
                await message.channel.send(embed=embed)
                return
    if message.content == perfix + "도움" or message.content == perfix + "help":
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        embed = discord.Embed(title="도움말",color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
        embed.add_field(name=perfix + "스배 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 종합 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "스배솔로 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 솔로 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "스배듀오 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 듀오 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "스배스쿼드 [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 스쿼드 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "스배솔로(1인칭) [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 1인칭 솔로 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "스배듀오(1인칭) [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 1인칭 듀오 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "스배스쿼드(1인칭) [닉네임] [시즌(선택)]:",value="스팀 배틀그라운드 1인칭 스쿼드 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "카배 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 종합 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "카배솔로 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 솔로 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "카배듀오 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 듀오 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "카배스쿼드 [닉네임] [시즌(선택)]:",value="카카오 배틀그라운드 스쿼드 전적을 검색해 줍니다.",inline=False)
        embed.add_field(name=perfix + "서버상태:",value="배틀그라운드 서버 상태를 알려줍니다.",inline=False)
        embed.add_field(name=perfix + "ping:",value="디스코드봇의 ping을 알려줍니다.",inline=False)
        embed.add_field(name=perfix + "접두어 [설정/초기화/정보] [(설정 사용시)설정할 접두어]:",value="접두어를 설정합니다.",inline=False)
        await message.channel.send(embed=embed)
        return
    if message.content == perfix + "서버상태":
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        response = await requests.get("https://steamcommunity.com/app/578080")
        if response.status_code == 200:
            html = response.text
        else:
            embed = discord.Embed(title="에러",description=message.guild.name + "정보를 불러오기에 실패했습니다..", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        plt.title('Max Players')
        plt.plot(DB_datetime,DB_players,color='blue', marker='o',label = 'Max Players')
        plt.xlabel('time')
        plt.ylabel('user')
        print("그래프 만들기 성공!")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        file = discord.File(buf,filename="cache.png")
        players = html.split('<span class="apphub_NumInApp">')[1].split('</span>')[0].replace("In-Game","").replace(" ","")
        embed = discord.Embed(color=0xffd619,timestamp=datetime.datetime.now(timezone('UTC')))
        embed.add_field(name="서버상태:",value="정상",inline=True)
        embed.add_field(name="동접자수:",value=players + "명 유저가 플레이 중입니다.",inline=True)
        embed.set_image(url="attachment://cache.png")
        await message.channel.send(file=file,embed=embed)
        return
    if message.content.startswith(perfix + 'eval') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        code =  message.content.replace(perfix + 'eval ','')
        if code == "" or code == perfix + "eval":
            embed = discord.Embed(title="에러!",description="내용을 적어주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        answer = eval(code)
        embed = discord.Embed(title="eval",description=answer, color=0xffd619)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(perfix + 'hellothisisverification'):
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        await message.channel.send("건유1019#0001(340373909339635725)")
        return
    if message.content == perfix + "ping":
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        now = datetime.datetime.utcnow()
        response_ping_c = now - message.created_at
        reading_ping = float(str(response_ping_c.seconds) + "." +  str(response_ping_c.microseconds))
        embed = discord.Embed(title="Pong!",description="클라이언트 핑상태: " + str(round(client.latency * 1000,2)) + "ms\n읽기 속도: " + str(round(reading_ping * 1000,2)) + "ms", color=0xffd619)
        msg = await message.channel.send(embed=embed)
        now = datetime.datetime.utcnow()
        response_ping_a = msg.created_at - now
        response_ping = float(str(response_ping_a.seconds) + "." +  str(response_ping_a.microseconds))
        embed = discord.Embed(title="Pong!",description="클라이언트 핑상태: " + str(round(client.latency * 1000,2)) + "ms\n읽기 속도: " + str(round(reading_ping * 1000,2)) + "ms\n출력 속도: " + str(round(response_ping * 1000,2)) + "ms", color=0xffd619)
        await msg.edit(embed=embed)
        return
    if message.content == perfix + '시스템':
        log_info(message.guild,message.channel,message.author,message.content)
        if is_banned(author_id,message):
            return
        data1 = str(psutil.cpu_percent(interval=None, percpu=False))
        data2 = str(psutil.virtual_memory().percent)
        data3 = str(psutil.disk_usage('/').percent)
        data4 = platform.system() + str(platform.release())
        data5 = psutil.virtual_memory()
        data6 = psutil.disk_usage('/')
        if platform.system() == "Linux":
            data7 = str(round(float(str(psutil.sensors_temperatures()).split('current=')[1].split(',')[0]),2))
        data8 = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
        total_RAM,total_type_RAM = change_data(psutil.virtual_memory()[0])
        used_RAM,used_type_RAM = change_data(psutil.virtual_memory()[3])
        total_SSD,total_type_SSD = change_data(psutil.disk_usage('/')[0])
        used_SSD,used_type_SSD = change_data(psutil.disk_usage('/')[1])
        embed = discord.Embed(title="[시스템 정보]", color=0xffd619)
        embed.add_field(name="CPU:", value=data1 + "%", inline=True)
        embed.add_field(name="부팅시간:", value=data8, inline=True)
        embed.add_field(name="메모리:", value=data2 + "%(" + str(used_RAM) + str(used_type_RAM) + '/' + str(total_RAM) + str(total_type_RAM) + ')', inline=False)
        embed.add_field(name="저장공간:", value=data3 +"%(" + str(used_SSD) + str(used_type_SSD) + '/' + str(total_SSD) + str(total_type_SSD) + ')' , inline=False)
        embed.add_field(name="소프트웨어:", value=data4, inline=False)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(perfix + '블랙리스트 추가') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            mention_id = list_message[2]
        except:
            embed = discord.Embed(title="에러!",description="닉네임을 기재해주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        cache_data = mention_id.replace("<@","",).replace(">","").replace("!","")
        if is_manager(cache_data):
            embed = discord.Embed(title="에러!",description="관리자는 블랙리스트에 추가할수 없습니다!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
        cur = connect .cursor()
        sql_Black = "insert into BLACKLIST(ID) value(%s)"
        cur.execute(sql_Black,cache_data)
        connect.commit()
        connect.close()
        embed = discord.Embed(title="Blacklist!",description=mention_id + "가 블랙리스트에 추가되었습니다!", color=0xaa0000)
        await message.channel.send(embed=embed)
        return
    if message.content.startswith(perfix + '블랙리스트 여부'):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            tester_id = list_message[2].replace("<@","",).replace(">","").replace("!","")
        except:
            tester_id = author_id
        embed = discord.Embed(title="Blacklist!",description="해당 유저가 밴당했는지 확인하는 중입니다.", color=0xaa0000)
        msg = await message.channel.send(embed=embed)
        cache = is_banned(tester_id,message)
        if cache:
            embed = discord.Embed(title="Blacklist!",description="이 사람은 블랙리스트에 등재되어 있습니다.", color=0xaa0000)
        else:
            embed = discord.Embed(title="Blacklist!",description="이 사람은 블랙리스트에 등재되어 있지 않습니다.", color=0xaa0000)
        await message.channel.send(embed=embed)
        await msg.delete()
    if message.content.startswith(perfix + '블랙리스트 제거') and is_manager(author_id):
        log_info(message.guild,message.channel,message.author,message.content)
        try:
            mention_id = list_message[2]
        except:
            embed = discord.Embed(title="에러!",description="닉네임을 기재해주세요!", color=0xffd619)
            await message.channel.send(embed=embed)
            return
        cache_data1 = mention_id.replace("<@","",).replace(">","").replace("!","")
        connect = pymysql.connect(host=db_ip, user=db_user, password=db_pw,db=db_name, charset='utf8')
        cur = connect .cursor()
        sql_delete = "delete from BLACKLIST where ID=%s"
        try:
            cur.execute(sql_delete,cache_data1)
        except:
            embed = discord.Embed(title="Blacklist!",description=mention_id + "는, 블랙리스트에 추가되어 있지 않습니다.", color=0xaa0000)
            await message.channel.send(embed=embed)
            connect.commit()
            connect.close()
            return
        connect.commit()
        connect.close()
        embed = discord.Embed(title="Blacklist!",description=mention_id + "가 블랙리스트에서 제거되었습니다!", color=0xaa0000)
        await message.channel.send(embed=embed)
        return

@client.event
async def on_resumed():
    log_info('Discord API','system-log','PUBG_BOT','재시작 되었습니다.')

client.loop.create_task(autopost1())
client.loop.create_task(autopost2(30))
client.run(token)
