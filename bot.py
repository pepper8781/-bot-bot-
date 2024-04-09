from discord.ext import commands, tasks
import discord
import config
import sqlite3
from datetime import datetime
import pytz
import re

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
    now = datetime.now(tokyo_tz).strftime('%H:%M')
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
    
    if message.content.startswith('&set'):
        components = message.content.split()
        if len(components) == 3:
            _, time_input, loop_input = components
            if re.match(r'^[0-2][0-9]:[0-5][0-9]$', time_input):
                try:
                    datetime.strptime(time_input, "%H:%M")
                    if loop_input in ['once', 'loop']:
                        if loop_input == 'once':
                            loop = 0
                        else:
                            loop = 1
                        cur.execute('INSERT INTO times(user_id, channel_id, time, is_loop) values(?, ?, ?, ?)',(message.author.id, message.channel.id, time_input, loop))
                        conn.commit()
                        await message.reply(f"{time_input}に好きな総菜を発表するよ！")
                    else:
                        await message.reply("ループ指定が不正です。`once` または `loop` を指定してください。")
                except ValueError:
                    await message.reply("指定された時間が無効です。")
            else:
                await message.reply("時間は HH:MM 形式で指定してください。")
        else:
            await message.reply("コマンドの形式が正しくありません。`&set HH:MM once|loop` の形式で入力してください。")

    if message.content.startswith('&che'):
        cur.execute('SELECT * FROM times WHERE user_id = ? ORDER BY time ASC', (message.author.id,))
        rows = cur.fetchall()
        if rows:
          messages = [f'<@{message.author.id}>さんのアラーム：']
          for row in rows:
            id, user_id, channel_id, time, is_loop = row
            if is_loop == 0:
                loop = 'once'
            else:
                loop = 'loop'
            messages.append(f'{id}|{time}|{loop}')
          await message.channel.send('\n'.join(messages))
        else:
          await message.reply("アラームが登録されていません。")
    
    if message.content.startswith('&del'):
        components = message.content.split()
        if len(components) == 2:
            _, id = components
            if id == 'all':
                cur.execute('DELETE FROM times WHERE user_id = ?',(message.author.id,))
                conn.commit()
                await message.reply("削除しました")
            elif is_halfwidth_number(id):
                cur.execute('SELECT id FROM times WHERE id = ?', (int(id),))
                row = cur.fetchone()
                if row:
                    cur.execute('DELETE FROM times WHERE id = ?',(int(id),))
                    conn.commit()
                    await message.reply("削除しました")
                else:
                    await message.reply(f"idが{id}のアラームはありません")
            else:
                await message.reply("削除したいidを数字かallで指定してください")
        else:
            message.reply("コマンドの形式が正しくありません。`&del int(id)|all` の形式で入力してください。")

def is_halfwidth_number(input_str):
    return re.fullmatch(r'\d+', input_str) is not None
            
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