# -*- coding: utf-8 -*-
from __future__ import unicode_literals


FORMAT_LOG = '%(asctime)s %(name)s %(message)s'
GENDER_LIST = ['','♂', '♀', '⚲']
TEAM_LIST = ['(vazio)', 'Mystic', 'Valor', 'Instinct']
ROUTE_FORMAT = 'http://maps.google.com/?q={latitude},{longitude}'
MESSAGE_CLIENT_DENIED = 'Você não está autorizado a conversar comigo. \nVocê precisará entrar no seu grupo de acesso e dar o comando /start.\nSeu código é {0}.'
NOTIFICATION_WILD_FORMAT = '🐾 #{pokemon_id} <b>{pokemon_name}</b> {gender}\nAté {disappear_time_str}{details}\n' + ROUTE_FORMAT 
NOTIFICATION_RAID_EGG_FORMAT = '🥚 <b>Level {raid_level}</b> em "{gym_name}" (abre às <b>{time_raid_start}</b>)\n'  + ROUTE_FORMAT + '{details}'
NOTIFICATION_RAID_HATCH_FORMAT = '🛡 #{raid_pokemon_id} <b>{raid_pokemon_name}</b>\n({raid_pokemon_move_1} / {raid_pokemon_move_2})\nRaid Level {raid_level} aberta em <b>"{gym_name}"</b> de {time_raid_start} até <b>{time_raid_end}</b>\nTime: {team_name}\n'  + ROUTE_FORMAT + '{details}'
NOTIFICATION_RAID_HATCH_LAZY_FORMAT = '❓ <b>Level {raid_level} aberta</b> (mapa com atraso)\nGinásio: <b>{gym_name}</b>\nDe {time_raid_start} até <b>{time_raid_end}</b>\nTime: {team_name}\n'  + ROUTE_FORMAT + '{details}'
POKEMON_THUMBNAIL_MAP_URL = 'https://maps.googleapis.com/maps/api/staticmap?zoom=15&size=500x250&maptype=roadmap&markers=icon:{icon}%7C{latitude},{longitude}&key={googlemaps_api_key}'
MULTI_POKEMON_THUMBNAIL_MAP_URL = 'https://maps.googleapis.com/maps/api/staticmap?zoom=17&size=600x550&maptype=roadmap{markers}&key={googlemaps_api_key}'
MULTI_POKEMON_MARKER = '&markers=icon:{icon}%7C{latitude},{longitude}'
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
FUNNY_OBS = [
    'Não me mande nudes.',
    'Não conte piadas de tiozão.',
    'Lave sempre suas mãos antes de digitar.',
    'Você conhece o Mario?',
    'Pokémon lendário é o Pidgey.',
    'Não tenho observação. Estou com tédio.',
    'Por onde você esteve?',
    'O Rattata rattatou com o Ralts e o Raichu.',
    'Diga com licença, obrigado e até logo para mim. Mentira. Dá trabalho entender todos esses frufrus de humanos.',
    'Sua chamada será encaminhada para caixa de mensagens e estará sujeita a cobrança após o sinal.',
]



COMMANDS_HELP = ''' 

/add <em>Magnemite</em>
Adiciona Magnemite na sua lista de monitorados.

/remove <em>Magnemite</em>
Remove Magnemite na sua lista de monitorados.

/show <em>Magnemite</em>
Mostrará todos os Magnemites disponíveis pelo mapa.

/spawns
Mostra todos os pokémon e raids que você selecionou.
'''

WELCOME_MESSAGE = '''Olá, {name}
Eis exemplos de comandos possíveis:
{cmds}
Você pode pedir o rastreio de um pokémon específico escrevendo, por exemplo, estas mensagens:

<code>Mostre Magnemite</code>
O mesmo que <code>/show Magnemite</code>

Caso você envie sua localização, será exibido um mapa com os pokémon ao redor.

Caso você envie ma imagem, não faço nada (mas se for uma foto de uma robô linda, ok).

Caso você envie um vídeo, eu te pergunto: pra quê?

 '''

WELCOME_MESSAGE_GROUP = '''Olá, {name}
Você poderá conversar comigo clicando aqui: @{botname}

Obs.: {funny_obs}

'''

RARE_LIST = [
        65,68,89,91,94,103,112,113,130,134,135,
        136,137,141,142,143,147,148,149,
        176,179,180,181,196,197,199,201,
        203,213,225,227,230,232,233,235,
        237,241,242,246,247,248,
        254,257,259,260,272,278,279,282,
        288,289,306,319,321,329,330,341,342,
        372,373,374,375,376                                
 ]

