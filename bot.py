# bot.py
# blackjack bot written by zachary.robinson on April 7, 2021
# CS 521 A4
import os
import discord  # discord.py is a wrapper for software discord
import random  # used in cardpicker function line 27 to pick a random card
import json  # data storage files. Used to store user's chip balance and card count in each game
from discord.ext import commands  # initiates a bot that runs off commands
from dotenv import load_dotenv
load_dotenv()  # necessary to hide token to bot for added security in line 13

TOKEN = os.getenv('DISCORD_TOKEN')  # references the .env file. Unique identifier for the bot

help_command = commands.DefaultHelpCommand(
    no_category='Commands'  # removes header when default !help command is used
)

bot = commands.Bot(
    command_prefix="!",
    help_command=help_command  # gives a subject line 'commands' when !help is used instead of 'no_subject'
)

# class that contains list of cards
class Cards:
    cardlist = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'Jack', 'Queen', 'King', 'Ace']

# function to pick a random card from cardlist
def cardout():
    deck = Cards.cardlist
    deal = random.choice(deck)
    return str(deal)

@bot.command(
    help="Starts the game by dealing you two cards"
)
# ctx variable in discord.py stands stands for 'chat message'
# async def is a basic function language to use discord's command bot
# async def "xyx", xyz = command used after ! in chat
# command to start the game and deal user two cards
async def start(ctx):
    getbank = await get_bank_data()  # opens bank.json to read
    getcount = await get_count_data()  # opens count.json to read

    # sets up to run loop to deal two cards line 151
    user = ctx.author
    card_total = getcount[str(user.id)]["total"]
    i = 0

    if card_total > 0:
        #exit condition if user has already been dealt cards
        await ctx.send("You have already started a game. Use !hit to deal another card or !check otherwise.")

    else:
        # deals two cards to start the game to user and presents user with their total
        while i < 2:
            card= cardout()
            if card in ('2', '3', '4', '5', '6', '7', '8', '9'):
                getcount[str(user.id)]["total"] += int(card)
                await ctx.send(f"Your card: " + str(card))
                i += 1
                with open("count.json", "w") as f:
                    json.dump(getcount, f)  # overwrite new count to JSON file

            elif card == 'Ace':
                if getcount[str(user.id)]["total"] > 10:
                    getcount[str(user.id)]["total"] += 1  # if user gets an ace, and will bust with an 11, defaults 11
                    await ctx.send(f"Your card: " + str(card) + " low")
                    i+=1
                    with open("count.json", "w") as f:
                        json.dump(getcount, f)  # overwrite new count to JSON file

                else:
                    getcount[str(user.id)]["total"] += 11  # if user gets an ace, and won't bust with an 11, defaults 11
                    await ctx.send(f"Your card: " + str(card) + " high")
                    i += 1
                    with open("count.json", "w") as f:
                        json.dump(getcount, f)  # overwrite new count to JSON file
            else:
                getcount[str(user.id)]["total"] += 10  # if card is jack, queen or king, increase user count by 10
                await ctx.send(f"Your card: " + str(card))
                i += 1
                with open("count.json", "w") as f:
                    json.dump(getcount, f)  # overwrite new count to JSON file


        card_total = getcount[str(user.id)]["total"]  # redefine card_total for new conditions
        # exit condition if count equals 21
        if card_total != 21:
            await ctx.send(f"Your card count: {getcount[str(user.id)]['total']}\n"
                           f"Use !hit to be dealt another card or !check to stay" )

        # continue play otherwise
        else:
            await ctx.send(f"Your card count: {getcount[str(user.id)]['total']}, you win!\n"
                           f"50 chips have been deposited into your account")  # ctx.send sends message in same channel command was sent

            getcount[str(user.id)]["total"] -= 21  # sets card count to 0
            with open("count.json", "w") as f:
                json.dump(getcount, f)  # overwrites users card count to JSON file

            getbank[str(user.id)]["wallet"] += 50  # increases user chip balance by 50
            with open("bank.json", "w") as f:
                json.dump(getbank, f)  # overwrites users chip count to JSON file


@bot.command(
    help="Deals you a random card two through ace."  # defined command when !help is used in chat
)                                                    # !help is default command with discord.py that returns all  written commands

