from datetime import datetime
import hikari
import requests
import re 
import aiohttp
import lightbulb
from lightbulb.utils import pag, nav
import asyncio


valorant_plugin = lightbulb.Plugin("Valorant")

def getVersion():
    versionData = requests.get("https://valorant-api.com/v1/version")
    versionDataJson = versionData.json()['data']
    final = f"{versionDataJson['branch']}-shipping-{versionDataJson['buildVersion']}-{versionDataJson['version'][-6:]}"
    return final

def priceconvert(skinUuid, offers_data):
    for row in offers_data["Offers"]:
        if row["OfferID"] == skinUuid:
            for cost in row["Cost"]:
                return row["Cost"][cost]

def username_to_data(username, password):
    session = requests.session()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
        'scope': 'account openid',

    }
    headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RiotClient/43.0.1.4195386.4190634 rso-auth (Windows;10;;Professional, x64)'
    }

    r = session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)

    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data, headers=headers)
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(r.json()['response']['parameters']['uri'])[0]
    access_token = data[0]

    headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
    }
    
    r = session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
    entitlements_token = r.json()['entitlements_token']

    r = session.post('https://auth.riotgames.com/userinfo', headers=headers, json={})
    user_id = r.json()['sub']
    session.close()
    return [access_token, entitlements_token, user_id]

def skins(region, entitlements_token, access_token, user_id):
    headers = {
        'X-Riot-Entitlements-JWT': entitlements_token,
        'Authorization': f'Bearer {access_token}',
    }

    r = requests.get(f'https://pd.{region}.a.pvp.net/store/v2/storefront/{user_id}', headers=headers)

    skins_data = r.json()
    single_skins = skins_data["SkinsPanelLayout"]["SingleItemOffers"]

    weapon_fetch = requests.get('https://valorant-api.com/v1/weapons/skinlevels')
    weapon_fetch = weapon_fetch.json()

    all_weapons = requests.get("https://valorant-api.com/v1/weapons")
    data_weapons = all_weapons.json()

    single_skins_images = []
    single_skins_tiers_uuids = []

    for skin in single_skins:
        for weapons_list in data_weapons['data']:
            for skin1 in weapons_list['skins']:
                if skin in str(skin1):
                    if skin1["chromas"][0]["displayIcon"] != None:
                        single_skins_images.append(skin1["chromas"][0]["displayIcon"])
                    else:
                        single_skins_images.append(skin1["chromas"][0]["fullRender"])
                    single_skins_tiers_uuids.append(skin1['contentTierUuid'])

    headers = {
        'X-Riot-Entitlements-JWT': entitlements_token,
        'Authorization': f'Bearer {access_token}',
        'X-Riot-ClientVersion': getVersion(),
        "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
    }

    data = requests.get(f"https://pd.{region}.a.pvp.net/store/v1/offers/", headers=headers)

    offers_data = data.json()

    skin_counter = 0

    for skin in single_skins:
        for row in weapon_fetch["data"]:
            if skin == row["uuid"]:
                if skin_counter == 0:
                    skin1_name = row['displayName']
                    skin1_image = row['displayIcon']
                    skin1_price = priceconvert(skin, offers_data)
                elif skin_counter == 1:
                    skin2_name = row['displayName']
                    skin2_image = row['displayIcon']
                    skin2_price = priceconvert(skin, offers_data)
                elif skin_counter == 2:
                    skin3_name = row['displayName']
                    skin3_image = row['displayIcon']
                    skin3_price = priceconvert(skin, offers_data)
                elif skin_counter == 3:
                    skin4_name = row['displayName']
                    skin4_image = row['displayIcon']
                    skin4_price = priceconvert(skin, offers_data)
                skin_counter += 1
    
    skins_list = {
        "skin1_name": skin1_name,
        "skin1_image":skin1_image,
        "skin1_price":skin1_price,
        "skin2_name": skin2_name,
        "skin2_image":skin2_image,
        "skin2_price": skin2_price,
        "skin3_name": skin3_name,
        "skin3_image":skin3_image,
        "skin3_price": skin3_price,
        "skin4_name": skin4_name,
        "skin4_image":skin4_image,
        "skin4_price": skin4_price,
    }

    return skins_list

