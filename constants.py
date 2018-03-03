# -*- coding: utf-8 -*-
from __future__ import unicode_literals


FORMAT_LOG = '%(asctime)s %(name)s %(message)s'
GENDER_LIST = ['','♂', '♀', '⚲']
TEAM_LIST = ['(vazio)', 'Mystic', 'Valor', 'Instinct']
ROUTE_FORMAT = 'http://maps.google.com/?q={latitude},{longitude}'
MESSAGE_CLIENT_DENIED = 'Você não está autorizado a conversar comigo. Seu código é {chat_id}.'
NOTIFICATION_WILD_FORMAT = '#{pokemon_id} {pokemon_name} {gender}\nAté {disappear_time_str}{details}\n\n' + ROUTE_FORMAT 
NOTIFICATION_RAID_EGG_FORMAT = 'Raid Level {raid_level} em "{gym_name}" (abre às {time_raid_start})\nTime: {team_name}\n\n'  + ROUTE_FORMAT + '{details}'
NOTIFICATION_RAID_HATCH_FORMAT = '#{raid_pokemon_id} {raid_pokemon_name}\nRaid Level {raid_level} aberta em "{gym_name}" até {time_raid_end}\nMovimentos:\n - {raid_pokemon_move_1}\n - {raid_pokemon_move_2}\nTime: {team_name}\n\n'  + ROUTE_FORMAT + '{details}'
NOTIFICATION_RAID_HATCH_LAZY_FORMAT = 'Raid Level {raid_level} aberta; mapa com atraso\nGinásio: {gym_name}\nDe {time_raid_start} até {time_raid_end}\nTime: {team_name}\n\n'  + ROUTE_FORMAT + '{details}'
POKEMON_THUMBNAIL_MAP_URL = 'https://maps.googleapis.com/maps/api/staticmap?zoom=15&size=500x250&maptype=roadmap&markers=icon:{icon}%7C{latitude},{longitude}&key={googlemaps_api_key}'
POKEMON_ICON = 'https://veekun.com/dex/media/pokemon/icons/{pokemon_id}.png'
RAID_HATCH_ICON = 'https://veekun.com/dex/media/pokemon/icons/{pokemon_id}.png'
RAID_EGG_ICONS = [
    '',
    'https://vignette.wikia.nocookie.net/pokemongo/images/5/5a/Egg_Raid_Normal.png/revision/latest/scale-to-width-down/64?cb=20170620230659',
    'https://vignette.wikia.nocookie.net/pokemongo/images/5/5a/Egg_Raid_Normal.png/revision/latest/scale-to-width-down/64?cb=20170620230659',
    'https://vignette.wikia.nocookie.net/pokemongo/images/e/e3/Egg_Raid_Rare.png/revision/latest/scale-to-width-down/64?cb=20170620230126',
    'https://vignette.wikia.nocookie.net/pokemongo/images/e/e3/Egg_Raid_Rare.png/revision/latest/scale-to-width-down/64?cb=20170620230126',
    'https://vignette.wikia.nocookie.net/pokemongo/images/c/cd/Egg_Raid_Legendary.png/revision/latest/scale-to-width-down/64?cb=20170620230139',
]
RAID_HATCH_ICON_LIST = {
    "382": "https://vignette.wikia.nocookie.net/pokemongo/images/f/f3/Kyogre.png/revision/latest/scale-to-width-down/64",
    "383": "https://vignette.wikia.nocookie.net/pokemongo/images/d/d5/Groudon.png/revision/latest/scale-to-width-down/64",
    "384": "https://vignette.wikia.nocookie.net/pokemongo/images/6/66/Rayquaza.png/revision/latest/scale-to-width-down/64",
}