# command to deal user another card
async def hit(ctx):
    await open_counter_account(ctx.author)  # opens a profile in JSON file if new user interacting with bot


    getbank = await get_bank_data()  # opens bank.json to read
    getcount = await get_count_data()  # opens count.json to read
    user = ctx.author

    # exit condition if user has not used !start
    if getcount[str(user.id)]["total"] == 0:
        await ctx.send(f"You have not started a game. Use !start to play.")
        return

    await card_count(ctx)
    getcount = await get_count_data()
    if getcount[str(user.id)]["total"] == 21:  # exit condition if user card count hits 21 exactly
        await ctx.send(f"Your card count: {getcount[str(user.id)]['total']}, you win!\n"
                       f"50 chips have been deposited into your account")  # ctx.send sends message in same channel command was sent

        getcount[str(user.id)]["total"] -= 21  # sets card count to 0
        with open("count.json", "w") as f:
            json.dump(getcount, f)  # overwrites users card count to JSON file

        getbank[str(user.id)]["wallet"] += 50  # increases user chip balance by 50
        with open("bank.json", "w") as f:
            json.dump(getbank, f)  # overwrites users chip count to JSON file

    elif getcount[str(user.id)]["total"] > 21:  # exit condition if users card count breaks 21
        await ctx.send(f"Your card count: {getcount[str(user.id)]['total']}, you lose!\n"
                    f"50 chips have been deducted from your account")

        getcount[str(user.id)]["total"] -= getcount[str(user.id)]["total"]
        with open("count.json", "w") as f:
            json.dump(getcount, f)

        getbank[str(user.id)]["wallet"] -= 50
        with open("bank.json", "w") as f:
            json.dump(getbank, f)  # deducts 50 chips & overrites JSON file

    else:
        await ctx.send(f"Your card count: {getcount[str(user.id)]['total']}\n"
                       f"Use !hit to receive another card or !check to stay")
        # returns card total if under 21 to give the user the option to either !hit or !check(line 125)


# function deals user a card, and stores the value of that card towards users total in JSON file
async def card_count(ctx):
    user = ctx.author
    getcount = await get_count_data()  # calls function line 117
    card = cardout()

    if card in ('2', '3', '4', '5', '6', '7', '8', '9'):
        getcount[str(user.id)]["total"] += int(card)
        await ctx.send(f"Your card: " + str(card))
        with open("count.json", "w") as f:
            return json.dump(getcount, f)

    elif card == 'Ace':
        if getcount[str(user.id)]["total"] > 10:
            getcount[str(user.id)]["total"] += 1  # if user gets an ace, and will bust with an 11, defaults 11
            await ctx.send(f"Your card: " + str(card) + " low")
            with open("count.json", "w") as f:
                return json.dump(getcount, f)

        else:
            getcount[str(user.id)]["total"] += 11  # if user gets an ace, and won't bust with an 11, defaults 11
            await ctx.send(f"Your card: " + str(card) + " high")
            with open("count.json", "w") as f:
                return json.dump(getcount, f)

    else:
        getcount[str(user.id)]["total"] += 10  # if card is jack, queen or king, increase user count by 10
        await ctx.send(f"Your card: " + str(card))
        with open("count.json", "w") as f:
            return json.dump(getcount, f)


# function to create a new profile in JSON file to store users card count
async def open_counter_account(user):
    with open("count.json", "r") as f:
        users = json.load(f)
    if str(user.id) in users:  # exit condition if user already has an account
        return False

    else:
        users[str(user.id)] = {}  # creates dictionary to access access total
        users[str(user.id)]["total"] = 0

        with open("count.json", "w") as f:
            json.dump(users, f)
            return  # writes new profile and card count to JSON file

# function to retrieve whatever card count value is stored in the JSON file for command user
async def get_count_data():
    with open("count.json") as f:
        users = json.load(f)
    return users


