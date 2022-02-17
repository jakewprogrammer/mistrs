import requests
import json
import datetime
import time
import os
import random
import discord
import asyncio
import traceback
import twitter
from in_stock_trades_bot import scanInStockTrades
from twitter_bot import set_up_twitter_api
from discord.ext.commands import Bot
from discord.ext import commands
from fake_useragent import UserAgent
from dotenv import dotenv_values

config = dotenv_values(".env")
twitter_api = set_up_twitter_api()
########################## THIS CONTROLS WHETHER OR NOT THE BOT IS LIVE OR IN TEST MODE #################################
runMode = config.get("RUN_MODE", "not_production")
TestPrintingOnlyMode = True
DEBUG_MENTION_MAP = False
if runMode == "production":
    print("Running in Production Mode")
    TestPrintingOnlyMode = False
else:
    print("Running in dev mode")

# disabling the tweets for now because they're not up to snuff
TweetsEnabled = False
#########################################################################################################################

DiscordChannelToMentionMap = {}
with open("DiscordChannelMentionMapFile.json") as f:
    DiscordChannelToMentionMap = json.load(f)


productCatalog = {}
with open("right_stuf_anime.json") as f:
    productCatalog = json.load(f)

with open("right_stuf_anime.on_start_backup.json", "w") as outfile:
    json.dump(productCatalog, outfile)

dateFormat = "%b %d %Y %I:%M%p"

itemsProcessed = 0

threadBlocked = False

MY_GUILD_NAME = "Jake's Manga In-Stock Tracker"

IN_STOCK_CHANNEL = "in_stock"
OUT_OF_STOCK_CHANNEL = "out_of_stock"
DAMAGED_AND_IMPERFECT_CHANNEL = "damaged_and_imperfect"
PREORDERS_CHANNEL = "preorders"
TEST_CHANNEL = "testing_please_ignore"
ANIME_CHANNEL = "anime"
KODANSHA_CHANNEL = "kodansha_comics"
YEN_PRESS_CHANNEL = "yen_press"
VIZ_CHANNEL = "viz_books"
UDON_CHANNEL = "udon_entertainment"
VERTICAL_CHANNEL = "vertical"
DARK_HORSE_CHANNEL = "dark_horse"
SEVENS_SEAS_CHANNEL = "seven_seas"
SQUARE_ENIX_CHANNEL = "square_enix_manga"

AIRSHIP_LN_CHANNEL = "airship"
VIZ_LN_CHANNEL = "viz_books_ln"
VERTICAL_LN_CHANNEL = "vertical_ln"
YEN_ON_LN_CHANNEL = "yen_on"
OTHER_LN_CHANNEL = "other"

FIGURINES_CHANNEL = "figures_and_collectables"

# RS Manga and Novel publishers
KODANSHA = "KODANSHA-COMICS"
YEN_PRESS = "YEN-PRESS"
VIZ = "VIZ-BOOKS"
UDON = "UDON-ENTERTAINMENT"
VERTICAL = "VERTICAL"
DARK_HORSE = "DARK-HORSE"
DARK_HORSE_MANGA = "DARK-HORSE-MANGA"
SEVEN_SEAS = "SEVEN-SEAS"
SQUARE_ENIX = "SQUARE-ENIX-MANGA"
# novels only
AIRSHIP = "AIRSHIP"
YEN_ON = "YEN-ON"

ANIME_CATEGORY = "Blu~ray,DVD"
ANIME = "ANIME"
MANGA = "Manga"
NOVELS = "Novels"
FIGURINES = "Figurines"

PUBLISHERS = [
    DARK_HORSE,
    DARK_HORSE_MANGA,
    KODANSHA,
    SEVEN_SEAS,
    SQUARE_ENIX,
    UDON,
    VERTICAL,
    VIZ,
    YEN_PRESS,
]

NOVEL_PUBLISHERS = [AIRSHIP, DARK_HORSE_MANGA,
                    SEVEN_SEAS, UDON, VERTICAL, VIZ, YEN_ON]

MangaPublisherNameToDiscordChannelNameMap = {
    ANIME: ANIME_CHANNEL,
    DARK_HORSE: DARK_HORSE_CHANNEL,
    DARK_HORSE_MANGA: DARK_HORSE_CHANNEL,
    KODANSHA: KODANSHA_CHANNEL,
    SEVEN_SEAS: SEVENS_SEAS_CHANNEL,
    SQUARE_ENIX: SQUARE_ENIX_CHANNEL,
    UDON: UDON_CHANNEL,
    VERTICAL: VERTICAL_CHANNEL,
    VIZ: VIZ_CHANNEL,
    YEN_PRESS: YEN_PRESS_CHANNEL,
}

