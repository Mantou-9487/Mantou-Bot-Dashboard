from nextcord.ext import commands,ipc
import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template,request,session,redirect,url_for
from flask_discord import DiscordOAuth2Session
from threading import Thread
import asyncio
app = Flask(__name__,template_folder="Templates")
ipc_client = ipc.Client(secret_key = "s-n2fdZUbF0gBlex0nvgGidD74SroJrc")
token = os.getenv("TOKEN")
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
app.config['SECRET_KEY'] = os.urandom(24)
app.config["DISCORD_CLIENT_ID"] = 949535524652216350   # Discord client ID.
app.config["DISCORD_CLIENT_SECRET"] = "s-n2fdZUbF0gBlex0nvgGidD74SroJrc"   # Discord client secret.
app.config["DISCORD_REDIRECT_URI"] = "https://www.mantougame.cf/callback"
app.config["DISCORD_BOT_TOKEN"] = token
#https://www.mantougame.cf/callback
discord = DiscordOAuth2Session(app)


@app.route('/')
def hello_world():
    return render_template("index.html",authorized=discord.authorized)

@app.route('/login')
async def login():
	return discord.create_session()

@app.route('/callback')
async def callback():
    try:
        await discord.callback()
    except Exception:
        pass
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
async def dashboard():
	if not discord.authorized:
		print("沒過驗證")
		return redirect(url_for("login")) 

	guild_count = await ipc_client.request("get_guild_count")
	guild_ids = await ipc_client.request("get_guild_ids")

	user_guilds = discord.fetch_guilds()

	guilds = []

	for guild in user_guilds:
		if guild.permissions.administrator:			
			guild.class_color = "green-border" if guild.id in guild_ids else "red-border"
			guilds.append(guild)

	guilds.sort(key = lambda x: x.class_color == "red-border")
	name = (discord.fetch_user()).name
	return render_template("dashboard.html", guild_count = guild_count, guilds = guilds, username=name)

@app.route("/dashboard/<int:guild_id>")
async def dashboard_server(guild_id):
	if not discord.authorized:
		return redirect(url_for("login")) 

	guild = await ipc_client.request("get_guild", guild_id = guild_id)
	if guild is None:
		return redirect(f'https://discord.com/oauth2/authorize?&client_id={app.config["DISCORD_CLIENT_ID"]}&scope=bot&permissions=8&guild_id={guild_id}&response_type=code&redirect_uri={app.config["DISCORD_REDIRECT_URI"]}')
	return guild["name"]

def run():
    app.run(host='0.0.0.0', port=10000, use_reloader=False, debug=True)

def stay():
	thread = Thread(target=run)
	thread.start()