@bot.command(
    help="Ends play, initiates dealer's turn"
)
# command to esentially end the game, runs dealer's hand to see who wins
async def check(ctx):
    getbank = await get_bank_data()  # opens bank.json to read
    getcount = await get_count_data()  # opens count.json to read

    user = ctx.author
    count_amount = getcount[str(user.id)]["total"]
    dealer_count = 0  # sets up value of dealers hand for line 145 loop

    if getcount[str(user.id)]["total"] == 0:  # exit condition if user has not used !start and tried to use !check
        await ctx.send("You have not started a game. Use !start to start a game.")

    elif getcount[str(user.id)]["total"] < 12:  # exit condition if user has under 12 points, since no way they can bust
        await ctx.send("You should use !hit again, you cannot lose!")

    else:
        await ctx.send(f"Your card count: {count_amount}")  # re-shows user's current card amount before running dealers hand
        while dealer_count < count_amount + 1:  # loop to keep dealing cards to dealer until they either:
                                                # get closer to 21 than user, get exactly 21, or bust over 21
            card = cardout()
            if card in ('2', '3', '4', '5', '6', '7', '8', '9'):  # searches list of face value cards for generated card
                dealer_count += int(card)  # increases dealers card count
                await ctx.send(f"Dealer is dealt " + str(card))

            elif card == 'Ace':
                if dealer_count > 10:
                    dealer_count += 1  # if dealer gets an ace, defaults value to 1 if 11 will bust them
                    await ctx.send(f"Dealer is dealt " + str(card) + " low")

                else:
                    dealer_count += 11  # if dealer gets an ace, and won't bust with an 11, defaults 11
                    await ctx.send(f"Dealer is dealt " + str(card) + " high")

            else:
                dealer_count += 10  # if card is not a face value card or ace, adds 10 to count for jack, queen & king
                await ctx.send(f"Dealer is dealt " + str(card))

        # if dealer's count exceeds 21, busts them and adds 50 chips to users wallet for winning
        if dealer_count > 21:
            await ctx.send(f"Dealer's card count: " + str(dealer_count) + ", bust! You win!\n"
                           f"50 chips have been deposited into your wallet.")
            getcount[str(user.id)]["total"] -= getcount[str(user.id)]["total"]
            with open("count.json", "w") as f:
                json.dump(getcount, f)  # game is over, sets users card count to 0 and overwrites JSON file

            getbank[str(user.id)]["wallet"] += 50
            with open("bank.json", "w") as f:
                json.dump(getbank, f)  # overwrites JSON chip value for user to plus 50

        # if the dealer did not bust and the loop stopped, they either:
        # hit 21 or are closer to 21 than the user. deducts 50 chips from user
        else:
            await ctx.send(f"Dealer's card count: " + str(dealer_count) + ", dealer wins!\n"
                           f"50 chips have been deducted from your wallet.")
            getcount[str(user.id)]["total"] -= getcount[str(user.id)]["total"]
            with open("count.json", "w") as f:
                json.dump(getcount, f)  # game is over, sets users card count to 0 and overwrites JSON file

            getbank[str(user.id)]["wallet"] -= 50
            with open("bank.json", "w") as f:
                json.dump(getbank, f)  # overwrites JSON chip value for user to less 50


@bot.command(
    help="Displays your chip balance."
)
# command to display users balance in clean embedded format
async def bal(ctx):
    await open_bank_account(ctx.author)

    getbank = await get_bank_data()
    user = ctx.author
    wallet_amt = getbank[str(user.id)]["wallet"]

    ebd = discord.Embed(title=f"{user.name}'s balance", color=discord.Color.green())
    ebd.add_field(name="Wallet bal", value=wallet_amt)
    await ctx.send(embed=ebd)


# function to open a wallet for the user if they do not have one
async def open_bank_account(user):
    with open("bank.json", "r") as f:
        users = json.load(f)

    if str(user.id) in users:  # checks if user already has a bank account stops if true
        return False

    else:
        users[str(user.id)] = {}  # creates dictionary to access wallet first then bank
        users[str(user.id)]["wallet"] = 0

        with open("bank.json", "w") as f:
            json.dump(users, f)
            return

# function to open the json file to read or write
async def get_bank_data():
    with open("bank.json", "r") as f:
        getbank = json.load(f)
    return getbank


@bot.command(
    help="Adds a random amount of chips to your wallet"
)
# function to add more chips to users wallet
async def buy(ctx):
    user = ctx.author
    getbank = await get_bank_data()
    await open_bank_account(user)

    amount = random.randrange(101)
    getbank[str(user.id)]["wallet"] += amount

    with open("bank.json", "w") as f:
        json.dump(getbank, f)

    await ctx.send(f"You have received {amount} chips in your wallet\n"
                   f"Updated balance:")

    wallet_amt = getbank[str(user.id)]["wallet"]

    ebd = discord.Embed(title=f"{user.name}'s balance", color=discord.Color.green())
    ebd.add_field(name="Wallet bal", value=wallet_amt)
    await ctx.send(embed=ebd)


@bot.event
# when code is originally ran, prints confirmation that there are no errors
async def on_ready():
    print("Connected to Discord!")

# runs the script and connects it to my bot on Discord's website
bot.run(TOKEN)