NovelsPublisherNameToDiscordChannelNameMap = {
    AIRSHIP: AIRSHIP_LN_CHANNEL,
    # other categoried
    DARK_HORSE_MANGA: OTHER_LN_CHANNEL,
    # same as airship
    SEVEN_SEAS: AIRSHIP_LN_CHANNEL,
    # other categoried
    UDON: OTHER_LN_CHANNEL,
    VERTICAL: VERTICAL_LN_CHANNEL,
    VIZ: VIZ_LN_CHANNEL,
    YEN_ON: YEN_ON_LN_CHANNEL,
    YEN_PRESS: YEN_ON_LN_CHANNEL,
}

AnimeDiscordChannelMap = {
    ANIME: ANIME_CHANNEL,
}

FigurinesDiscordChannelMap = {
    FIGURINES: FIGURINES_CHANNEL,
}

IN_STOCK = "in stock"
OUT_OF_STOCK = "out of stock"
PREORDER = "preorder"

CategoryToDiscordChannelMap = {
    NOVELS: NovelsPublisherNameToDiscordChannelNameMap,
    ANIME: AnimeDiscordChannelMap,
    MANGA: MangaPublisherNameToDiscordChannelNameMap,
    FIGURINES: FigurinesDiscordChannelMap,
}

DiscordChannelMap = {
    DARK_HORSE: DARK_HORSE_CHANNEL,
    DARK_HORSE_MANGA: DARK_HORSE_CHANNEL,
    KODANSHA: KODANSHA_CHANNEL,
    SEVEN_SEAS: SEVENS_SEAS_CHANNEL,
    SQUARE_ENIX: SQUARE_ENIX_CHANNEL,
    UDON: UDON_CHANNEL,
    VERTICAL: VERTICAL_CHANNEL,
    VIZ: VIZ_CHANNEL,
    YEN_PRESS: YEN_PRESS_CHANNEL,
}

publisherNameHumanReadable = {
    ANIME: "Anime",
    DARK_HORSE: "Dark Horse",
    DARK_HORSE_MANGA: "Dark Horse",
    KODANSHA: "Kodansha Comics",
    SEVEN_SEAS: "Seven Seas",
    SQUARE_ENIX: "Square Enix Manga",
    UDON: "Udon Entertainment",
    VERTICAL: "Vertical",
    VIZ: "Viz Books",
    YEN_PRESS: "Yen Press",
    FIGURINES: "Figurines and Collectables"
}

guildChannelList = {
    MY_GUILD_NAME: {
        IN_STOCK_CHANNEL: {},
        OUT_OF_STOCK_CHANNEL: {},
        DAMAGED_AND_IMPERFECT_CHANNEL: {},
        PREORDERS_CHANNEL: {},
        TEST_CHANNEL: {},
        KODANSHA_CHANNEL: {},
        VIZ_CHANNEL: {},
        VERTICAL_CHANNEL: {},
        DARK_HORSE_CHANNEL: {},
        SEVENS_SEAS_CHANNEL: {},
        SQUARE_ENIX_CHANNEL: {},
        UDON_CHANNEL: {},
        YEN_PRESS_CHANNEL: {},
        ANIME_CHANNEL: {},
        AIRSHIP_LN_CHANNEL: {},
        VIZ_LN_CHANNEL: {},
        VERTICAL_LN_CHANNEL: {},
        YEN_ON_LN_CHANNEL: {},
        OTHER_LN_CHANNEL: {},
        FIGURINES_CHANNEL: {},
    }
}

categoryList = {
    FIGURINES: [FIGURINES],
    ANIME: [ANIME],
    MANGA: PUBLISHERS,
    NOVELS: NOVEL_PUBLISHERS,
}


def generateMentions(discordChannelMentionMap, discordChannel, stockStatus):
    ROLE_ID = discordChannelMentionMap.get(discordChannel, {"a": "b"}).get(
        stockStatus, None
    )
    if ROLE_ID:
        return "<@&" + ROLE_ID + ">\n"
    else:
        return ""


def replaceNameWithMention(discordChannelMentionMap, message):
    for series in discordChannelMentionMap.get('series', {}).keys():
        if series in message:
            role_id = discordChannelMentionMap.get(
                'series', {}).get(series, None)
            if role_id:
                replaceText = "<@&" + str(role_id) + ">"
                message = message.replace(series, replaceText)
    return message


