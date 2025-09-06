import os
import time
import json
import asyncio
import threading
from dotenv import load_dotenv
import discord
from discord.ext import commands
import schedule
from utils.scrap import request_site, listAll

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

key = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix='+', intents=intents, help_command=None)

with open("users/users.json", "r", encoding="utf-8") as f:
    usuarios = list(json.load(f).keys())


@bot.event
async def on_ready():
    print("Bot online!")


@bot.command(name="ajuda", aliases=["help", "comandos"])
async def ajuda(ctx, destino: str = None):
    """
    +ajuda               -> envia a lista de comandos no canal atual
    +ajuda dm            -> envia a lista de comandos por DM para o autor
    +ajuda privado       -> idem 'dm'
    """
    comandos = [
        ("editais", "Busca e lista os editais/bolsas/intercâmbios encontrados."),
        ("inscrever", "Inscreve você para receber notificações sobre novos editais de intercâmbios."),
        ("desinscrever", "Cancela sua inscrição para notificações sobre novos editais de intercâmbios."),
        ("ajuda", "Mostra essa mensagem de ajuda. Use `+ajuda dm` para receber por DM."),
    ]

    embed = discord.Embed(
        title="🔎 Ajuda — Comandos do Bot",
        description="Lista de comandos disponíveis e seu objetivo. Use o prefixo `+` antes do comando.",
        color=discord.Color.blurple()
    )
    for nome, descricao in comandos:
        embed.add_field(name=f"+{nome}", value=descricao, inline=False)

    embed.set_footer(text="Se quiser que eu envie por DM, use: +ajuda dm")

    if destino and destino.lower() in ("dm", "privado", "pm"):
        try:
            await ctx.author.send(embed=embed)
            await ctx.send(f"{ctx.author.mention}, enviei a lista de comandos por DM ✅")
        except Exception as e:
            await ctx.send(f"Não consegui enviar DM para {ctx.author.mention}. Verifique suas configurações de privacidade ou consulte a lista aqui.")
            print(f"Erro ao enviar ajuda por DM: {e}")
    else:
        await ctx.send(embed=embed)


@bot.command("editais", aliases=["edital", "intercambios"])
async def editais(ctx):
    editais = listAll()

    message = "**Olá senhor!**"

    if len(editais) > 0:
        message += "\n\nHá alguns editais em aberto neste momento! Aqui vai a busca de nossa última atualização."

        for item in editais:
            message += f"\n\n**Intercâmbio:** {item.get('name')}\n**Link:** {item.get('link')}."
        else:
            message += "\n\nCaso queira acessar o portal diretamente, segue a **lista de editais:** https://inatel.br/intercambios/editais/lista-editais"
    else:
        message = "\n\nNão há editais abertos no momento!"
    
    await ctx.send(message)


@bot.command("inscricao", aliases=["inscrever", "inscrição"])
async def subscribe(ctx):
    message = "**Você acabou de ser inscrito e será notificado sobre os novos editais assim que abrirem!**"

    user = str(ctx.author.id)

    with open("users/users.json", "r+", encoding="utf-8") as file:
        inscriptions = json.load(file)
        if user not in inscriptions or inscriptions[user] == 0:
            inscriptions[user] = 1
            json.dump(inscriptions, file, ensure_ascii=False, indent=4)
        else:
            message = "**Você já está inscrito e já recebe notificações sobre novos editais!**"
        
    await ctx.send(message)


@bot.command("desinscrever", aliases=["cancelar_inscricao", "unsubscribe"])
async def unsubscribe(ctx):
    message = "**Você acabou de se desinscrever e não será mais notificado sobre novos editais.**"

    user = str(ctx.author.id)

    with open("users/users.json", "r+", encoding="utf-8") as file:
        inscriptions = json.load(file)
        if inscriptions[user] == 1:
            inscriptions[user] = 0
            json.dump(inscriptions, file, ensure_ascii=False, indent=4)
        else:
            message = "**Você não está inscrito e não recebe notificações sobre novos editais!**"
        
    await ctx.send(message)
    

async def enviar_msg(user_id: int, msg: str):
    try:
        user = await bot.fetch_user(user_id)
        await user.send(msg)
    except Exception as e:
        print(f"Erro ao enviar mensagem para {user_id}: {e}")


def run_schedule():
    schedule.every().day.at("12:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)


def job():
    try:
        result = request_site()

        if isinstance(result, dict):
            code = result.get("code")

            if code == 1:
                message = f"*Olá, senhor! Espero que esteja bem.*\n\nUm novo edital de intercâmbio foi aberto a menos de 24 horas!\n\n**Intercâmbio:** {result.get('data')[0].get('name')}\n**Link:** {result.get('data')[0].get('link')}.\n\n**Lista de editais:** https://inatel.br/intercambios/editais/lista-editais"
                for uid in usuarios:
                    bot.loop.create_task(enviar_msg(uid, message))
            
            elif code == 0:
                print("Tudo igual")
            
            elif code == -1:
                bot.loop.create_task(enviar_msg(usuarios[0], "Ocorreu um erro na execução!"))
    except Exception as e:
        print(f"Erro no job: {e}")


threading.Thread(target=run_schedule, daemon=True).start()

bot.run(key)