def check_item_shop(region, username, password):
    user_data = username_to_data(username, password)
    access_token = user_data[0]
    entitlements_token = user_data[1]
    user_id = user_data[2]
    skin_data = skins(region,entitlements_token, access_token, user_id)
    skin_list = [skin_data["skin1_name"], skin_data["skin1_image"], skin_data["skin1_price"], 
                 skin_data["skin2_name"], skin_data["skin2_image"], skin_data["skin2_price"],
                 skin_data["skin3_name"], skin_data["skin3_image"], skin_data["skin3_price"],
                 skin_data["skin4_name"], skin_data["skin4_image"], skin_data["skin4_price"],]
    return skin_list

@valorant_plugin.command
@lightbulb.command('valorant', 'Commands related to your VALORANT Account.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def valorant_group(ctx):
    pass

@valorant_group.child
@lightbulb.option('region', 'The region associated to your VALORANT Account. (AP, NA, EU, KR)')
@lightbulb.option('password', 'Your VALORANT Account password. Case-sensitive.')
@lightbulb.option('username', 'Your VALORANT Account username. Case-sensitive.')
@lightbulb.command('store', 'Checks the daily store linked to a VALORANT Account.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def store(ctx: lightbulb.Context) -> None:
    try:
        await ctx.respond('Waiting for response. Please be patient!', flags=hikari.MessageFlag.EPHEMERAL)
        shop = check_item_shop(ctx.options.region, ctx.options.username, ctx.options.password)

        embed_color = [0x000000, 0x000000, 0x000000, 0x000000]
        i = 0
        j = 2
        while(i <= 3):
            if(shop[j] == 875 or shop[j] == 1750):
                embed_color[i] = 0x318DB5
            elif(shop[j] == 1275 or shop[j] == 2550):
                embed_color[i] = 0x469160
            elif(shop[j] == 1775 or shop[j] == 3550):
                embed_color[i] = 0xBF4066
            elif(shop[j] == 2175 or shop[j] == 2675 or shop[j] == 4350 or shop[j] == 5350):
                embed_color[i] = 0xC4662B
            elif(shop[j] == 2475 or shop[j] == 4950):
                embed_color[i] = 0xF3BB41

            i = i + 1
            j = j + 3

        embed0 = (
        hikari.Embed(
            title=f"Here's your store!",
            colour=0x07FE82,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
        .add_field(
            shop[0],
            f'{shop[2]} VP'
        )
        .add_field(
            shop[3],
            f'{shop[5]} VP'
        )
        .add_field(
            shop[6],
            f'{shop[8]} VP'
        )
        .add_field(
            shop[9],
            f'{shop[11]} VP'
        )
        ) 

        embed1 = (
        hikari.Embed(
            title=shop[0],
            description=f'{shop[2]} VP',
            colour=embed_color[0],
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
        .set_image(
            shop[1]
        )
        ) 

        embed2 = (
        hikari.Embed(
            title=shop[3],
            description=f'{shop[5]} VP',
            colour=embed_color[1],
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
        .set_image(
            shop[4]
        )
        )

        embed3 = (
        hikari.Embed(
            title=shop[6],
            description=f'{shop[8]} VP',
            colour=embed_color[2],
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
        .set_image(
            shop[7]
        )
        )

        embed4 = (
        hikari.Embed(
            title=shop[9],
            description=f'{shop[11]} VP',
            colour=embed_color[3],
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url or ctx.member.default_avatar_url,
        )
        .set_image(
            shop[10]
        )
        )

        pages = [embed0, embed1, embed2, embed3, embed4]

        navigator = nav.ButtonNavigator(pages, timeout=None)
        await navigator.run(ctx)

    except(KeyError):
        await ctx.respond('Your login credentials are invalid! Check your username, password, and region, and then try again. Remember, username and password are case-specific!',
        flags=hikari.MessageFlag.EPHEMERAL)

@valorant_group.child
@lightbulb.option('username', 'The VALORANT name you wish to check (Name#12345).')
@lightbulb.command('info', 'Shows account level and current act rank of a player. Not yet implemented.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def info(ctx: lightbulb.Context) -> None:
    await ctx.respond('Account linked successfully!... not. This command has yet to be written.', flags=hikari.MessageFlag.EPHEMERAL)

def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(valorant_plugin)