async def doublePrint(
    discordChannel, message, discordChannelMentionMap={}, stockStatus="none"
):
    try:
        mention = generateMentions(
            discordChannelMentionMap=discordChannelMentionMap,
            discordChannel=discordChannel,
            stockStatus=stockStatus,
        )
        if TestPrintingOnlyMode:
            await guildChannelList[MY_GUILD_NAME][TEST_CHANNEL].send(mention + message)
            #print()
        else:
            await guildChannelList[MY_GUILD_NAME][discordChannel].send(
               mention + message
            )
            #print()
    except:
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("error posting to discord: [" + message + "]")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        traceback.print_exc()
    print()
    print(message)


async def triplePrint(
    discordChannel,
    message,
    discordChannelMentionMap={},
    stockStatus="none",
    twitterMessagePrefix="",
):
    try:
        await doublePrint(
            discordChannel, message, discordChannelMentionMap, stockStatus
        )
        if not TestPrintingOnlyMode and TweetsEnabled:
            twitter_api.PostUpdate(twitterMessagePrefix + message)
    except:
        print("Maybe error posting to twitter")


async def conditionalCombinedPrint(
    discordChannel, message, discordMessageParts="", category=""
):
    if category != MANGA:
        return
    try:
        await guildChannelList[MY_GUILD_NAME][discordChannel].send(
            discordMessageParts + message
        )
    except:
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        print("error posting to discord: [" + message + "]")
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        traceback.print_exc()


def makeRSURL(page=0, publisher="", category=""):
    increments = 96
    publisherURLPart = ""

    if category:
        publisherURLPart = "&custitem_rs_web_class=" + category
        if publisher:
            publisherURLPart += "&custitem_rs_publisher=" + publisher
    elif publisher == "ANIME" or publisher == "Anime" or publisher == "Blu~ray,DVD":
        publisherURLPart = "&custitem_rs_web_class=Blu~ray,DVD"
    elif publisher == "FIGURINES" or publisher == "Figurines":
        publisherURLPart = "&custitem_rs_web_class=Figures%2CMemorabilia%2CModel-Kits"
    elif publisher:
        publisherURLPart = (
            "&custitem_rs_publisher=" + publisher + "&custitem_rs_web_class=Manga"
        )

    rsLinkParts = [
        "https://www.rightstufanime.com/api/items?c=546372&country=US&currency=USD",
        publisherURLPart,
        "&custitem_rs_adult=false&fieldset=search&include=facets&language=en&",
        "limit=",
        str(increments),
        "&n=2&offset=",
        str(increments * page),
        "&pricelevel=5&sort=relevance:asc&use_pcv=F",
    ]
    return "".join(rsLinkParts)


