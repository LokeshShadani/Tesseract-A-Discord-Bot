import discord
from discord.ext import commands
from discord import app_commands
import datetime

class Utility(commands.Cog):
    """
    A collection of utility and informational commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Ping Command ---
    @app_commands.command(name="ping", description="Checks the bot's current latency.")
    async def ping(self, interaction: discord.Interaction):
        # Calculate latency in milliseconds and use the bot's internal latency attribute
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(
            f"🏓 **Pong!** Bot Latency: `{latency_ms}ms`", 
            ephemeral=True
        )

    # --- User Info Command ---
    @app_commands.command(name="userinfo", description="Shows detailed information about a user.")
    @app_commands.describe(user="The user to get info about (defaults to you)")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        # If no user is specified, default to the command invoker
        user = user or interaction.user
        
        # Format dates for better readability
        created_at_str = discord.utils.format_dt(user.created_at, style='F') # Full date/time
        joined_at_str = discord.utils.format_dt(user.joined_at, style='F') if user.joined_at else "N/A"

        embed = discord.Embed(
            title=f"User Info: {user.display_name}", 
            color=user.color if user.color != discord.Color.default() else discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(name="Account Creation", value=created_at_str, inline=False)
        embed.add_field(name="Joined Server", value=joined_at_str, inline=False)
        embed.add_field(name="Roles", value=len(user.roles) - 1, inline=True) # Subtract @everyone
        embed.add_field(name="Status", value=str(user.status).title(), inline=True)
        embed.add_field(name="Bot?", value="Yes" if user.bot else "No", inline=True)
        embed.set_footer(text=f"ID: {user.id}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Server Info Command ---
    @app_commands.command(name="serverinfo", description="Shows detailed information about the server.")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Format creation date
        created_at_str = discord.utils.format_dt(guild.created_at, style='F')

        embed = discord.Embed(
            title=f"Server Info: {guild.name}", 
            color=discord.Color.blurple()
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        # First row of fields
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Server ID", value=guild.id, inline=True)
        embed.add_field(name="Created On", value=created_at_str, inline=True)
        
        # Second row of fields
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=f"Text: {len(guild.text_channels)}\nVoice: {len(guild.voice_channels)}", inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Avatar Command ---
    @app_commands.command(name="avatar", description="Displays a user's full-size avatar.")
    @app_commands.describe(user="The user to show the avatar of (defaults to you)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user
        
        embed = discord.Embed(
            title=f"{user.display_name}'s Avatar",
            color=user.color if user.color != discord.Color.default() else discord.Color.blue()
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        # Add a link to the image
        await interaction.response.send_message(
            embed=embed, 
            ephemeral=True
        )

    # --- Bot Info Command ---
    @app_commands.command(name="botinfo", description="Shows information and statistics about the bot.")
    async def botinfo(self, interaction: discord.Interaction):
        total_members = sum(g.member_count for g in self.bot.guilds)
        
        embed = discord.Embed(title=f"🤖 Bot Info: {self.bot.user.name}", color=discord.Color.green())
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Statistics
        embed.add_field(name="Latency", value=f"**{round(self.bot.latency * 1000)}ms**", inline=True)
        embed.add_field(name="Servers", value=f"**{len(self.bot.guilds)}**", inline=True)
        embed.add_field(name="Total Users", value=f"**{total_members}**", inline=True)
        
        # Developer/Uptime
        embed.add_field(name="Discord.py Version", value=f"v{discord.__version__}", inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Invite Command ---
    @app_commands.command(name="invite", description="Generates a link to invite the bot to your server.")
    async def invite(self, interaction: discord.Interaction):
        # This creates a generic invite link with permissions you grant the bot
        # NOTE: Replace the placeholder below with your actual invite link if you use one with specific permissions/scopes.
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(administrator=True), # Example: request administrator
            scopes=("bot", "applications.commands")
        )
        
        await interaction.response.send_message(
            f"🔗 [**Click here to invite the bot!**]({invite_url})", 
            ephemeral=True
        )

# --- Cog Setup Function ---
async def setup(bot: commands.Bot):
    """Adds the Utility cog to the bot."""
    await bot.add_cog(Utility(bot))