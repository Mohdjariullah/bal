import discord
from discord.ext import commands
import requests
import asyncio

intents = discord.Intents.default()
intents.reactions = True
intents.message_content = True
# Define your bot instance and other variables
bot = commands.Bot(command_prefix=',', intents=intents)

# Define your color variable
color = 0x000000  # You can replace this with the color you prefer

bot.remove_command('help')


@bot.command(name='help')
async def my_help(ctx):
  embed = discord.Embed(title="Plague Store Bot Help",
                        color=color,
                        description="A bot to check cryptocurrency balances.")

  embed.add_field(name=",ping", value="Check the bot's latency.", inline=False)
  embed.add_field(
      name=",bal",
      value=
      "Check cryptocurrency balance. React with the corresponding emoji to choose the cryptocurrency.",
      inline=False)

  embed.set_footer(text="By Pixlbuilders")
  await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.send(f"Invalid command. Use ,help to see available commands.")
  elif isinstance(error, commands.MissingRequiredArgument):
    await ctx.send(
        f"Missing required arguments. Check the command usage with ,help.")
  elif isinstance(error, commands.BadArgument):
    await ctx.send(
        "Bad argument. Make sure you provided the right type of argument.")
  elif isinstance(error, commands.CheckFailure):
    await ctx.send("You do not have permission to use this command.")
  else:
    print(f"An error occurred: {error}")


@bot.command()
async def bal(ctx):
  # Create the embed with cryptocurrency selection
  embed = discord.Embed(
      title="Select the Cryptocurrency to check the balance",
      color=color,
      description=
      "React with the corresponding emoji to choose the cryptocurrency.")
  embed.add_field(name="Litecoin (LTC)",
                  value="React with <:cryptoLTC:1184891420381822996>",
                  inline=False)
  embed.add_field(name="Bitcoin (BTC)",
                  value="React with <:Bitcoin:1196482389317259355>",
                  inline=False)
  embed.add_field(name="Ethereum (ETH)",
                  value="React with <:eth:1184891485930393710>",
                  inline=False)
  embed.add_field(name="Solana (SOL)",
                  value="React with <:solana:1196482428387209348>",
                  inline=False)
  embed.set_footer(text="By Pixlbuilders")
  # Send the embed message
  msg = await ctx.send(embed=embed)

  # Add reactions to the message
  for emoji in [
      '<:cryptoLTC:1184891420381822996>', '<:Bitcoin:1196482389317259355>',
      '<:eth:1184891485930393710>', '<:solana:1196482428387209348>'
  ]:
    await msg.add_reaction(emoji)

  # Define a check function for wait_for
  def check(reaction, user):
    return user == ctx.author and str(reaction.emoji) in [
        '<:cryptoLTC:1184891420381822996>', '<:Bitcoin:1196482389317259355>',
        '<:eth:1184891485930393710>', '<:solana:1196482428387209348>'
    ]

  # Wait for a reaction
  try:
    reaction, user = await bot.wait_for('reaction_add',
                                        timeout=60.0,
                                        check=check)
  except asyncio.TimeoutError:
    await ctx.send("Timeout. Please try the command again.")
    return

  # Map the chosen emoji to the corresponding cryptocurrency
  crypto_mapping = {
      '<:cryptoLTC:1184891420381822996>': 'ltc',
      '<:Bitcoin:1196482389317259355>': 'btc',
      '<:eth:1184891485930393710>': 'eth',
      '<:solana:1196482428387209348>': 'sol'
  }
  selected_crypto = crypto_mapping.get(str(reaction.emoji))

  # Prompt user for address
  await ctx.send(f"Please enter your {selected_crypto.upper()} address:")
  try:
    address_msg = await bot.wait_for('message',
                                     timeout=60.0,
                                     check=lambda m: m.author == ctx.author)
    address = address_msg.content.strip()
  except asyncio.TimeoutError:
    await ctx.send("Timeout. Please try the command again.")
    return

  # Fetch balance based on the selected cryptocurrency
  if selected_crypto == 'ltc':
    await ltc(ctx, address)
  elif selected_crypto == 'btc':
    await btc(ctx, address)  # Implement btc function similarly to ltc
  elif selected_crypto == 'eth':
    await eth(ctx, address)  # Implement eth function similarly to ltc
  elif selected_crypto == 'sol':
    await sol(ctx, address)  # Implement sol function similarly to ltc


# Litecoin balance function
async def ltc(ctx, ltcaddress):
  response = requests.get(
      f'https://api.blockcypher.com/v1/ltc/main/addrs/{ltcaddress}/balance')
  if response.status_code == 200:
    data = response.json()
    balance = data['balance'] / 10**8
    total_balance = data['total_received'] / 10**8
    unconfirmed_balance = data['unconfirmed_balance'] / 10**8
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve balance. Please check the Litecoin address.**"
    )
    return

  cg_response = requests.get(
      'https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd'
  )
  if cg_response.status_code == 200:
    usd_price = cg_response.json()['litecoin']['usd']
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve the current price of Litecoin.**"
    )
    return

  usd_balance = balance * usd_price
  usd_total_balance = total_balance * usd_price
  usd_unconfirmed_balance = unconfirmed_balance * usd_price

  embed = discord.Embed(title="LTC BALANCE",
                        color=color,
                        description=f"ADDRESS :- **{ltcaddress}**")

  embed.add_field(
      name="Confirmed Balance",
      value=f"LTC  :- **{balance}**\nUSD :- **${usd_balance:.2f}**",
      inline=False)
  embed.add_field(
      name="Unconfirmed Balance",
      value=
      f"LTC  :- **{unconfirmed_balance}**\nUSD :- **${usd_unconfirmed_balance:.2f}**",
      inline=False)
  embed.add_field(
      name="Total Ltc Received",
      value=f"LTC  :- **{total_balance}**\nUSD :- **${usd_total_balance:.2f}**",
      inline=False)
  embed.set_footer(text="By Pixlbuilders")
  response_message = await ctx.send(embed=embed)
  await asyncio.sleep(60)
  await response_message.delete()


