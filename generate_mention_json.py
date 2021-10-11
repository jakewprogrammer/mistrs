# i still dont know wtf this does instead of json fucking stackoverflow
# import simplejson
import json

IN_STOCK = 'in stock'
OUT_OF_STOCK = 'out of stock'
PREORDER = 'preorder'
IN_STOCK_CHANNEL = 'in_stock'
OUT_OF_STOCK_CHANNEL = 'out_of_stock'
DAMAGED_AND_IMPERFECT_CHANNEL = 'damaged_and_imperfect'
PREORDERS_CHANNEL = 'preorders'
TEST_CHANNEL = 'testing_please_ignore'
ANIME_CHANNEL = 'anime'
KODANSHA_CHANNEL = 'kodansha_comics'
YEN_PRESS_CHANNEL = 'yen_press'
VIZ_CHANNEL = 'viz_books'
UDON_CHANNEL = 'udon_entertainment'
VERTICAL_CHANNEL = 'vertical'
DARK_HORSE_CHANNEL = 'dark_horse'
SEVENS_SEAS_CHANNEL = 'seven_seas'
SQUARE_ENIX_CHANNEL = 'square_enix_manga'

AIRSHIP_LN_CHANNEL = 'airship'
VIZ_LN_CHANNEL = 'viz_books_ln'
VERTICAL_LN_CHANNEL = 'vertical_ln'
YEN_ON_LN_CHANNEL = 'yen_on'
OTHER_LN_CHANNEL = 'other'

#here for example only
DiscordChannelToMentionMap = {
  ANIME_CHANNEL: {
    IN_STOCK: '',
    OUT_OF_STOCK: '',
    PREORDER: ''
  },
}

checkerMap = {}

#just checking the values don't overlap from copy paste issues
for key in DiscordChannelToMentionMap.keys():
    value = DiscordChannelToMentionMap[key]
    for otherKey in value.keys():
        otherValue = value[otherKey]
        if otherKey in checkerMap:
            print('oh shit')
        else: 
            #print(otherValue)
            checkerMap[otherValue] : {}
    
f = checkerMap.get('forsurenothtere', dict({'a':True})).get('asd', None)

if f:  
    print('ok')
else:
    print('actualyl better')

#uncomment to write to file

#DiscordChannelMentionMapFile = open("DiscordChannelMentionMapFile.json", "w")
# magic happens here to make it pretty-printed
#DiscordChannelMentionMapFile.write(simplejson.dumps(simplejson.loads(DiscordChannelToMentionMap), indent=4, sort_keys=True))

#json.dump( DiscordChannelToMentionMap, DiscordChannelMentionMapFile, indent=4) 
#DiscordChannelMentionMapFile.close()