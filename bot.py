import discord
import os 
from discord.ext import commands
from discord import app_commands
from typing import Optional
from keep_alive import keep_alive

intents = discord.Intents.default()
intents.members = True  # Mitglieder-Intents aktivieren
bot = commands.Bot(command_prefix="!", intents=intents)

points = {}  # Punkte speichern: {user_id: punkte}

class PointsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add", description="➕ [MOD] add points from multiple users")
    async def add(
        self,
        interaction: discord.Interaction,
        amount: int,
        user1: discord.Member,
        user2: Optional[discord.Member] = None,
        user3: Optional[discord.Member] = None,
        user4: Optional[discord.Member] = None,
        user5: Optional[discord.Member] = None
    ):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return

        users = [user1, user2, user3, user4, user5]
        added_users = []

        for user in users:
            if user:
                points[user.id] = points.get(user.id, 0) + amount
                added_users.append(user.mention)

        if added_users:
            # Öffentlich sichtbar (ephemeral entfernt)
            await interaction.response.send_message(
                f"{', '.join(added_users)} were **{amount} points** added each person."
            )
        else:
            await interaction.response.send_message("❌ No valid users specified.", ephemeral=True)

    @app_commands.command(name="remove", description="➖ [MOD] remove points from multiple users")
    async def remove(
        self,
        interaction: discord.Interaction,
        amount: int,
        user1: discord.Member,
        user2: Optional[discord.Member] = None,
        user3: Optional[discord.Member] = None,
        user4: Optional[discord.Member] = None,
        user5: Optional[discord.Member] = None
    ):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ No permission.", ephemeral=True)
            return
        
        users = [user1, user2, user3, user4, user5]
        removed_users = []

        for user in users:
            if user:
                current = points.get(user.id, 0)
                points[user.id] = max(0, current - amount)
                removed_users.append(user.mention)

        if removed_users:
            await interaction.response.send_message(
                f"{', '.join(removed_users)} were **{amount} points** removed each user."
            )
        else:
            await interaction.response.send_message("❌ No valid users specified.", ephemeral=True)

    @app_commands.command(name="clear", description="🗑️ [ADMIN] delete points from an user")
    async def clear(self, interaction: discord.Interaction, user: discord.Member):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ only admins are allowed to do this.", ephemeral=True)
            return
        points[user.id] = 0
        await interaction.response.send_message(f"points from {user.mention} got reseted.")

    @app_commands.command(name="reset_leaderboard", description="⚠️ [ADMIN] delete entire leaderboard")
    async def reset_leaderboard(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ only admins are allowed to do this.", ephemeral=True)
            return
        points.clear()
        await interaction.response.send_message("The entire Points-leaderboard got reseted.")

    @app_commands.command(name="leaderboard", description="📈 Shows the points leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        if not points:
            await interaction.response.send_message("No points awarded yet.")
            return
        sorted_users = sorted(points.items(), key=lambda x: x[1], reverse=True)
        msg = "**🏆 Points leaderboard:**\n"
        for i, (uid, pts) in enumerate(sorted_users[:10], start=1):
            user = interaction.guild.get_member(uid)
            name = user.display_name if user else f"Unknown ({uid})"
            msg += f"{i}. {name}: {pts} points\n"
        await interaction.response.send_message(msg)  # öffentlich sichtbar

    @app_commands.command(name="check", description="👤 Show your own points")
    async def check(self, interaction: discord.Interaction):
        pts = points.get(interaction.user.id, 0)
        # Private Nachricht an den Nutzer
        await interaction.response.send_message(f"you own **{pts} points**.", ephemeral=True)

    @app_commands.command(name="help", description="❓ show help")
    async def help(self, interaction: discord.Interaction):
        msg = (
            "**📊 bot-comamands:**\n"
            "➕ `/add @user1 @user2 ... amount` – Add points [MOD]\n"
            "➖ `/remove @user1 @user2 ... amount` – Remove points [MOD]\n"
            "🗑️ `/clear @user` – Reset points [ADMIN]\n"
            "🔁 `/reset_leaderboard` – Reset points from everyone [ADMIN]\n"
            "📈 `/leaderboard` – Show rank\n"
            "👤 `/check` – Show your own points\n"
            "❓ `/help` – Show this help message"
        )
        await interaction.response.send_message(msg, ephemeral=True)

GUILD_ID = 1332041966686568601

@bot.event
async def on_ready():
    print(f"✅ Bot ist online als {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    try:
        await bot.add_cog(PointsCog(bot))
        await bot.tree.sync(guild=guild)  # Slash-Commands nur für deinen Server synchronisieren
        print("Slash Commands für den Server synchronisiert!")
    except Exception as e:
        print(f"Fehler beim Synchronisieren: {e}")

keep_alive()  # Mini-Webserver starten
bot.run(os.getenv("DISCORD_TOKEN"))
