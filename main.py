import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
import os
import random
import asyncio
from dotenv import load_dotenv

# Load environment variables (like the bot token) from a .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # NOTE: Updated to a common env variable name

# 1. Setup Intents
intents = discord.Intents.default()
intents.members = True          # Required for member-related events/data (e.g., getting member_count)
intents.message_content = True  # Required for processing messages (if you use prefix commands or message content)

bot = commands.Bot(command_prefix=".", intents=intents)

# 2. Status Loop
@tasks.loop(seconds=30)
async def change_status():
    """Cycles the bot's status every 30 seconds."""
    # Ensure bot.guilds is ready before accessing it (prevents rare startup errors)
    if not bot.is_ready():
        return

    # Calculate total members to display in one of the statuses
    total_users = sum(g.member_count for g in bot.guilds)

    activities = [
        (discord.ActivityType.watching, "for rule-breakers"),
        (discord.ActivityType.listening, f"to {len(bot.guilds)} servers"),
        (discord.ActivityType.playing, "with the ban hammer"),
        (discord.ActivityType.watching, f"{total_users} users"),
    ]
    activity_type, status_text = random.choice(activities)
    
    await bot.change_presence(
        status=discord.Status.do_not_disturb,
        activity=discord.Activity(type=activity_type, name=status_text)
    )

# 3. Help Menu View (for navigation buttons)
class HelpMenu(ui.View):
    def __init__(self, embeds):
        # Set a short timeout for the buttons
        super().__init__(timeout=120) 
        self.embeds = embeds
        self.current = 0
        self.message = None # To store the message object for on_timeout

    # Store the message object once the view is sent
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: ui.Item) -> None:
        if isinstance(error, discord.errors.NotFound) and "Unknown interaction" in str(error):
            # This handles users clicking a button after the bot restarts or the timeout
            await interaction.followup.send("This button interaction is no longer valid. Please run the `/help` command again.", ephemeral=True)
        else:
            print(f"An error occurred in HelpMenu view: {error}")
            await super().on_error(interaction, error, item)

    async def update_message(self, interaction: discord.Interaction):
        """Edits the message to show the new page/embed."""
        embed = self.embeds[self.current]
        embed.set_footer(text=f"Page {self.current+1}/{len(self.embeds)}")
        # Check if interaction has already been responded to (e.g., from a deferral, though not used here)
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=self)
        else:
            await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label="◀️ Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current = (self.current - 1) % len(self.embeds)
        await self.update_message(interaction)

    @ui.button(label="▶️ Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: ui.Button):
        self.current = (self.current + 1) % len(self.embeds)
        await self.update_message(interaction)
        
    async def on_timeout(self) -> None:
        """Disables buttons when the view times out."""
        if self.message:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)


# 4. Help Command
@bot.tree.command(name="help", description="Shows all available commands.")
async def help_command(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True) # Defer the response immediately

    # Group commands by Cog name
    categories = {}
    for command in bot.tree.walk_commands():
        cog_name = command.cog_name if command.cog_name else "Other"
        # Skip the 'Help' command itself and commands that are hidden (if you use that)
        if command.name == "help":
            continue
        categories.setdefault(cog_name, []).append(command)

    # Create an embed for each category
    embeds = []
    for cog, cmds in categories.items():
        embed = discord.Embed(
            title=f"📘 {cog} Commands",
            description=f"List of available slash commands for {cog}.",
            color=random.randint(0, 0xFFFFFF)
        )
        for cmd in cmds:
            # Build the command string with options for clarity
            cmd_args = [f"<{opt.name}>" for opt in cmd.parameters]
            cmd_string = f"/{cmd.name} {' '.join(cmd_args)}"
            
            # Use the full command string and description
            embed.add_field(name=cmd_string, value=cmd.description or "No description provided.", inline=False)
            
        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embeds.append(embed)

    # Fallback if no commands are found (shouldn't happen with Cogs loaded)
    if not embeds:
        await interaction.followup.send("No commands loaded yet. Please wait for the bot to fully initialize.", ephemeral=True)
        return

    # Send the first embed with the navigational view
    view = HelpMenu(embeds)
    embed = embeds[0]
    embed.set_footer(text="Page 1/" + str(len(embeds)))
    
    # Use followup.send after deferral
    message = await interaction.followup.send(embed=embed, view=view, ephemeral=True)
    view.message = message # Pass the message object to the view for on_timeout


# 5. On Ready Event
@bot.event
async def on_ready():
    """Fires when the bot is ready and logged in."""
    print(f"✅ Logged in as {bot.user}")
    
    # Start the status loop
    if not change_status.is_running():
        change_status.start()
        
    # Sync Slash Commands
    try:
        # Note: You can optionally sync to a specific guild for faster testing:
        # synced = await bot.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))
        synced = await bot.tree.sync() 
        print(f"🔄 Synced {len(synced)} global commands.")
    except Exception as e:
        print(f"⚠ Error syncing commands: {e}")

# 6. Main Function and Cog Loading
async def main():
    """Loads Cogs and starts the bot."""
    # List of extensions (Cogs) to load
    initial_extensions = [
        "cogs.moderation",
        "cogs.utility",
        "cogs.fun"
    ]
    
    for extension in initial_extensions:
        try:
            # The '.' prefix is used here because the cogs will be inside a 'cogs' folder
            await bot.load_extension(extension)
            print(f"✅ Loaded Cog: {extension}")
        except Exception as e:
            print(f"❌ Failed to load Cog: {extension}. Error: {e}")

    # Start the bot
    await bot.start(TOKEN)


if __name__ == "__main__":
    # Ensure you have a '.env' file with DISCORD_BOT_TOKEN="YOUR_TOKEN"
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot shutting down gracefully.")