DONT_KNOW_LIST = [
    'Não sei do que você está falando',
    'Eu não faço ideia do que seja isso que você escreveu.',
    'Nem sei o que é isso.',
    'Sei lá, não entendi.',
    'É melhor escrever direito pois não entendi.',
    'O que você escreveu deve ter algo de errado que não está certo.',
    'Eu acho que não sei. Deve ser porque não entendi.',
    'Atchimmmmnnnãoentendi!!!!',
    'Ai donti uanderstande (sotaque ingrichi britichi).',
    'Temos mais um caso de erro de digitação ou de uma conversa estranha com um robô.',
]

MESSAGE_HI_LIST = ['OI', 'OLÁ', 'OLA',]
MESSAGE_HI_RESPONSE_LIST = ['Olá. Sou só um robô. Não sei conversar direito.']

POKEMON_LIST = [
        "",
       "Bulbasaur",
       "Ivysaur",
       "Venusaur",
       "Charmander",
       "Charmeleon",
       "Charizard",
       "Squirtle",
       "Wartortle",
       "Blastoise",
       "Caterpie",
       "Metapod",
       "Butterfree",
       "Weedle",
       "Kakuna",
       "Beedrill",
       "Pidgey",
       "Pidgeotto",
       "Pidgeot",
       "Rattata",
       "Raticate",
       "Spearow",
       "Fearow",
       "Ekans",
       "Arbok",
       "Pikachu",
       "Raichu",
       "Sandshrew",
       "Sandslash",
       "Nidoran♀",
       "Nidorina",
       "Nidoqueen",
       "Nidoran♂",
       "Nidorino",
       "Nidoking",
       "Clefairy",
       "Clefable",
       "Vulpix",
       "Ninetales",
       "Jigglypuff",
       "Wigglytuff",
       "Zubat",
       "Golbat",
       "Oddish",
       "Gloom",
       "Vileplume",
       "Paras",
       "Parasect",
       "Venonat",
       "Venomoth",
       "Diglett",
       "Dugtrio",
       "Meowth",
       "Persian",
       "Psyduck",
       "Golduck",
       "Mankey",
       "Primeape",
       "Growlithe",
       "Arcanine",
       "Poliwag",
       "Poliwhirl",
       "Poliwrath",
       "Abra",
       "Kadabra",
       "Alakazam",
       "Machop",
       "Machoke",
       "Machamp",
       "Bellsprout",
       "Weepinbell",
       "Victreebel",
       "Tentacool",
       "Tentacruel",
       "Geodude",
       "Graveler",
       "Golem",
       "Ponyta",
       "Rapidash",
       "Slowpoke",
       "Slowbro",
       "Magnemite",
       "Magneton",
       "Farfetch’d",
       "Doduo",
        "Dodrio",
       "Seel",
       "Dewgong",
       "Grimer",
       "Muk",
       "Shellder",
       "Cloyster",
       "Gastly",
       "Haunter",
       "Gengar",
       "Onix",
       "Drowzee",
       "Hypno",
       "Krabby",
       "Kingler",
       "Voltorb",
       "Electrode",
       "Exeggcute",
       "Exeggutor",
       "Cubone",
       "Marowak",
       "Hitmonlee",
       "Hitmonchan",
       "Lickitung",
       "Koffing",
       "Weezing",
       "Rhyhorn",
       "Rhydon",
       "Chansey",
       "Tangela",
       "Kangaskhan",
       "Horsea",
       "Seadra",
       "Goldeen",
       "Seaking",
       "Staryu",
       "Starmie",
       "Mr. Mime",
       "Scyther",
       "Jynx",
       "Electabuzz",
       "Magmar",
       "Pinsir",
       "Tauros",
       "Magikarp",
       "Gyarados",
       "Lapras",
       "Ditto",
       "Eevee",
       "Vaporeon",
       "Jolteon",
       "Flareon",
       "Porygon",
       "Omanyte",
       "Omastar",
       "Kabuto",
       "Kabutops",
       "Aerodactyl",
       "Snorlax",
       "Articuno",
       "Zapdos",
       "Moltres",
       "Dratini",
       "Dragonair",
       "Dragonite",
       "Mewtwo",
       "Mew",
       "Chikorita",
       "Bayleef",
       "Meganium",
       "Cyndaquil",
       "Quilava",
       "Typhlosion",
       "Totodile",
       "Croconaw",
       "Feraligatr",
       "Sentret",
       "Furret",
       "Hoothoot",
       "Noctowl",
       "Ledyba",
       "Ledian",
       "Spinarak",
       "Ariados",
       "Crobat",
       "Chinchou",
       "Lanturn",
       "Pichu",
       "Cleffa",
       "Igglybuff",
       "Togepi",
       "Togetic",
       "Natu",
       "Xatu",
       "Mareep",
       "Flaaffy",
       "Ampharos",
       "Bellossom",
       "Marill",
       "Azumarill",
       "Sudowoodo",
       "Politoed",
       "Hoppip",
       "Skiploom",
       "Jumpluff",
       "Aipom",
       "Sunkern",
       "Sunflora",
       "Yanma",
       "Wooper",
       "Quagsire",
       "Espeon",
       "Umbreon",
       "Murkrow",
       "Slowking",
       "Misdreavus",
       "Unown",
       "Wobbuffet",
       "Girafarig",
       "Pineco",
       "Forretress",
       "Dunsparce",
       "Gligar",
       "Steelix",
       "Snubbull",
       "Granbull",
       "Qwilfish",
       "Scizor",
       "Shuckle",
       "Heracross",
       "Sneasel",
       "Teddiursa",
       "Ursaring",
       "Slugma",
       "Magcargo",
       "Swinub",
       "Piloswine",
       "Corsola",
       "Remoraid",
       "Octillery",
       "Delibird",
       "Mantine",
       "Skarmory",
       "Houndour",
       "Houndoom",
       "Kingdra",
       "Phanpy",
       "Donphan",
       "Porygon2",
       "Stantler",
       "Smeargle",
       "Tyrogue",
       "Hitmontop",
       "Smoochum",
       "Elekid",
       "Magby",
       "Miltank",
       "Blissey",
       "Raikou",
       "Entei",
       "Suicune",
       "Larvitar",
       "Pupitar",
       "Tyranitar",
       "Lugia",
       "Ho-Oh",
       "Celebi",
       "Treecko",
       "Grovyle",
       "Sceptile",
       "Torchic",
       "Combusken",
       "Blaziken",
       "Mudkip",
       "Marshtomp",
       "Swampert",
       "Poochyena",
       "Mightyena",
       "Zigzagoon",
       "Linoone",
       "Wurmple",
       "Silcoon",
       "Beautifly",
       "Cascoon",
       "Dustox",
       "Lotad",
       "Lombre",
       "Ludicolo",
       "Seedot",
       "Nuzleaf",
       "Shiftry",
       "Taillow",
       "Swellow",
       "Wingull",
       "Pelipper",
       "Ralts",
       "Kirlia",
       "Gardevoir",
       "Surskit",
       "Masquerain",
       "Shroomish",
       "Breloom",
       "Slakoth",
       "Vigoroth",
       "Slaking",
       "Nincada",
       "Ninjask",
       "Shedinja",
       "Whismur",
       "Loudred",
       "Exploud",
       "Makuhita",
       "Hariyama",
       "Azurill",
       "Nosepass",
       "Skitty",
       "Delcatty",
       "Sableye",
       "Mawile",
       "Aron",
       "Lairon",
       "Aggron",
       "Meditite",
       "Medicham",
       "Electrike",
       "Manectric",
       "Plusle",
       "Minun",
       "Volbeat",
       "Illumise",
       "Roselia",
       "Gulpin",
       "Swalot",
       "Carvanha",
       "Sharpedo",
       "Wailmer",
       "Wailord",
       "Numel",
       "Camerupt",
       "Torkoal",
       "Spoink",
       "Grumpig",
       "Spinda",
       "Trapinch",
       "Vibrava",
       "Flygon",
       "Cacnea",
       "Cacturne",
       "Swablu",
       "Altaria",
       "Zangoose",
       "Seviper",
       "Lunatone",
       "Solrock",
       "Barboach",
       "Whiscash",
       "Corphish",
       "Crawdaunt",
       "Baltoy",
       "Claydol",
       "Lileep",
       "Cradily",
       "Anorith",
       "Armaldo",
       "Feebas",
       "Milotic",
       "Castform",
       "Kecleon",
       "Shuppet",
       "Banette",
       "Duskull",
       "Dusclops",
       "Tropius",
       "Chimecho",
       "Absol",
       "Wynaut",
       "Snorunt",
       "Glalie",
       "Spheal",
       "Sealeo",
       "Walrein",
       "Clamperl",
       "Huntail",
       "Gorebyss",
       "Relicanth",
       "Luvdisc",
       "Bagon",
       "Shelgon",
       "Salamence",
       "Beldum",
       "Metang",
       "Metagross",
       "Regirock",
       "Regice",
       "Registeel",
       "Latias",
       "Latios",
       "Kyogre",
       "Groudon",
       "Rayquaza",
       "Jirachi",
       "Deoxys",
       "Turtwig",
       "Grotle",
       "Torterra",
       "Chimchar",
       "Monferno",
       "Infernape",
       "Piplup",
       "Prinplup",
       "Empoleon",
       "Starly",
       "Staravia",
       "Staraptor",
       "Bidoof",
       "Bibarel",
       "Kricketot",
       "Kricketune",
       "Shinx",
       "Luxio",
       "Luxray",
       "Budew",
       "Roserade",
       "Cranidos",
       "Rampardos",
       "Shieldon",
       "Bastiodon",
       "Burmy",
       "Wormadam",
       "Mothim",
       "Combee",
       "Vespiquen",
       "Pachirisu",
       "Buizel",
       "Floatzel",
       "Cherubi",
       "Cherrim",
       "Shellos",
       "Gastrodon",
       "Ambipom",
       "Drifloon",
       "Drifblim",
       "Buneary",
       "Lopunny",
       "Mismagius",
       "Honchkrow",
       "Glameow",
       "Purugly",
       "Chingling",
       "Stunky",
       "Skuntank",
       "Bronzor",
       "Bronzong",
       "Bonsly",
       "Mime Jr.",
       "Happiny",
       "Chatot",
       "Spiritomb",
       "Gible",
       "Gabite",
       "Garchomp",
       "Munchlax",
       "Riolu",
       "Lucario",
       "Hippopotas",
       "Hippowdon",
       "Skorupi",
       "Drapion",
       "Croagunk",
       "Toxicroak",
       "Carnivine",
       "Finneon",
       "Lumineon",
       "Mantyke",
       "Snover",
       "Abomasnow",
       "Weavile",
       "Magnezone",
       "Lickilicky",
       "Rhyperior",
       "Tangrowth",
       "Electivire",
       "Magmortar",
       "Togekiss",
       "Yanmega",
       "Leafeon",
       "Glaceon",
       "Gliscor",
       "Mamoswine",
       "Porygon-Z",
       "Gallade",
       "Probopass",
       "Dusknoir",
       "Froslass",
       "Rotom",
       "Uxie",
       "Mesprit",
       "Azelf",
       "Dialga",
       "Palkia",
       "Heatran",
       "Regigigas",
       "Giratina",
       "Cresselia",
       "Phione",
       "Manaphy",
       "Darkrai",
       "Shaymin",
       "Arceus",
       "Victini",
       "Snivy",
       "Servine",
       "Serperior",
       "Tepig",
       "Pignite",
       "Emboar",
       "Oshawott",
       "Dewott",
       "Samurott",
       "Patrat",
       "Watchog",
       "Lillipup",
       "Herdier",
       "Stoutland",
       "Purrloin",
       "Liepard",
       "Pansage",
       "Simisage",
       "Pansear",
       "Simisear",
       "Panpour",
       "Simipour",
       "Munna",
       "Musharna",
       "Pidove",
       "Tranquill",
       "Unfezant",
       "Blitzle",
       "Zebstrika",
       "Roggenrola",
       "Boldore",
       "Gigalith",
       "Woobat",
       "Swoobat",
       "Drilbur",
       "Excadrill",
       "Audino",
       "Timburr",
       "Gurdurr",
       "Conkeldurr",
       "Tympole",
       "Palpitoad",
       "Seismitoad",
       "Throh",
       "Sawk",
       "Sewaddle",
       "Swadloon",
       "Leavanny",
       "Venipede",
       "Whirlipede",
       "Scolipede",
       "Cottonee",
       "Whimsicott",
       "Petilil",
       "Lilligant",
       "Basculin",
       "Sandile",
       "Krokorok",
       "Krookodile",
       "Darumaka",
       "Darmanitan",
       "Maractus",
       "Dwebble",
       "Crustle",
       "Scraggy",
       "Scrafty",
       "Sigilyph",
       "Yamask",
       "Cofagrigus",
       "Tirtouga",
       "Carracosta",
       "Archen",
       "Archeops",
       "Trubbish",
       "Garbodor",
       "Zorua",
       "Zoroark",
       "Minccino",
       "Cinccino",
       "Gothita",
       "Gothorita",
       "Gothitelle",
       "Solosis",
       "Duosion",
       "Reuniclus",
       "Ducklett",
       "Swanna",
       "Vanillite",
       "Vanillish",
       "Vanilluxe",
       "Deerling",
       "Sawsbuck",
       "Emolga",
       "Karrablast",
       "Escavalier",
       "Foongus",
       "Amoonguss",
       "Frillish",
       "Jellicent",
       "Alomomola",
       "Joltik",
       "Galvantula",
       "Ferroseed",
       "Ferrothorn",
       "Klink",
       "Klang",
       "Klinklang",
       "Tynamo",
       "Eelektrik",
       "Eelektross",
       "Elgyem",
       "Beheeyem",
       "Litwick",
       "Lampent",
       "Chandelure",
       "Axew",
       "Fraxure",
       "Haxorus",
       "Cubchoo",
       "Beartic",
       "Cryogonal",
       "Shelmet",
       "Accelgor",
       "Stunfisk",
       "Mienfoo",
       "Mienshao",
       "Druddigon",
       "Golett",
       "Golurk",
       "Pawniard",
       "Bisharp",
       "Bouffalant",
       "Rufflet",
       "Braviary",
       "Vullaby",
       "Mandibuzz",
       "Heatmor",
       "Durant",
       "Deino",
       "Zweilous",
       "Hydreigon",
       "Larvesta",
       "Volcarona",
       "Cobalion",
       "Terrakion",
       "Virizion",
       "Tornadus",
       "Thundurus",
       "Reshiram",
       "Zekrom ",
       "Landorus",
       "Kyurem",
       "Keldeo",
       "Meloetta",
       "Genesect",
       "Chespin",
       "Quilladin",
       "Chesnaught",
       "Fennekin",
       "Braixen",
       "Delphox",
       "Froakie",
       "Frogadier",
       "Greninja",
       "Bunnelby",
       "Diggersby",
       "Fletchling",
       "Fletchinder",
       "Talonflame",
       "Scatterbug",
       "Spewpa",
       "Vivillon",
       "Litleo",
       "Pyroar",
       "Flabebe",
       "Floette",
       "Florges",
       "Skiddo",
       "Gogoat",
       "Pancham",
       "Pangoro",
       "Furfrou",
       "Espurr",
       "Meowstic",
       "Honedge",
       "Doublade",
       "Aegislash",
       "Spritzee",
       "Aromatisse",
       "Swirlix",
       "Slurpuff",
       "Inkay",
       "Malamar",
       "Binacle",
       "Barbaracle",
       "Skrelp",
       "Dragalge",
       "Clauncher",
       "Clawitzer",
       "Helioptile",
       "Heliolisk",
       "Tyrunt",
       "Tyrantrum",
       "Amaura",
       "Aurorus",
       "Sylveon",
       "Hawlucha",
       "Dedenne",
       "Carbink",
       "Goomy",
       "Sliggoo",
       "Goodra",
       "Klefki",
       "Phantump",
       "Trevenant",
       "Pumpkaboo",
       "Gourgeist",
       "Bergmite",
       "Avalugg",
       "Noibat",
       "Noivern",
       "Xerneas",
       "Yveltal",
       "Zygarde",
       "Diancie",
       "Hoopa",
       "Volcanion",
       "Rowlet",
       "Dartrix",
       "Decidueye",
       "Litten",
       "Torracat",
       "Incineroar",
       "Popplio",
       "Brionne",
       "Primarina",
       "Pikipek",
       "Trumbeak",
       "Toucannon",
       "Yungoos",
       "Gumshoos",
       "Grubbin",
       "Charjabug",
       "Vikavolt",
       "Crabrawler",
       "Crabominable",
       "Oricorio",
       "Cutiefly",
       "Ribombee",
       "Rockruff",
       "Lycanroc",
       "Wishiwashi",
       "Mareanie",
       "Toxapex",
       "Mudbray",
       "Mudsdale",
       "Dewpider",
       "Araquanid",
       "Fomantis",
       "Lurantis",
       "Morelull",
       "Shiinotic",
       "Salandit",
       "Salazzle",
       "Stufful",
       "Bewear",
       "Bounsweet",
       "Steenee",
       "Tsareena",
       "Comfey",
       "Oranguru",
       "Passimian",
       "Wimpod",
       "Golisopod",
       "Sandygast",
       "Palossand",
       "Pyukumuku",
       "Type: Null",
       "Silvally",
       "Minior",
       "Komala",
       "Turtonator",
       "Togedemaru",
       "Mimikyu",
       "Bruxish",
       "Drampa",
       "Dhelmise",
       "Jangmo-o",
       "Hakamo-o",
       "Kommo-o",
       "Tapu Koko",
       "Tapu Lele",
       "Tapu Bulu",
       "Tapu Fini",
       "Cosmog",
       "Cosmoem",
       "Solgaleo",
       "Lunala",
       "Nihilego",
       "Buzzwole",
       "Pheromosa",
       "Xurkitree",
       "Celesteela",
       "Kartana",
       "Guzzlord",
       "Necrozma",
       "Magearna",
       "Marshadow"
]    