import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Moderation(commands.Cog):
    """
    A collection of server moderation commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Dictionary to store warnings: {guild_id: {user_id: [warning_reason_1, warning_reason_2, ...]}}
        # Note: For production, this should use a database (e.g., SQLite, PostgreSQL).
        self.warnings = {}

    # --- Error Handling ---
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Custom handler for errors occurring in slash commands within this cog."""
        if isinstance(error, app_commands.MissingPermissions):
            # Format the required permissions nicely
            perms = ', '.join([p.replace('_', ' ').title() for p in error.missing_permissions])
            await interaction.response.send_message(
                f"❌ You lack the required permissions to use this command: **{perms}**.",
                ephemeral=True
            )
        else:
            # For all other unhandled errors
            await interaction.response.send_message(
                f"❌ An unhandled error occurred: `{error}`",
                ephemeral=True
            )
            print(f"Unhandled error in Moderation Cog: {error}") # Log error to console


    # --- Kick Command ---
    @app_commands.command(name="kick", description="Kick a member from the server.")
    @app_commands.describe(member="The member to kick", reason="The reason for the kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason specified"):
        if member == interaction.user:
            return await interaction.response.send_message("❌ You can't kick yourself!", ephemeral=True)
        if member.top_role >= interaction.user.top_role and interaction.guild.owner_id != interaction.user.id:
            return await interaction.response.send_message("❌ You cannot kick a member with an equal or higher role.", ephemeral=True)

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                description=f"✅ Kicked {member.mention}", 
                color=discord.Color.red()
            )
            embed.set_author(name="Member Kicked", icon_url=member.display_avatar.url)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ I do not have permission to kick {member.mention}.", ephemeral=True)


    # --- Ban Command ---
    @app_commands.command(name="ban", description="Ban a member from the server.")
    @app_commands.describe(member="The member to ban", reason="The reason for the ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason specified"):
        if member == interaction.user:
            return await interaction.response.send_message("❌ You can't ban yourself!", ephemeral=True)
        
        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                description=f"✅ Banned {member.mention}", 
                color=discord.Color.dark_red()
            )
            embed.set_author(name="Member Banned", icon_url=member.display_avatar.url)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ I do not have permission to ban {member.mention}.", ephemeral=True)


    # --- Unban Command ---
    @app_commands.command(name="unban", description="Unban a user by ID or Name#Discriminator.")
    @app_commands.describe(user_identifier="User ID or Username#Discriminator of the user to unban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_identifier: str):
        await interaction.response.defer(ephemeral=True) # Defer as fetching bans can take time

        banned_users = await interaction.guild.bans()
        user_to_unban = None

        # Try to find by User ID
        try:
            user_id = int(user_identifier)
            for ban_entry in banned_users:
                if ban_entry.user.id == user_id:
                    user_to_unban = ban_entry.user
                    break
        except ValueError:
            # Not a number, try to find by Name#Discriminator
            for ban_entry in banned_users:
                if str(ban_entry.user) == user_identifier:
                    user_to_unban = ban_entry.user
                    break
        
        if user_to_unban:
            try:
                await interaction.guild.unban(user_to_unban)
                await interaction.followup.send(f"✅ User **{str(user_to_unban)}** unbanned.")
            except discord.Forbidden:
                await interaction.followup.send("❌ I do not have permission to unban users.")
            except Exception as e:
                await interaction.followup.send(f"❌ An error occurred during unban: `{e}`")
        else:
            await interaction.followup.send(f"❌ User identifier **`{user_identifier}`** not found in the ban list.")


    # --- Mute Command (Timeout) ---
    @app_commands.command(name="mute", description="Mute a member for a certain duration (uses Discord Timeout).")
    @app_commands.describe(
        member="Member to mute", 
        duration_minutes="Duration in minutes", 
        reason="Reason for mute"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration_minutes: int, reason: str = "No reason specified"):
        if duration_minutes <= 0:
            return await interaction.response.send_message("❌ Duration must be a positive number of minutes.", ephemeral=True)
        if duration_minutes > 40320: # 28 days is the max timeout
            return await interaction.response.send_message("❌ Maximum mute duration is 28 days (40320 minutes).", ephemeral=True)

        try:
            mute_until = discord.utils.utcnow() + datetime.timedelta(minutes=duration_minutes)
            await member.timeout(mute_until, reason=reason)
            
            embed = discord.Embed(
                description=f"✅ Muted {member.mention}", 
                color=discord.Color.orange()
            )
            embed.set_author(name="Member Muted", icon_url=member.display_avatar.url)
            embed.add_field(name="Duration", value=f"{duration_minutes} minutes", inline=True)
            embed.add_field(name="Reason", value=reason, inline=True)
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ I do not have permission to mute {member.mention}.", ephemeral=True)


    # --- Unmute Command (Remove Timeout) ---
    @app_commands.command(name="unmute", description="Unmute a member (removes Discord Timeout).")
    @app_commands.describe(member="Member to unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        try:
            if not member.timed_out:
                return await interaction.response.send_message(f"❌ {member.mention} is not currently timed out.", ephemeral=True)
                
            await member.timeout(None) # Setting duration to None removes the timeout
            await interaction.response.send_message(f"✅ {member.mention} unmuted.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f"❌ I do not have permission to unmute {member.mention}.", ephemeral=True)


    # --- Clear Command ---
    @app_commands.command(name="clear", description="Bulk delete a number of messages.")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
        # Clear command needs deferral because .purge() can take a little longer
        await interaction.response.defer(ephemeral=True)
        
        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"🧹 Successfully deleted **{len(deleted)}** messages.")
        except discord.Forbidden:
            await interaction.followup.send("❌ I do not have permission to delete messages in this channel.")
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred during clearing: `{e}`")

    
    # --- Warn Command (using in-memory storage) ---
    @app_commands.command(name="warn", description="Issue a warning to a member.")
    @app_commands.describe(member="The member to warn", reason="The reason for the warning")
    @app_commands.checks.has_permissions(kick_members=True) # Usually mods/admins who can kick can warn
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        guild_id = interaction.guild_id
        user_id = member.id
        
        # Initialize dictionary if not present
        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []

        # Add the warning
        self.warnings[guild_id][user_id].append(reason)
        warning_count = len(self.warnings[guild_id][user_id])
        
        # Send confirmation
        await interaction.response.send_message(
            f"⚠️ **{member.display_name}** has been warned for: **{reason}**. "
            f"Total warnings: **{warning_count}**.",
            ephemeral=True
        )
        
        # Optionally DM the warned user
        try:
            await member.send(
                f"You received a warning in **{interaction.guild.name}** for: **{reason}**."
                f" This is your warning number **{warning_count}**."
            )
        except:
            pass # Ignore if DMs are closed


async def setup(bot: commands.Bot):
    """Adds the Moderation cog to the bot."""
    await bot.add_cog(Moderation(bot))