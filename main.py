import os
import dotenv
import hikari
import lightbulb
from keep_alive import keep_alive

dotenv.load_dotenv()

bot = lightbulb.BotApp(os.environ["BOT_TOKEN"],
					   keep_alive(),
                       intents=hikari.Intents.ALL,
                       banner=None,
					   )


@bot.listen(hikari.StartedEvent)
async def startbot(event):
    print('Bot has started!')


@bot.command
@lightbulb.command('ping', 'Returns bot ping (heartbeat command).')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond(f'Pong! Latency: {bot.heartbeat_latency*1000:.2f}ms',
                      flags=hikari.MessageFlag.EPHEMERAL)
    print(f'Bot responds in {bot.heartbeat_latency*1000:.2f}ms.')


@bot.command
@lightbulb.command('about', 'Shows information about the bot.')
@lightbulb.implements(lightbulb.SlashCommand)
async def about(ctx):
    await ctx.respond(
        '''I\'m goosebot! First ideated as a VALORANT store checker, I was first created on 1 March 2022 as a multipurpose Python Discord bot.
    
The dev: https://twitter.com/_duckgoose_
Current Version: v0.1''')


bot.load_extensions_from("./extensions/", must_exist=True)

bot.run()