# Bitcoin balance function
async def btc(ctx, btcaddress):
  response = requests.get(
      f'https://api.blockcypher.com/v1/btc/main/addrs/{btcaddress}/balance')
  if response.status_code == 200:
    data = response.json()
    balance = data['balance'] / 10**8
    total_balance = data['total_received'] / 10**8
    unconfirmed_balance = data['unconfirmed_balance'] / 10**8
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve balance. Please check the Bitcoin address.**"
    )
    return

  cg_response = requests.get(
      'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
  )
  if cg_response.status_code == 200:
    usd_price = cg_response.json()['bitcoin']['usd']
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve the current price of Bitcoin.**"
    )
    return

  usd_balance = balance * usd_price
  usd_total_balance = total_balance * usd_price
  usd_unconfirmed_balance = unconfirmed_balance * usd_price

  embed = discord.Embed(title="BTC BALANCE",
                        color=color,
                        description=f"ADDRESS :- **{btcaddress}**")

  embed.add_field(
      name="Confirmed Balance",
      value=f"BTC  :- **{balance}**\nUSD :- **${usd_balance:.2f}**",
      inline=False)
  embed.add_field(
      name="Unconfirmed Balance",
      value=
      f"BTC  :- **{unconfirmed_balance}**\nUSD :- **${usd_unconfirmed_balance:.2f}**",
      inline=False)
  embed.add_field(
      name="Total BTC Received",
      value=f"BTC  :- **{total_balance}**\nUSD :- **${usd_total_balance:.2f}**",
      inline=False)
  embed.set_footer(text="By Pixlbuilders")
  response_message = await ctx.send(embed=embed)
  await asyncio.sleep(60)
  await response_message.delete()


# Ethereum balance function
async def eth(ctx, ethaddress):
  response = requests.get(
      f'https://api.blockcypher.com/v1/eth/main/addrs/{ethaddress}/balance')
  if response.status_code == 200:
    data = response.json()
    balance = int(data['balance']) / 10**18
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve balance. Please check the Ethereum address.**"
    )
    return

  cg_response = requests.get(
      'https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd'
  )
  if cg_response.status_code == 200:
    usd_price = cg_response.json()['ethereum']['usd']
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve the current price of Ethereum.**"
    )
    return

  usd_balance = balance * usd_price

  embed = discord.Embed(title="ETH BALANCE",
                        color=color,
                        description=f"ADDRESS :- **{ethaddress}**")

  embed.add_field(
      name="Balance",
      value=f"ETH  :- **{balance}**\nUSD :- **${usd_balance:.2f}**",
      inline=False)
  embed.set_footer(text="By Pixlbuilders")
  response_message = await ctx.send(embed=embed)
  await asyncio.sleep(60)
  await response_message.delete()


# Solana balance function
async def sol(ctx, soladdress):
  response = requests.get(
      f'https://api.blockcypher.com/v1/solana/main/addrs/{soladdress}/balance')
  if response.status_code == 200:
    data = response.json()
    balance = int(data['balance']) / 10**9
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve balance. Please check the Solana address.**"
    )
    return

  cg_response = requests.get(
      'https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd'
  )
  if cg_response.status_code == 200:
    usd_price = cg_response.json()['solana']['usd']
  else:
    await ctx.send(
        "<:error:1196504491856506881> **Failed to retrieve the current price of Solana.**"
    )
    return

  usd_balance = balance * usd_price

  embed = discord.Embed(title="SOL BALANCE",
                        color=color,
                        description=f"ADDRESS :- **{soladdress}**")

  embed.add_field(
      name="Balance",
      value=f"SOL  :- **{balance}**\nUSD :- **${usd_balance:.2f}**",
      inline=False)
  embed.set_footer(text="By Pixlbuilders")
  response_message = await ctx.send(embed=embed)
  await asyncio.sleep(60)
  await response_message.delete()


status_data = [
    {
        "name": "Plague Store",
        "url":
        "https://www.youtube.com/watch?v=s-bZD3O3P80&list=PL3_PicFYccc8jiQSRo1YohA-3NM4pifBS&index=2&pp=iAQB8AUB",
        "interval_minutes": 1
    },
    # Add your other status entries here
]


async def change_presence():
  while True:
    for status_entry in status_data:
      # Set the bot's status to "Streaming"
      await bot.change_presence(activity=discord.Streaming(
          name=status_entry["name"], url=status_entry["url"]))
    await asyncio.sleep(status_entry["interval_minutes"] * 60)


@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name}')
  bot.loop.create_task(change_presence())


# Start the bot
bot.run(
    "MTE4NTUxODczMzEwODcxOTY4Ng.GSEh2n.Ocxt31ioFEYHCL7E2roH--jT6Vscyt328t7WWk")
