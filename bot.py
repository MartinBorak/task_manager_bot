import json
import os
from datetime import datetime

from discord import Embed, Intents, Interaction, Member
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

TASKS_FILE = "tasks.json"


def load_tasks() -> dict:
    if not os.path.exists(TASKS_FILE):
        return {"to_do": [], "doing": [], "done": []}
    with open(TASKS_FILE, "r") as file:
        return json.load(file)


def save_tasks(tasks: dict) -> None:
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def get_member_name(interaction: Interaction, task: dict) -> str:
    return interaction.guild.get_member(task["member"]).name


async def send(
    interaction: Interaction, message: str | None = None, embed: Embed | None = None
) -> None:
    await interaction.response.send_message(content=message, embed=embed)


@bot.tree.command(name="addtask", description="Add a task with a deadline.")
async def add_task(
    interaction: Interaction, deadline: str, member: Member, task: str
) -> None:
    """
    Pridá novú úlohu do sekcie To-Do.
    Syntax: !addtask DD.MM.YYYY Úloha
    """
    try:
        deadline_date = datetime.strptime(deadline, "%d.%m.%Y")
        tasks = load_tasks()
        tasks["to_do"].append(
            {
                "task": task,
                "deadline": deadline_date.strftime("%d.%m.%Y"),
                "member": member.id,
            }
        )
        save_tasks(tasks)
        await send(
            interaction,
            f"✅ Úloha '{task}' pridaná pre {member.mention} s deadline: {deadline}.",
        )
    except ValueError:
        await send(
            interaction,
            "❌ Zadaj správny formát dátumu: DD.MM.YYYY.",
        )


@bot.tree.command(name="movetask", description="Move a task.")
async def move_task(interaction: Interaction, task_name: str, new_status: str) -> None:
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
                await send(
                    interaction,
                    f"✅ Úloha '{task_name}' ({get_member_name(interaction, task)}) presunutá do sekcie {new_status}.",
                )
                return
    await send(
        interaction,
        f"❌ Úloha '{task_name}' sa nenašla.",
    )


@bot.tree.command(name="listtasks", description="List all tasks.")
async def list_tasks(interaction: Interaction) -> None:
    """
    Zobrazí všetky úlohy v jednotlivých sekciách.
    Syntax: !listtasks
    """
    tasks = load_tasks()
    embed = Embed(title="📋 Úlohy", color=0x00FF00)
    for section, section_tasks in tasks.items():
        task_list = (
            "\n".join(
                [
                    f"- {get_member_name(interaction, task)}: {task['task']} (do {task['deadline']})"
                    for task in section_tasks
                ]
            )
            or "Žiadne úlohy."
        )
        embed.add_field(name=section.upper(), value=task_list, inline=False)
    await send(interaction, embed=embed)


@bot.tree.command(name="removetask", description="Remove a task.")
async def remove_task(interaction: Interaction, task_name: str) -> None:
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
                await send(
                    interaction,
                    f"🗑️ Úloha '{task_name}' ({get_member_name(interaction, task)}) bola vymazaná.",
                )
                return
    await send(
        interaction,
        f"❌ Úloha '{task_name}' sa nenašla.",
    )


@bot.event
async def on_ready() -> None:
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced successfully!")
    except Exception as e:
        print(f"⚠️ Failed to sync slash commands: {e}")


bot.run(TOKEN)
