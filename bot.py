import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Načítanie tokenu z .env súboru
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Inicializácia bota
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Cesta k súboru s úlohami
TASKS_FILE = "tasks.json"


# Funkcia na načítanie úloh zo súboru
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return {"to_do": [], "doing": [], "done": []}
    with open(TASKS_FILE, "r") as file:
        return json.load(file)


# Funkcia na uloženie úloh do súboru
def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


# Príkaz na pridanie úlohy
@bot.tree.command(name="addtask", description="Add a task with a deadline.")
async def add_task(interaction: discord.Interaction, deadline: str, task: str):
    """
    Pridá novú úlohu do sekcie To-Do.
    Syntax: !addtask DD.MM.YYYY Úloha
    """
    try:
        deadline_date = datetime.strptime(deadline, "%d.%m.%Y")
        tasks = load_tasks()
        tasks["to_do"].append(
            {"task": task, "deadline": deadline_date.strftime("%d.%m.%Y")}
        )
        save_tasks(tasks)
        await interaction.response.send_message(f"✅ Úloha '{task}' pridaná s deadline: {deadline}.")
    except ValueError:
        await interaction.response.send_message("❌ Zadaj správny formát dátumu: DD.MM.YYYY.")


# Príkaz na presun úlohy
@bot.tree.command(name="movetask", description="Move a task.")
async def move_task(interaction: discord.Interaction, task_name: str, new_status: str):
    """
    Presunie úlohu do inej sekcie.
    Syntax: !movetask "Úloha" (to_do, doing, done)
    """
    tasks = load_tasks()
    for section in tasks:
        for task in tasks[section]:
            if task["task"] == task_name:
                tasks[section].remove(task)
                tasks[new_status].append(task)
                save_tasks(tasks)
                await interaction.response.send_message(
                    f"✅ Úloha '{task_name}' presunutá do sekcie {new_status}."
                )
                return
    await interaction.response.send_message(f"❌ Úloha '{task_name}' sa nenašla.")


# Príkaz na zobrazenie úloh
@bot.tree.command(name="listtasks", description="List all tasks.")
async def list_tasks(interaction: discord.Interaction):
    """
    Zobrazí všetky úlohy v jednotlivých sekciách.
    Syntax: !listtasks
    """
    tasks = load_tasks()
    embed = discord.Embed(title="📋 Úlohy", color=0x00FF00)
    for section, section_tasks in tasks.items():
        task_list = (
            "\n".join([f"- {t['task']} (do: {t['deadline']})" for t in section_tasks])
            or "Žiadne úlohy."
        )
        embed.add_field(name=section.upper(), value=task_list, inline=False)
    await interaction.response.send_message(embed=embed)


# Príkaz na vymazanie úlohy
@bot.tree.command(name="removetask", description="Remove a task.")
async def remove_task(interaction: discord.Interaction, task_name: str):
    """
    Vymaže úlohu podľa názvu.
    Syntax: !removetask "Úloha"
    """
    tasks = load_tasks()
    for section in tasks:
        for task in tasks[section]:
            if task["task"] == task_name:
                tasks[section].remove(task)
                save_tasks(tasks)
                await interaction.response.send_message(f"🗑️ Úloha '{task_name}' bola vymazaná.")
                return
    await interaction.response.send_message(f"❌ Úloha '{task_name}' sa nenašla.")

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced successfully!")
    except Exception as e:
        print(f"⚠️ Failed to sync slash commands: {e}")

# Spustenie bota
bot.run(TOKEN)
