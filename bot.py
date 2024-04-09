from discord.ext import commands, tasks
import discord
import config
import sqlite3
import datetime
import pytz

tokyo_tz = pytz.timezone('Asia/Tokyo')

dbname = 'SOUZAI.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

intents = discord.Intents.all()
client = discord.Client(intents=intents)

bot = commands.Bot(
    command_prefix="&",
    case_insensitive=True, 
    intents=intents
)

@bot.event
async def on_ready():
    print("好きな総菜発表ドラゴンが好きな総菜を発表します")
    alarm.start()

async def send_alarm_message(user_id, channel_id):
    channel = bot.get_channel(channel_id)
    random_row = await bot.loop.run_in_executor(None, fetch_random_food)
    if channel:  # チャンネルが見つかった場合
        await channel.send(f'<@{user_id}>' + ' ' + random_row[0])
    else:
        print('チャンネルが見つからないよー！')

@tasks.loop(seconds=30)
async def alarm():
    now = datetime.datetime.now(tokyo_tz).strftime('%H:%M')
    rows = await bot.loop.run_in_executor(None, fetch_next_alarm, now)
    for row in rows:
        id, user_id, channel_id, time, is_loop = row
        await send_alarm_message(int(user_id), int(channel_id))
        if is_loop == 0:
            cur.execute('DELETE FROM times WHERE id = ?',(id,))
            conn.commit()
            
def fetch_random_food():
    conn = sqlite3.connect('SOUZAI.db')
    cur = conn.cursor()
    cur.execute('SELECT name FROM foods ORDER BY RANDOM() LIMIT 1')
    row = cur.fetchone()
    conn.close()
    return row

def fetch_next_alarm(now):
    conn = sqlite3.connect('SOUZAI.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM times WHERE time = ? ORDER BY time ASC', (now,))
    rows = cur.fetchall()
    conn.close()
    return rows

@bot.event
async def on_message(message):
    
    if message.author == client.user:
        return
    
    if message.author.bot:
        return
    
    if message.content.endsswith('&set'):
            time, is_loop = message.content.replace("&set", "").strip()
            if time and is_loop:
                if is_valid_time(time):
                    if is_valid_is_loop(is_loop):
                        if is_loop == 'once':
                            loop = 0
                        elif is_loop == 'loop':
                            loop = 1
                        cur.execute('INSERT INTO times(user_id, channel_id, time, is_loop) VALUES (?, ?, ?, ?)',(message.author.id, message.channel.id, time, loop))
                        conn.commit()
                        await message.reply(f"{time}に発表するよ！")
                    else:
                        await message.reply("アラームのセットには、HH:MMの時間とループするかどうかの指定が必要です。\n (例) \n 09:30 once")
                else:
                    await message.reply("アラームのセットには、HH:MMの時間とループするかどうかの指定が必要です。\n (例) \n 09:30 once")
            else:
                await message.reply("アラームのセットには、HH:MMの時間とループするかどうかの指定が必要です。\n (例) \n 09:30 once")
            
def is_valid_time(time):
    try:
        datetime.strptime(time, "%H:%M")
        return True
    except ValueError:
        return False

def is_valid_is_loop(is_loop):
    if int(is_loop) == 'once' or 'loop':
        return True
    else:
        return False
            

@bot.event
async def on_close():
    conn.close()

bot.run(config.DISCORD_TOKEN)