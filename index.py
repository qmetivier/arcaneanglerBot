import os

import requests
import discord
from datetime import datetime
import zoneinfo
from discord.ext import commands, tasks
from dotenv import load_dotenv
import json

load_dotenv()

bot = commands.Bot(command_prefix="p ", intents=discord.Intents.default())
channel_name = os.getenv("CHANNEL")
token = os.getenv("TOKEN")
app_token = os.getenv("APP_TOKEN")

base_url = "https://arcaneangler.com/api"
anomalie_url = base_url + "/anomalies/current"
derby_url = base_url + "/derby/current"
tournament_url = base_url + "/guild/tournaments/current"
headers = {
    'content-type': "application/json",
    'Authorization': "Bearer " + app_token,
    'cache-control': "no-cache"
}


def get_right_channels():
    channels = []
    for channel in bot.get_all_channels():
        if channel.name == channel_name:
            channels.append(channel)

    return channels


def is_within_30min(date_debut: str):
    date_debut = datetime.fromisoformat(date_debut.replace("Z", "+00:00"))
    paris_tz = zoneinfo.ZoneInfo("Europe/Paris")
    now = datetime.now(paris_tz)
    diff = now - date_debut

    return 30 * 60 > abs(diff.total_seconds()) > 25 * 60


@bot.event
async def on_ready():
    print("Le bot est prêt.")
    notif_anomalie.start()
    notif_derby.start()
    notif_tournament.start()


@tasks.loop(minutes=5)
async def notif_anomalie():
    channels = get_right_channels()
    request = requests.request("GET", anomalie_url, headers=headers)
    if request.status_code != 200:
        return
    if 'nextSpawnTime' not in request.json():
        return

    next_spawn_time = request.json()['nextSpawnTime']
    if is_within_30min(next_spawn_time):
        for channel in channels:
            await bot.get_channel(channel.id).send(
                "<@&1476885924767076485> Une anomalie arrive dans moins de 30 minutes ! Chargez !!! Dans quelques minutes..."
            )


@tasks.loop(minutes=5)
async def notif_derby():
    channels = get_right_channels()
    request = requests.request("GET", derby_url, headers=headers)
    if request.status_code != 200:
        return

    derby_infos_upcoming = request.json()['upcoming'][0]

    date_debut = derby_infos_upcoming['start_time']
    if is_within_30min(date_debut):
        for channel in channels:
            await bot.get_channel(channel.id).send(
                "<@&1476885924767076485> Un derby commence dans moins de 30 minutes biome "
                + str(derby_infos_upcoming['biome_id'])
                + " ! Chargez !!! Dans quelques minutes..."
            )


@tasks.loop(minutes=5)
async def notif_tournament():
    channels = get_right_channels()
    request = requests.request("GET", tournament_url, headers=headers)
    if request.status_code != 200:
        return

    tournament_infos_upcoming = request.json()['upcoming'][0]

    date_debut = tournament_infos_upcoming['start_time']
    if is_within_30min(date_debut):
        for channel in channels:
            await bot.get_channel(channel.id).send(
                "<@&1476885924767076485> Un tournoie commence dans moins de 30 minutes biome "
                + str(tournament_infos_upcoming['biome_id'])
                + " ! Chargez !!! Dans quelques minutes..."
            )

bot.run(token)
