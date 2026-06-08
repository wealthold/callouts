import nextcord
from nextcord import Interaction
from nextcord.ui import Modal, TextInput
from nextcord.ext import commands
import asyncio
import os
from datetime import datetime
import pytz

TOKEN = os.environ.get("DISCORD_TOKEN")
CALLOUTS_CHANNEL_NAME = "callouts"
LOGO_URL = "https://cdn.discordapp.com/attachments/1451020864345604138/1513409109167444148/logo_transparent.png"

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents)

class CalloutModal(Modal):
    def __init__(self):
        super().__init__("Wealth Woken Callout")
        self.pair = TextInput(label="Pair", placeholder="e.g. XAUUSD", required=True)
        self.direction = TextInput(label="BUY or SELL", placeholder="BUY or SELL", required=True)
        self.entry = TextInput(label="Entry Price", placeholder="e.g. 2342.50", required=True)
        self.stop_loss = TextInput(label="Stop Loss", placeholder="e.g. 2336.00", required=True)
        self.take_profit = TextInput(label="Take Profit", placeholder="e.g. 2358.00", required=True)
        self.reason = TextInput(label="Reason", placeholder="Brief trade reason...", required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.pair)
        self.add_item(self.direction)
        self.add_item(self.entry)
        self.add_item(self.stop_loss)
        self.add_item(self.take_profit)
        self.add_item(self.reason)

    async def callback(self, interaction: Interaction):
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

        embed = nextcord.Embed(
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
            value="Read the full callout before entering. Enter exactly as posted. Do **not** enter more than **2 minutes** after this post. Monitor this channel closely for updates.",
            inline=False
        )
        embed.set_footer(text=f"Wealth Woken  •  Posted {date_str} at {time_str}")
        embed.set_author(name="WEALTH WOKEN CALLOUTS", icon_url=LOGO_URL)

        channel = nextcord.utils.get(interaction.guild.channels, name=CALLOUTS_CHANNEL_NAME)

        if channel is None:
            await interaction.response.send_message("Callouts channel not found.", ephemeral=True)
            return

        await interaction.response.send_message("Callout posted.", ephemeral=True)
        callout_msg = await channel.send(embed=embed)

        await asyncio.sleep(120)

        expiry_embed = nextcord.Embed(
            title="⛔ CALLOUT WINDOW CLOSED",
            description=f"**{pair_upper} {direction_label}** was posted at **{time_str}**.\nThe 2 minute entry window has passed. **Do not enter this trade.**",
            color=0xFFB800
        )
        expiry_embed.set_footer(text="Wealth Woken  •  Follow rules. Every trade is documented.")
        await channel.send(embed=expiry_embed)


@bot.slash_command(name="callout", description="Post a Wealth Woken trade callout")
async def callout(interaction: Interaction):
    try:
        await interaction.response.send_modal(CalloutModal())
    except Exception as e:
        print(f"Error sending modal: {e}")


@bot.event
async def on_ready():
    print(f"Wealth Woken Callouts Bot is online as {bot.user}")


bot.run(TOKEN)
