from keys import TOKEN, translateToken
from languages import languages
import ast
from gtts import gTTS
from discord import FFmpegPCMAudio
import requests
import discord
from discord.ext import commands
from discord import Option, OptionChoice

#setting the proper intents
intent = discord.Intents.default()
intent.message_content = True

#creation of the client and tree of commands
client = discord.Bot(intents=intent)

#language that was selected by user
client.lang = None
#check whether bot is already in a voice channel
client.vc = False


@client.event
async def on_connect():
	if client.auto_sync_commands:
		synced = await client.sync_commands()
	print(f"{client.user.name} connected.")
	print("The bot is now ready for use!")


@client.slash_command(name="join", description="Make bot join your voice channel")
async def join(interaction: discord.ApplicationContext):
	if(interaction.user.voice and client.vc == False):
		client.vc = True
		await interaction.user.voice.channel.connect()
		await interaction.response.send_message("Successfully joined Voice Channel")
	elif(client.vc == True):
		await interaction.response.send_message("Already in a Voice Channel")
	else:
		await interaction.response.send_message("Currently not in a Voice Channel")


@client.slash_command(name="leave", description="Make bot leave your voice channel")
async def leave(interaction: discord.ApplicationContext):
	if(client.vc == True):
		client.vc = False
		await client.voice_clients[0].disconnect()
		await interaction.response.send_message("Bot left the Voice Channel")
	else:
		await interaction.response.send_message("Bot is not in a Voice Channel")

@client.slash_command(name="set", description="Set the language for translation")
async def set(interaction: discord.ApplicationContext, language: Option(str, choices=languages)):
	client.lang = language
	print(client.lang)
	await interaction.response.send_message(f"The language has been set to: {client.lang}")
	

@client.message_command(name="Translate")
async def translate(interaction: discord.ApplicationContext, message: discord.Message):
	#check to see if user has set the target language for translation
	if(client.lang == None):
		await interaction.response.send_message("Please set the language for translation by using /set {language}")
	else:
		try:
			url = "https://google-translator9.p.rapidapi.com/v2"
			payload = {
				"q": message.content,
				"target": client.lang,
				"format": "text"
			}
			headers = {
				"content-type": "application/json",
				"X-RapidAPI-Key": translateToken,
				"X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
			}
			response = requests.post(url, json=payload, headers=headers)
			response = str(response.json())
			data = ast.literal_eval(response)
			await interaction.response.send_message(f'"{message.content}" -> {data["data"]["translations"][0]["translatedText"]}')
		except Exception as e:
			await interaction.response.send_message(e)


@client.message_command(name="Translate and Speak")
async def translate(interaction: discord.ApplicationContext, message: discord.Message):
	if(client.vc == True and client.lang != None):
		try:
			url = "https://google-translator9.p.rapidapi.com/v2"
			payload = {
				"q": message.content,
				"target": client.lang,
				"format": "text"
			}
			headers = {
				"content-type": "application/json",
				"X-RapidAPI-Key": translateToken,
				"X-RapidAPI-Host": "google-translator9.p.rapidapi.com"
			}
			response = requests.post(url, json=payload, headers=headers)
			response = str(response.json())
			data = ast.literal_eval(response)
			tts = gTTS(text=data["data"]["translations"][0]["translatedText"], lang=client.lang)
			tts.save("text.mp3")

			await interaction.response.send_message(f'"{message.content}" -> {data["data"]["translations"][0]["translatedText"]}')
			interaction.bot.voice_clients[0].play(FFmpegPCMAudio("text.mp3"))
		except Exception as e:
				await interaction.response.send_message(e)
	elif(client.vc == False):
		await interaction.response.send_message("Please have the bot join a voice channel first using /join")
	else:
		await interaction.response.send_message("Please set the language for translation by using /set {language}")


@client.slash_command(name="help", description="Additional info on how to use bot")
async def join(interaction: discord.Interaction):
	await interaction.response.send_message('''/join will make the bot join if you are in a voice channel\n\n/leave will make the bot leave the voice channel if it is in one\n\n/set {selection} will set the bot's language to translate to\n\nFor translations, right click on a message and select the one of the following:\n"Translate" will simply translate a message (must have used /set first)\n"Translate and Speak" will translate message and say it out loud in voice channel (must have used /join and /set first)''')


client.run(TOKEN)
