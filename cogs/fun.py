import discord
from discord.ext import commands
from discord import app_commands
import random

class Fun(commands.Cog):
    """
    A collection of entertaining and random commands.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --- Joke Command ---
    @app_commands.command(name="joke", description="Tells a random joke to lighten the mood.")
    async def joke(self, interaction: discord.Interaction):
        jokes = [
            "Why did the chicken cross the road? To get to the other side!",
            "I told my computer I needed a break, and it froze.",
            "Why don’t programmers like nature? Too many bugs.",
            "Have you heard the one about the three holes? Well, well, well.",
            "What's orange and sounds like a parrot? A carrot."
        ]
        # Keep this ephemeral, as jokes are typically a response to a user
        await interaction.response.send_message(random.choice(jokes), ephemeral=True)

    # --- Roll Command (Dice) ---
    @app_commands.command(name="roll", description="Rolls a standard six-sided dice.")
    async def roll(self, interaction: discord.Interaction):
        roll = random.randint(1, 6)
        # Keep this ephemeral
        await interaction.response.send_message(f"🎲 You rolled a **{roll}**!", ephemeral=True)

    # --- Meme Command (Public Response) ---
    @app_commands.command(name="meme", description="Posts a funny, random meme.")
    async def meme(self, interaction: discord.Interaction):
        # NOTE: Using a simple list for images is fine, but for production,
        # consider using an API like the 'meme-api' for fresh content.
        memes = [
            "https://i.imgur.com/W3duR07.png", # Drake meme example
            "https://i.imgur.com/2vQtZBb.png", # Distracted boyfriend example
            "https://i.imgur.com/o1t1Q8Q.jpg"  # Cat meme example
        ]
        
        embed = discord.Embed(title="🤣 Random Meme!", color=discord.Color.gold())
        embed.set_image(url=random.choice(memes))
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        
        # Change to PUBLIC response (remove ephemeral=True)
        await interaction.response.send_message(embed=embed)

    # --- Coinflip Command ---
    @app_commands.command(name="coinflip", description="Flips a coin: heads or tails.")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads", "Tails"])
        # Keep this ephemeral
        await interaction.response.send_message(f"🪙 The coin landed on **{result}**!", ephemeral=True)

    # --- 8Ball Command ---
    @app_commands.command(name="8ball", description="Ask the magic 8 ball a question.")
    @app_commands.describe(question="Your yes/no question for the 8 ball")
    async def eightball(self, interaction: discord.Interaction, question: str):
        answers = [
            "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.",
            "You may rely on it.", "As I see it, yes.", "Most likely.", "Outlook good.",
            "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
            "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
            "My sources say no.", "Outlook not so good.", "Very doubtful."
        ]
        
        embed = discord.Embed(title="🎱 The Magic 8-Ball Speaks...", color=0x000000)
        embed.add_field(name="❓ Question", value=question, inline=False)
        embed.add_field(name="✨ Answer", value=random.choice(answers), inline=False)
        
        # Keep this ephemeral
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- Cat Command (Public Response) ---
    @app_commands.command(name="cat", description="Get a picture of a random cute cat.")
    async def cat(self, interaction: discord.Interaction):
        # NOTE: Using a single reliable image URL is better than maintaining a local list.
        # This API link (cataas.com) provides a new image on every request.
        image_url = "https://cataas.com/cat" 
        
        embed = discord.Embed(title="🐱 Here's a cute cat!", color=discord.Color.dark_teal())
        embed.set_image(url=image_url)
        
        # Change to PUBLIC response
        await interaction.response.send_message(embed=embed)

    # --- Dog Command (Public Response) ---
    @app_commands.command(name="dog", description="Get a picture of a random happy dog.")
    async def dog(self, interaction: discord.Interaction):
        # NOTE: Using a single reliable image URL that randomizes on request.
        image_url = "https://random.dog/woof.jpg"
        
        embed = discord.Embed(title="🐶 Woof! A good doggo!", color=discord.Color.dark_gold())
        embed.set_image(url=image_url)
        
        # Change to PUBLIC response
        await interaction.response.send_message(embed=embed)

    # --- Quote Command ---
    @app_commands.command(name="quote", description="Get a random inspirational quote.")
    async def quote(self, interaction: discord.Interaction):
        quotes = [
            "The best way to predict the future is to create it. — Peter Drucker",
            "Do one thing every day that scares you. — Eleanor Roosevelt",
            "Success is not final, failure is not fatal: It is the courage to continue that counts. — Winston Churchill",
            "The only way to do great work is to love what you do. — Steve Jobs",
            "Believe you can and you’re halfway there. — Theodore Roosevelt"
        ]
        
        # Keep this ephemeral
        await interaction.response.send_message(f"💬 **Quote of the Moment:**\n> {random.choice(quotes)}", ephemeral=True)


async def setup(bot: commands.Bot):
    """Adds the Fun cog to the bot."""
    await bot.add_cog(Fun(bot))