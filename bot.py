import os
from datetime import datetime

from discord import Embed, Intents, Interaction, Member
from discord.ext import commands
from dotenv import load_dotenv
from google.cloud.exceptions import NotFound

from db_api import (
    db_add_document,
    db_delete_document,
    db_update_document,
    get_all_tasks,
    get_task,
)
from discord_api import get_member_name, send
from enums import TaskStatus
from models import Task

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)


@bot.tree.command(name="addtask", description="Add a task with a deadline.")
async def add_task(
    interaction: Interaction,
    deadline: str,
    member: Member,
    task_name: str,
) -> None:
    try:
        deadline_date = datetime.strptime(deadline, "%d.%m.%Y")
        _deadline = deadline_date.strftime("%d.%m.%Y")
    except ValueError:
        await send(
            interaction,
            "❌ Enter a valid date: d.m.yyyy.",
        )
        return

    task = Task(
        name=task_name,
        deadline=_deadline,
        member=member.id,
        status=TaskStatus.TO_DO,
    )

    await db_add_document(
        document_id=task_name,
        data=task.to_dict(),
    )

    await send(
        interaction,
        f"✅ Task '{task_name}' added for {member.mention} with a deadline: {deadline}.",
    )


@bot.tree.command(name="movetask", description="Move a task.")
async def move_task(interaction: Interaction, task_name: str, new_status: str) -> None:
    status = TaskStatus.from_string(new_status)

    if not status:
        await send(
            interaction,
            f"✅ '{new_status}' is not a valid status.",
        )
        return

    try:
        await db_update_document(
            document_id=task_name,
            update_data={
                "status": TaskStatus.from_string(new_status),
            },
        )
    except NotFound:
        await send(
            interaction,
            f"❌ Task '{task_name}' not found.",
        )
        return

    task = get_task(task_name)
    member_name = await get_member_name(interaction, task)

    await send(
        interaction,
        f"✅ Task '{task_name}' ({member_name}) moved to status '{new_status}'.",
    )


@bot.tree.command(name="listtasks", description="List all tasks.")
async def list_tasks(interaction: Interaction) -> None:
    tasks = get_all_tasks()
    embed = Embed(title="📋 Tasks", color=0x00FF00)

    for status in TaskStatus.all():
        task_list_str = (
            "\n".join(
                [
                    f"- {await get_member_name(interaction, task)}: '{task.name}' (until {task.deadline})"
                    for task in tasks
                    if task.status == status
                ]
            )
            or "No tasks."
        )
        embed.add_field(name=status.to_string(), value=task_list_str, inline=False)

    await send(interaction, embed=embed)


@bot.tree.command(name="removetask", description="Remove a task.")
async def remove_task(interaction: Interaction, task_name: str) -> None:
    task = get_task(task_name)

    if not task:
        await send(
            interaction,
            f"❌ Task '{task_name}' not found.",
        )
        return

    await db_delete_document(task_name)

    await send(
        interaction,
        f"🗑️ Task '{task_name}' ({await get_member_name(interaction, task)}) was removed.",
    )


@bot.event
async def on_ready() -> None:
    try:
        await bot.tree.sync()
        print("✅ Slash commands synced successfully!")
    except Exception as e:
        print(f"⚠️ Failed to sync slash commands: {e}")


bot.run(TOKEN)
