import discord
from discord import app_commands
from discord.ui import Modal, TextInput
import asyncio
import os
from datetime import datetime
import pytz

TOKEN = os.environ.get("DISCORD_TOKEN")
CALLOUTS_CHANNEL_NAME = "callouts"
LOGO_URL = "https://cdn.discordapp.com/attachments/1451020864345604138/1513409109167444148/logo_transparent.png"
GOLD_COLOR = 0xFFB800

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class CalloutModal(Modal, title="Wealth Woken Callout"):
    pair = TextInput(label="Pair", placeholder="e.g. XAUUSD", required=True)
    direction = TextInput(label="BUY or SELL", placeholder="BUY or SELL", required=True)
    entry = TextInput(label="Entry Price", placeholder="e.g. 2342.50", required=True)
    stop_loss = TextInput(label="Stop Loss", placeholder="e.g. 2336.00", required=True)
    take_profit = TextInput(label="Take Profit", placeholder="e.g. 2358.00", required=True)
    reason = TextInput(label="Reason", placeholder="Brief trade reason...", required=True, style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        direction_upper = self.direction.value.strip().upper()
        pair_upper = self.pair.value.strip().upper()

        if direction_upper == "BUY":
            direction_color = 0x00C853
            direction_label = "🟢 BUY"
        else:
            direction_color = 0xFF1744
            direction_label = "🔴 SELL"

        est = pytz.timezone("US/Eastern")
        now = datetime.now(est)
        time_str = now.strftime("%I:%M %p EST")
        date_str = now.strftime("%B %d, %Y")

        embed = discord.Embed(
            title=f"{pair_upper}  |  {direction_label}",
            color=direction_color
        )

        embed.set_thumbnail(url=LOGO_URL)

        embed.add_field(name="💰 ENTRY", value=f"`{self.entry.value.strip()}`", inline=True)
        embed.add_field(name="🛑 STOP LOSS", value=f"`{self.stop_loss.value.strip()}`", inline=True)
        embed.add_field(name="🎯 TAKE PROFIT", value=f"`{self.take_profit.value.strip()}`", inline=True)
        embed.add_field(name="📋 REASON", value=self.reason.value.strip(), inline=False)
        embed.add_field(
            name="⚠️ EXECUTION RULES",
            value="Read the full callout before entering. Enter the trade exactly as posted. Do **not** enter more than **2 minutes** after this post. Monitor this channel closely for updates.",
            inline=False
        )

        embed.set_footer(text=f"Wealth Woken  •  Posted {date_str} at {time_str}")
        embed.set_author(name="WEALTH WOKEN CALLOUTS", icon_url=LOGO_URL)

        channel = discord.utils.get(interaction.guild.text_channels, name=CALLOUTS_CHANNEL_NAME)

        if channel is None:
            await interaction.response.send_message("Callouts channel not found. Make sure it is named 'callouts'.", ephemeral=True)
            return

        await interaction.response.send_message("Callout posted.", ephemeral=True)
        callout_msg = await channel.send(embed=embed)

        await asyncio.sleep(120)

        expiry_embed = discord.Embed(
            title="⛔ CALLOUT WINDOW CLOSED",
            description=f"**{pair_upper} {direction_label}** was posted at **{time_str}**.\nThe 2 minute entry window has passed. **Do not enter this trade.**",
            color=0xFFB800
        )
        expiry_embed.set_footer(text="Wealth Woken  •  Follow rules. Every trade is documented.")
        await channel.send(embed=expiry_embed)


class WealthWokenBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Wealth Woken Callouts Bot is online as {self.user}")


bot = WealthWokenBot()

@bot.tree.command(name="callout", description="Post a Wealth Woken trade callout")
async def callout(interaction: discord.Interaction):
    await interaction.response.send_modal(CalloutModal())


bot.run(TOKEN)