def printProgressBar(
    iteration, prefix="", suffix="", decimals=1, length=100, fill="█", printEnd="\r"
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    if iteration % 1000 == 0:
        print()

    filledLength = int(length * (iteration % 1000 + 1) // 1000)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {suffix}", end=printEnd)
    # Print New Line on Complete


###################################


def RSprocessItem(item, foundURL, now, publisher, category):
    i = {}
    i["name"] = item["storedisplayname"]
    i["price"] = item["onlinecustomerprice_formatted"]
    i["purchasable"] = item["isinstock"]
    # need to look into handling "ispurchasable" separately as they use this to toggle purchasability on preorders as a stock signal

    i["url"] = "https://www.rightstufanime.com/" + item["urlcomponent"]
    i["found_on_url"] = foundURL
    i["publisher"] = publisher
    i["category"] = category
    if "custitem_rs_new_releases_preorders" in item:
        if (
            item["custitem_rs_new_releases_preorders"] == None
            or "None" in item["custitem_rs_new_releases_preorders"]
            or "New Release" in item["custitem_rs_new_releases_preorders"]
        ):
            i["preorder"] = False
        elif "Pre-order" in item["custitem_rs_new_releases_preorders"]:
            i["preorder"] = True
        else:
            print(item["custitem_rs_new_releases_preorders"])
            print("**********FUCKKKKK**************")
    else:
        i["preorder"] = False
    if "custitem_damaged_type" in item:
        if item["custitem_damaged_type"] == "Imperfect":
            i["imperfect"] = True
        else:
            i["imperfect"] = False
        if item["custitem_damaged_type"] == "Damaged":
            i["damaged"] = True
        else:
            i["damaged"] = False
    if "upccode" in item:
        i["upccode"] = item["upccode"]
    i["last_checked"] = now.strftime(dateFormat)
    return i


###################################

# we should refactor this. emit a status enum


async def compareItemAndPublishMessage(
    i,
    productCatalogMap,
    now,
    mDict,
    publisher,
    category,
    itemsProcessedForPublisher,
    discordChannelMentionMap,
):
    printProgressBar(
        itemsProcessedForPublisher,
        prefix="Progress:",
        suffix=str(itemsProcessedForPublisher),
        length=50,
    )
    changes = False
    url = i["url"]
    nameAndURL = replaceNameWithMention(
        discordChannelMentionMap, i["name"]) + "\n" + url
    if url in productCatalogMap:
        if "in-stock-time" in productCatalogMap[url]:
            i["in-stock-time"] = productCatalogMap[url].get("in-stock-time")
        if "out-of-stock-time" in productCatalogMap[url]:
            i["out-of-stock-time"] = productCatalogMap[url].get("out-of-stock-time")
        if "pre-order-time" in productCatalogMap[url]:
            i["pre-order-time"] = productCatalogMap[url].get("pre-order-time")

        if (
            "damaged" in i
            and i["damaged"]
            and i["purchasable"]
            and not productCatalogMap[url]["purchasable"]
        ):
            mDict["damagedMismatch"] += 1
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await doublePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**[Damaged]**\n" + nameAndURL,
            )
            await conditionalCombinedPrint(
                DAMAGED_AND_IMPERFECT_CHANNEL,
                "**[Damaged]**\n" + nameAndURL,
                "",
                category,
            )
        elif (
            "imperfect" in i
            and i["imperfect"]
            and i["purchasable"]
            and not productCatalogMap[url]["purchasable"]
        ):
            mDict["imperfectMismatch"] += 1
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await doublePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**[Imperfect]**\n" + nameAndURL,
            )
            await conditionalCombinedPrint(
                DAMAGED_AND_IMPERFECT_CHANNEL,
                "**[Imperfect]**\n" + nameAndURL,
                "",
                category,
            )
        elif i["purchasable"] and productCatalogMap[url]["preorder"] and not i["preorder"]:
            mDict["mismatches"] += 1
            mDict["preorderMismatch"] += 1
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await triplePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**[Preorder Now In Stock]**\n" + nameAndURL,
                discordChannelMentionMap,
                IN_STOCK,
            )
            await conditionalCombinedPrint(
                IN_STOCK_CHANNEL,
                "**[Preorder Now In Stock]**\n" + nameAndURL,
                "",
                category,
            )
        elif (
            productCatalogMap[url]["purchasable"]
            and not i["purchasable"]
            and not productCatalogMap[url]["preorder"]
        ):
            mDict["mismatches"] += 1
            mDict["outOfStockMismatch"] += 1
            changes = True
            i["out-of-stock-time"] = now.strftime(dateFormat)
            await doublePrint(
                CategoryToDiscordChannelMap[category][publisher],
                nameAndURL,
                discordChannelMentionMap,
                OUT_OF_STOCK,
            )
            await conditionalCombinedPrint(
                OUT_OF_STOCK_CHANNEL, "**[OUT OF STOCK]**\n" +
                nameAndURL, "", category
            )
        elif not productCatalogMap[url]["purchasable"] and i["purchasable"]:
            mDict["mismatches"] += 1
            mDict["inStockMismatch"] += 1
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await triplePrint(
                CategoryToDiscordChannelMap[category][publisher],
                nameAndURL,
                discordChannelMentionMap,
                IN_STOCK,
                "**[RESTOCK]**\n",
            )
            await conditionalCombinedPrint(
                IN_STOCK_CHANNEL, "**[RESTOCK]**\n" + nameAndURL, "", category
            )
    else:
        if i["preorder"]:
            changes = True
            i["pre-order-time"] = now.strftime(dateFormat)
            await triplePrint(
                CategoryToDiscordChannelMap[category][publisher],
                nameAndURL,
                discordChannelMentionMap,
                PREORDER,
                "**[NEW PREORDER]**\n",
            )
            await conditionalCombinedPrint(
                PREORDERS_CHANNEL, "**[NEW PREORDER]**\n" +
                nameAndURL, "", category
            )
        elif "damaged" in i and i["damaged"]:
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await doublePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**[Damaged]**\n" + nameAndURL,
            )
            await conditionalCombinedPrint(
                DAMAGED_AND_IMPERFECT_CHANNEL,
                "**[Damaged]**\n" + nameAndURL,
                "",
                category,
            )
        elif "imperfect" in i and i["imperfect"]:
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await doublePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**[Imperfect]**\n" + nameAndURL,
            )
            await conditionalCombinedPrint(
                DAMAGED_AND_IMPERFECT_CHANNEL,
                "**[Imperfect]**\n" + nameAndURL,
                "",
                category,
            )
        elif i["purchasable"]:
            changes = True
            i["in-stock-time"] = now.strftime(dateFormat)
            await triplePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**[NEW]**\n" + nameAndURL,
                discordChannelMentionMap,
                IN_STOCK,
            )
            await conditionalCombinedPrint(
                IN_STOCK_CHANNEL, "**[NEW]**\n" + nameAndURL, "", category
            )
        else:
            changes = True
            i["out-of-stock-time"] = now.strftime(dateFormat)
            await doublePrint(
                CategoryToDiscordChannelMap[category][publisher],
                "**New Item scanned in out of stock:**\n" + nameAndURL,
                discordChannelMentionMap,
            )
            await conditionalCombinedPrint(
                OUT_OF_STOCK_CHANNEL,
                "**New Item scanned in out of stock:**\n" + nameAndURL,
                "",
                category,
            )

    return changes


