# id 719658490939048058
# permission int 8
# https://discordapp.com/oauth2/authorize?client_id=719658490939048058&scope=bot&permissions=8
token = "NzE5NjU4NDkwOTM5MDQ4MDU4.Xt6ocA.OoyFX3FjWAm3S8bU2H2DuOL6ugM"

import time
import asyncio
import discord
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
style.use("fivethirtyeight")

client = discord.Client() #initiates client

def community_report(guild):
	online = 0
	idle = 0
	offline = 0
	for m in guild.members:
		if str(m.status) == "online":
			online += 1
		if str(m.status) == "offline":
			offline += 1
		if str(m.status) != "online" and str(m.status) != "offline":
			idle += 1
	return online, idle, offline

async def user_metrics_background_task():
	await client.wait_until_ready()
	global mybot_guild
	mybot_guild=client.get_guild(717396352094437446)

	while not client.is_closed():
		try:
			online, idle, offline = community_report(mybot_guild)
			with open("usermetrics.csv", "a") as f:
				f.write(f"{int(time.time())},{online},{idle},{offline}\n")

			df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
			df['date'] = pd.to_datetime(df['time'],unit='s')
			df['total'] = df['online'] + df['offline'] + df['idle']
			df.drop("time", 1,  inplace=True)
			df.set_index("date", inplace=True)
			print(df.head())
			plt.clf()
			df['online'].plot()
			plt.legend()
			plt.savefig("online.png")

			await asyncio.sleep(600)

		except Exception as e:
			print(str(e))
			await asyncio.sleep(600)

async def game_notify():
	await client.wait_until_ready()
	global mybot_guild
	user = client.get_user(279751543593500672)
	while not client.is_closed():
		try:
			voice_channel_list = mybot_guild.voice_channels
			for voice_channels in voice_channel_list:
				if len(voice_channels.members) >= 1:
					for members in voice_channels.members:
						if members.id == 27975154359350067:
							continue
						else:
							await user.send("{} members in {}".format(len(voice_channels.members), voice_channels.name))
							for members in voice_channels.members:
								if members.nick == None:
									await user.send(members.name)
								else:
									await user.send(members.nick)
				await asyncio.sleep(3600)						
			await asyncio.sleep(300)

		except Exception as e:
			print(str(e))
			await asyncio.sleep(600)

@client.event #event decorator/wrapper
async def on_ready():
	global mybot_guild
	print(f"We have logged in as {client.user}")

@client.event 
async def on_message(message):
	global mybot_guild
	print(f"{message.channel}:{message.author}: {message.author.name}: {message.content}")

	if "mybot.member_count()" == message.content.lower():
		await message.channel.send(f"```py\n{mybot_guild.member_count}```")

	elif "myBot.logout()" == message.content.lower():
		await client.close()

	elif "!report" == message.content.lower():
		online, idle, offline = community_report(mybot_guild)
		await message.channel.send(f"```py\nOnline: {online}.\nIdle: {idle}.\nOffline: {offline}.```")
		file= discord.File("online.png", filename="online.png")
		await message.channel.send("online.png",file=file)

	elif message.content.startswith('!game'):
		for mybot_guild in client.guilds:
			for member in mybot_guild.members:
				if str(member.status) == "online":
					if str(member.activity) != "None":
						await message.channel.send(f"```py\n{member} is playing : {member.activity.name}.```")
					else:
						await message.channel.send(f"```py\n{member} is playing : {member.activity}.```")

	elif message.content.startswith('!voice'):
		voice_channel_list = mybot_guild.voice_channels
		for voice_channels in voice_channel_list:
			if len(voice_channels.members) != 0:
				if len(voice_channels.members) == 1:
					await message.channel.send("{} member in {}".format(len(voice_channels.members), voice_channels.name))
				else:
					await message.channel.send("{} members in {}".format(len(voice_channels.members), voice_channels.name))
				for members in voice_channels.members:
					#if user does not have a nickname in the guild, send thier discord name. Otherwise, send thier guild nickname
					if members.nick == None:
						await message.channel.send(members.name)
					else:
						await message.channel.send(members.nick)

if __name__ == "__main__":
	client.loop.create_task(user_metrics_background_task())
	client.loop.create_task(game_notify())
	client.run(token)