import os
import asyncio
import pytz
from datetime import datetime
import nextcord
from nextcord import Interaction
from nextcord.ui import Modal, TextInput
from nextcord.ext import commands

TOKEN = os.environ.get("DISCORD_TOKEN")
CALLOUTS_CHANNEL_NAME = "call-outs"
LOGO_URL = "https://cdn.discordapp.com/attachments/1451020864345604138/1513409109167444148/logo_transparent.png"

intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(intents=intents)

class CalloutModal(Modal):
    def __init__(self):
        super().__init__("Wealth Woken Callout", timeout=300)
        self.pair = TextInput(label="Pair", placeholder="e.g. XAUUSD", required=True, max_length=20)
        self.direction = TextInput(label="BUY or SELL", placeholder="BUY or SELL", required=True, max_length=10)
        self.entry = TextInput(label="Entry Price", placeholder="e.g. 2342.50", required=True, max_length=20)
        self.stop_loss = TextInput(label="Stop Loss", placeholder="e.g. 2336.00", required=True, max_length=20)
        self.take_profit = TextInput(label="Take Profit", placeholder="e.g. 2358.00", required=True, max_length=20)
        
        self.add_item(self.pair)
        self.add_item(self.direction)
        self.add_item(self.entry)
        self.add_item(self.stop_loss)
        self.add_item(self.take_profit)
        

    async def callback(self, interaction: Interaction):
        await interaction.response.defer(ephemeral=True)
        
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

        embed = nextcord.Embed(title=f"{pair_upper}  |  {direction_label}", color=direction_color)
        embed.set_thumbnail(url=LOGO_URL)
        embed.add_field(name="💰 ENTRY", value=f"`{self.entry.value.strip()}`", inline=True)
        embed.add_field(name="🛑 STOP LOSS", value=f"`{self.stop_loss.value.strip()}`", inline=True)
        embed.add_field(name="🎯 TAKE PROFIT", value=f"`{self.take_profit.value.strip()}`", inline=True)
        
        embed.add_field(name="⚠️ EXECUTION RULES", value="Read the full callout before entering. Enter exactly as posted. Do **not** enter more than **2 minutes** after this post. Monitor this channel closely for updates.", inline=False)
        embed.set_footer(text=f"Wealth Woken  •  Posted {date_str} at {time_str}")
        embed.set_author(name="WEALTH WOKEN CALLOUTS", icon_url=LOGO_URL)

        channel = nextcord.utils.get(interaction.guild.channels, name=CALLOUTS_CHANNEL_NAME)

        if channel is None:
            await interaction.followup.send("Callouts channel not found.", ephemeral=True)
            return

        await channel.send(embed=embed)
        await interaction.followup.send("Callout posted.", ephemeral=True)

        await asyncio.sleep(120)

        expiry_embed = nextcord.Embed(
            title="⛔ CALLOUT WINDOW CLOSED",
            description=f"**{pair_upper} {direction_label}** was posted at **{time_str}**.\nThe 2 minute entry window has passed. **Do not enter this trade.**",
            color=0xFFB800
        )
        expiry_embed.set_footer(text="Wealth Woken  •  Follow rules. Every trade is documented.")
        await channel.send(embed=expiry_embed)

class UpdateModal(Modal):
    def __init__(self):
        super().__init__("Wealth Woken Update", timeout=300)

        self.update_title = TextInput(
            label="UPDATE",
            placeholder="e.g. Move Stop Loss to Break Even",
            required=True,
            max_length=80
        )

        self.pair_direction = TextInput(
            label="Pair | BUY/SELL",
            placeholder="e.g. XAUUSD | BUY",
            required=True,
            max_length=30
        )

        self.main_message = TextInput(
            label="Main Update Message",
            placeholder="e.g. Secure partials now and move SL to entry.",
            required=True,
            max_length=300
        )

        self.footer_note = TextInput(
            label="Footer Note",
            placeholder="e.g. Stay disciplined and manage risk.",
            required=False,
            max_length=120
        )

        self.add_item(self.update_title)
        self.add_item(self.pair_direction)
        self.add_item(self.main_message)
        self.add_item(self.footer_note)

    async def callback(self, interaction: Interaction):
        channel = nextcord.utils.get(interaction.guild.text_channels, name=CALLOUTS_CHANNEL_NAME)

        if channel is None:
            await interaction.response.send_message(
                "Could not find the call-outs channel.",
                ephemeral=True
            )
            return

        embed = nextcord.Embed(
            title=self.update_title.value,
            description=self.main_message.value,
            color=0xD4AF37
        )

        embed.add_field(
            name="Pair | BUY/SELL",
            value=self.pair_direction.value,
            inline=False
        )

        if self.footer_note.value:
            embed.set_footer(text=self.footer_note.value)

        embed.set_thumbnail(url=LOGO_URL)

        await channel.send(embed=embed)
        await interaction.response.send_message(
            "Trade update sent successfully.",
            ephemeral=True
        )
@bot.slash_command(name="callout", description="Post a Wealth Woken trade callout")
async def callout(interaction: Interaction):
    await interaction.response.send_modal(CalloutModal())
    @bot.slash_command(name="update", description="Send a trade update")
async def update(interaction: Interaction):
    await interaction.response.send_modal(UpdateModal())

@bot.event
async def on_ready():
    print(f"Wealth Woken Callouts Bot is online as {bot.user}")

bot.run(TOKEN)