###################################


async def runApp(category, publishers, DiscordChannelToMentionMap):
    print("Category: " + category)
    ua = UserAgent()
    headers = {"User-Agent": ua.random}
    global itemsProcessed

    mDict = {
        "mismatches": 0,
        "preorderMismatch": 0,
        "inStockMismatch": 0,
        "outOfStockMismatch": 0,
        "damagedMismatch": 0,
        "imperfectMismatch": 0,
    }

    for publisher in publishers:
        publisherStartTime = datetime.datetime.now()
        page = 0
        itemsProcessedForPublisher = 0

        while True:
            url = ""
            if publisher == ANIME:
                url = makeRSURL(page, "ANIME")
            elif publisher == FIGURINES:
                url = makeRSURL(page, "FIGURINES")
                print("##### URL " + str(url))
            else:
                url = makeRSURL(page, publisher, category)
            # print(url)

            await asyncio.sleep(0.15)
            # await asyncio.sleep(0.5)
            request = requests.get(url, headers=headers)

            if request.status_code == 400:
                print("$$$$$$$$$$ Bad page load detected at page: " + str(page))
                break
            if request.status_code != 200:
                print("$$$$$$$$$$ Weird status code: " +
                      str(request.status_code))
                continue

            if "items" not in request.json():
                print("uh oh shit************")

            items = request.json()["items"]

            now = datetime.datetime.now()
            changes = False
            # Scan page of items loop
            for item in items:
                await asyncio.sleep(0.13)
                i = RSprocessItem(item, url, now, publisher, category)
                itemsProcessed += 1
                itemsProcessedForPublisher += 1
                
                innerChanges = await compareItemAndPublishMessage(
                    i,
                    productCatalog,
                    now=now,
                    mDict=mDict,
                    publisher=publisher,
                    category=category,
                    itemsProcessedForPublisher=itemsProcessedForPublisher,
                    discordChannelMentionMap=DiscordChannelToMentionMap,
                )

                changes = changes or innerChanges

                productCatalog[i["url"]] = i

            # Dump changes to disk
            if changes:
                print("Dumping changes to disk...")
                with open("right_stuf_anime._change_dump_backup.json", "w") as outfile:
                    json.dump(productCatalog, outfile)
                with open("right_stuf_anime.json", "w") as outfile:
                    json.dump(productCatalog, outfile)

            # Check for next query page
            nextPageFound = False
            if "links" in request.json():
                for item in request.json()["links"]:
                    if "rel" in item:
                        if item["rel"] == "next":
                            nextPageFound = True
                            page += 1

            if not nextPageFound:
                print()
                print("Last page: " + str(page))
                break

        publisherEndTime = datetime.datetime.now()
        print("------------------------------------------------")
        print("Category: " + publisher)
        print("Publisher: " + publisher)
        print("Mismatches This Session: " + str(mDict["mismatches"]))
        print("In Stock mismatches: " + str(mDict["inStockMismatch"]))
        print("Out Of Stock mismatches: " + str(mDict["outOfStockMismatch"]))
        print("Preorder Mismatches: " + str(mDict["preorderMismatch"]))
        print("Damaged Mismatches: " + str(mDict["damagedMismatch"]))
        print("Imperfect Mismatches: " + str(mDict["imperfectMismatch"]))
        print("End time: " + publisherEndTime.strftime(dateFormat))
        print("Total time: " + str(publisherEndTime - publisherStartTime))
        print(
            "Total time per page: "
            + str((publisherEndTime - publisherStartTime) / (page + 1))
        )
        print("Items processed this publisher: " +
              str(itemsProcessedForPublisher))
        print("Items processed this session: " + str(itemsProcessed))
        print("------------------------------------------------")
        with open("right_stuf_anime._publisher_done_dump_backup.json", "w") as outfile:
            json.dump(productCatalog, outfile)
        with open("right_stuf_anime.json", "w") as outfile:
            json.dump(productCatalog, outfile)
    await doublePrint(TEST_CHANNEL, "Loop complete for category: " + category + ".")


