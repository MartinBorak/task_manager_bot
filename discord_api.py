from discord import Embed, HTTPException, Interaction, Member, NotFound

from models import Task


async def send(
    interaction: Interaction,
    message: str | None = None,
    embed: Embed | None = None,
    ephemeral: bool = False,
) -> None:
    await interaction.response.send_message(
        content=message,
        embed=embed,
        ephemeral=ephemeral,
    )


async def get_member(interaction: Interaction, task: Task) -> Member | None:
    member_id = task.member
    member = interaction.guild.get_member(member_id)

    if not member:
        try:
            member = await interaction.guild.fetch_member(member_id)
        except NotFound:
            await send(interaction, "Member not found.", ephemeral=True)
        except HTTPException:
            await send(interaction, "Failed to fetch the member.", ephemeral=True)

    return member


async def get_member_name(interaction: Interaction, task: Task) -> str:
    member = await get_member(interaction, task)
    return member.display_name if member else "?"