###################################


bot = commands.Bot(command_prefix="!")

discordSecret = config["TOKEN"]


@bot.command(name="test")
async def test(ctx):
    print("message content")
    print(ctx.message.content)
    print("roles")
    print(ctx.guild.roles)
    print("channels")
    print(ctx.guild.channels)


@bot.command(name="create-mention-role")
async def create_mention_role(ctx):
    if ctx.message.author.id != 143168505485852672:
        print('non jwp user attempted to use this')
        print(ctx.message.author.id)
        return
    else:
        print('verified user')

    input = ctx.message.content.replace("!create-mention-role", "").strip()
    if input in DiscordChannelToMentionMap["series"]:
        print("input already in dict" + input)
        return
    print(input)
    print(DiscordChannelToMentionMap)
    newRole = await ctx.guild.create_role(name=input, colour=discord.Colour.random())
    print(newRole.id)
    print(newRole.name)
    print(newRole)

    with open("DiscordChannelMentionMapFile.on_start_backup.json", "w") as outfile:
        json.dump(DiscordChannelToMentionMap, outfile)
    DiscordChannelToMentionMap["series"][newRole.name] = str(newRole.id)
    with open("DiscordChannelMentionMapFile.json", "w") as outfile:
        json.dump(DiscordChannelToMentionMap, outfile, indent=4)

    print("role created")

@bot.command(name="print-record")
async def print_record(ctx):
    input = ctx.message.content.replace("!print-record", "").strip()
    entry = productCatalog[input]
    
    await ctx.message.channel.send(json.dumps(entry, indent=4, sort_keys=True))
    return


@ bot.event
async def on_ready():
    global threadBlocked
    random.shuffle(PUBLISHERS)
    print(f"{bot.user.name} has connected to Discord!")
    for guild in bot.guilds:
        if guild.name in guildChannelList:
            print("[Guild]: " + guild.name)
            for channel in guild.channels:
                if channel.name in guildChannelList[guild.name]:
                    print("[Channel]: " + channel.name)
                    guildChannelList[guild.name][channel.name] = bot.get_channel(
                        channel.id
                    )
                else:
                    print("[**Unmapped Channel**]: " + channel.name)
    print("Publishers loaded:")
    for publisher in PUBLISHERS:
        print(publisher)
    if not threadBlocked:
        threadBlocked = True

        if DEBUG_MENTION_MAP:
            for series in DiscordChannelToMentionMap['series'].keys():
                await asyncio.sleep(0.3)
                await doublePrint(TEST_CHANNEL, replaceNameWithMention(
                    DiscordChannelToMentionMap, series), DiscordChannelToMentionMap)

        try:
            await doublePrint(TEST_CHANNEL, "App booting up...")
            while True:
                for category in categoryList.keys():
                    print("************************************************")
                    print("Starting category: " + category)
                    print(
                        "Publishers: [" + ", ".join(categoryList[category]) + "]")
                    print("************************************************")
                    await runApp(
                        category, categoryList[category], DiscordChannelToMentionMap
                    )

                mDict = {
                    "mismatches": 0,
                    "preorderMismatch": 0,
                    "inStockMismatch": 0,
                    "outOfStockMismatch": 0,
                    "damagedMismatch": 0,
                    "imperfectMismatch": 0,
                }

                print("************************************************")
                print("Starting InStockTradesScan")
                print("************************************************")
                await scanInStockTrades(
                    compareItemAndPublishMessage, mDict, DiscordChannelToMentionMap
                )
        finally:
            threadBlocked = False
    else:
        await doublePrint(TEST_CHANNEL, "Thread blocked!!!")


bot.run(discordSecret)
