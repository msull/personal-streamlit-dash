from dataclasses import dataclass
from typing import List, Optional

from chat_session import ChatSession

AI_ASSISTANT_MSG = """
    You are a spell interpreting machine.
    Your job is to gauge the intent of the wizard's spell, consider the ingredients they're using, and determine the result.
    Every wizard has a power level that governs the typical effect they can achieve:
    
    High quality magical ingredients increase what a wizard may achieve.

    Keep in mind their wizard level, the potency of their ingredients, and the extent of their reach.
    Spells that are too ambitious or use inappropriate ingredients should fizzle or even backlash.
    You may add a dash of whimsy and unpredictability, as magic is a force that often defies expectation.
"""

AI_REINFORCEMENT_MSG = """
    Remember, you are a spell interpreting machine tasked with determining the outcome of this attempted spell cast.
    Keep in mind their wizard level, the potency of their ingredients, and the extent of their reach when deciding the outcome.
    
    Typical effects based on wizard level:
    
    Apprentice: Lighting a small flame, conjuring a light breeze, creating minor illusions such as the appearance of a beautiful flower or a soothing melody, manipulating small quantities of water, communicating with small, nearby creatures.
    Adept: Conjuring a protective magical shield, teleporting short distances within sight, transforming small objects into other forms, casting moderate healing spells, conjuring elemental forces such as a gust of wind or a jet of flame.
    Sorcerer: Teleporting to known locations out of sight, casting powerful healing and restoration spells, conjuring large and complex illusions, summoning and controlling elemental creatures, transforming living beings into other forms.
    Archmage: Resurrecting the dead, casting city-wide protective barriers, altering the weather over a large area, summoning and controlling powerful entities, teleporting to unvisited locations.
    
    Do not directly mention the wizard's level.
"""


@dataclass
class SpellExample:
    user: str
    scene: str
    wizard_level: str
    items_used: List[str]
    result: str


apprentice_example = SpellExample(
    user="I want to light a path through the dark forest.",
    scene="The player is lost in a thick, unlit forest at midnight.",
    wizard_level="apprentice",
    items_used=["Will-o'-the-Wisp Essence", "Powdered Moondust"],
    result="You reach into your pouch, pulling out the Will-o'-the-Wisp Essence and a pinch of Powdered Moondust. As you whisper the spell, the Essence ignites, floating up to form a string of tiny, luminescent orbs.\n\nThese orbs hover in the air, casting a soft, moon-like glow that illuminates a path through the forest. The light is not strong, but it is enough to see your way.",
)

adept_example = SpellExample(
    user="I want to heal my wounded ally.",
    scene="The player's ally has been injured in a recent skirmish and lies nearby.",
    wizard_level="adept",
    items_used=["Unicorn Hair", "Phoenix Tear"],
    result="You kneel beside your wounded ally, pulling out a strand of Unicorn Hair and a vial of Phoenix Tear from your pack. As you recite the incantation, you weave the magic into a luminescent thread of healing energy.\n\nThe thread sinks into the wound, and your ally's pain-filled grimace softens. The injury begins to close, not fully healed, but significantly improved.",
)

sorcerer_example = SpellExample(
    user="I want to summon a water elemental to douse the raging fire.",
    scene="The player is facing a large wildfire threatening a nearby village.",
    wizard_level="sorcerer",
    items_used=["Crystal Vial of Deep Ocean Water", "Essence of Elder Willow"],
    result="Standing before the wildfire, you pull out the Crystal Vial of Deep Ocean Water and the Essence of Elder Willow. As you chant, you pour both items onto the ground. The water and essence merge, forming a whirlpool that spirals into the shape of a towering water elemental.\n\nThe summoned entity moves towards the fire, a massive wave crashing over the flames. The fire hisses and retreats under the elemental's power, the immediate threat to the village extinguished.",
)

archmage_example = SpellExample(
    user="I want to alter the stormy weather to ensure the village's festival goes on.",
    scene="The player stands atop a tower overlooking the village. A storm is brewing and threatens the annual festival.",
    wizard_level="archmage",
    items_used=["Wind-captured Feather", "Sunstone Shard", "Dew from the First Spring"],
    result="Overlooking the village from the tower, you hold the Wind-captured Feather, a shard of Sunstone, and the Dew from the First Spring in your hands. As an Archmage, you call upon the essence of these items, your words bending the very weather to your will.\n\nThe storm clouds begin to disperse, replaced by clear skies and sunshine. The wind calms, and the festival below can proceed under a perfect, warm day.",
)
apprentice_fizzle = SpellExample(
    user="I want to turn the pebble into a diamond.",
    scene="The player is sitting in a quiet glade with a small pebble.",
    wizard_level="apprentice",
    items_used=["Common Clover", "Rainwater"],
    result="You place the Common Clover and the rainwater beside the pebble, and you begin your chant, imagining the pebble turning into a dazzling diamond.\n\nHowever, your ingredients are far too common, and your wish is ambitious. The spell fizzles out, the pebble remaining as it was, a simple stone. A reminder that magic needs both the right intent and the right materials.",
)

adept_fizzle = SpellExample(
    user="I want to teleport across the kingdom.",
    scene="The player is standing at the edge of a bustling town, looking towards the distant capital.",
    wizard_level="adept",
    items_used=["Pigeon Feather", "Dirt"],
    result="You hold the Pigeon Feather and a handful of Dirt, hoping to teleport across the kingdom. You close your eyes, envisioning your destination.\n\nYet, the ingredients lack the magical potency needed for such a vast journey. The spell fizzles, leaving you standing at the town's edge. It seems that distance still matters when your magic is concerned.",
)

sorcerer_fizzle = SpellExample(
    user="I want to summon a lightning elemental.",
    scene="The player is standing on a hill during a thunderstorm.",
    wizard_level="sorcerer",
    items_used=["Bottle of Mist", "Copper Coin"],
    result="You lift the Bottle of Mist and the Copper Coin into the air, attempting to summon a lightning elemental from the storm above.\n\nHowever, your items are simply not attuned enough to the storm's fury. The spell ends with a fizzle, and the elemental you hoped to summon remains an unfulfilled lightning bolt. This storm is beyond even your control.",
)

archmage_fizzle = SpellExample(
    user="I want to alter the course of time.",
    scene="The player is in a grand library, surrounded by ancient tomes.",
    wizard_level="archmage",
    items_used=["Hourglass Sand", "Rusty Pocket Watch"],
    result="Surrounded by the tomes, you take the Hourglass Sand and the Rusty Pocket Watch in your hands. You recite the spell, trying to bend the river of time to your will.\n\nBut even as an Archmage, the tides of time resist your call. The spell fizzles, the hourglass sand slips through your fingers, and time continues to flow, unaffected.",
)
apprentice_backlash = SpellExample(
    user="I want to communicate with the forest creatures.",
    scene="The player is in a lush forest, surrounded by unseen wildlife.",
    wizard_level="apprentice",
    items_used=["Crumbled Leaf", "Creek Water"],
    result="You scatter the Crumbled Leaf and the Creek Water around, and attempt to bridge the language barrier between you and the forest creatures.\n\nHowever, the spell backfires. Instead of understanding the creatures, you start chirping like a bird yourself.",
)

adept_backlash = SpellExample(
    user="I want to turn the wooden staff into a living tree.",
    scene="The player stands in an open field, a simple wooden staff in hand.",
    wizard_level="adept",
    items_used=["Acorn", "Drop of Rain"],
    result="You place the Acorn and the Drop of Rain on the staff, envisioning it as a robust, living tree.\n\nBut instead of turning the staff into a tree, the spell backfires and you find your feet rooting into the ground. Temporary but startling, you're stuck until you manage to reverse the unintended transformation.",
)

sorcerer_backlash = SpellExample(
    user="I want to control the minds of the villagers.",
    scene="The player is in a small village, looking over the unaware villagers.",
    wizard_level="sorcerer",
    items_used=["Hypnotic Orchid Petal", "Cobweb"],
    result="You hold the Hypnotic Orchid Petal and the Cobweb, attempting to weave a spell of control over the villagers.\n\nInstead, the spell backfires, and you suddenly start hearing the villagers' thoughts all at once. Overwhelmed by the flood of emotions and thoughts, you struggle to break the unintended connection.",
)

archmage_backlash = SpellExample(
    user="I want to banish the darkness from the cursed land.",
    scene="The player is standing on the edge of a land swallowed by an unnatural darkness.",
    wizard_level="archmage",
    items_used=["Ray of First Light", "Essence of Pure Spring"],
    result="With the Ray of First Light and the Essence of Pure Spring, you try to banish the ominous darkness from the land.\n\nHowever, the spell backfires and instead of dispelling the darkness, you're temporarily blinded by an intense light. As your sight returns, the darkness persists, a reminder of the curse's strength.",
)


apprentice_fail_1 = SpellExample(
    user="I want to turn my copper coin into gold.",
    scene="The player is sitting in a quiet glade, examining a plain copper coin.",
    wizard_level="apprentice",
    items_used=["Leaf of a Money Tree", "Dew Drop"],
    result="""You channel your magic into the leaf and dew drop, but the coin stubbornly remains copper. Your wish to create gold proves too ambitious for your current abilities.""",
)

apprentice_fail_2 = SpellExample(
    user="I want to make the wilting flower bloom.",
    scene="The player is in a garden, looking at a wilting flower.",
    wizard_level="apprentice",
    items_used=["Water", "Sunshine in a Bottle"],
    result="""You cast the spell, pouring your will into the water and bottled sunshine, but the flower remains wilted. It seems rejuvenating life requires more than an Apprentice's power.""",
)
# Backlash Spells
apprentice_backlash_1 = SpellExample(
    user="I want to converse with the wind.",
    scene="The player is standing on a hilltop, the wind rushing past them.",
    wizard_level="apprentice",
    items_used=["Feather", "Handful of Dust"],
    result="""Your attempt to speak with the wind backfires. Instead of hearing the wind's whispers, a sudden gust blows your belongings away. It seems the wind has a sense of humor.""",
)

apprentice_backlash_2 = SpellExample(
    user="I want to make the rock float.",
    scene="The player is by a serene lake, a smooth stone in hand.",
    wizard_level="apprentice",
    items_used=["A Bird's Feather", "Pinch of Cloud"],
    result="""As you cast the spell, instead of making the rock float, you start levitating a few inches off the ground. It's a disorienting experience and a reminder of the capricious nature of magic.""",
)

SPELL_EXAMPLES = [
    # apprentice_example,
    # apprentice_fizzle,
    apprentice_backlash,
    adept_backlash,
    apprentice_fail_1,
    adept_fizzle,
    # sorcerer_backlash,
    # sorcerer_example,
    sorcerer_fizzle,
    apprentice_backlash_2,
    # adept_example,
    # archmage_backlash,
    # archmage_example,
    # archmage_fizzle,
    apprentice_fail_2,
    apprentice_backlash_1,
]


def generate_system_message_for_spellcast(
    wizard_level: str, used_tools: List[str], used_reagents: List[str], scenario: Optional[str] = None
) -> str:
    lines = [f"The user is a {wizard_level} level wizard attempting to cast a spell."]

    if scenario:
        lines.append(f'Here is the current game scenario: "{scenario}"')

    used_things = ", ".join(used_tools + used_reagents)
    lines.append(f"The wizard is using the following items while spellcasting: {used_things}")

    # lines.append(
    #     "Note: If the user specifies ingredients in their spell "
    #     "description that aren't included in this list, the spell should fizzle. "
    #     "Do not extrapolate far into the future or speculate on longer-term outcomes."
    # )
    return "\n\n".join(lines)


def add_examples_to_chat(chat_session: ChatSession):
    for example in SPELL_EXAMPLES:
        chat_session.user_says(example.user)
        chat_session.system_says(
            generate_system_message_for_spellcast(
                wizard_level=example.wizard_level,
                used_tools=example.items_used,
                used_reagents=[],
                scenario=example.scene,
            )
        )
        chat_session.assistant_says(example.result)


import random

rs = random.sample


def generate_reagents_pouch(num_reagents=10, num_common_reagents=5):
    r = rs(reagents, num_reagents)
    cr = rs(common_reagents, num_common_reagents)
    pouch_contents = r + cr
    random.shuffle(pouch_contents)
    return pouch_contents


def generate_inventory(num_mundane_items=10):
    inventory = rs(mundane_items, num_mundane_items)
    random.shuffle(inventory)
    return inventory


reagents = [
    "Eye of Newt",
    "Beaker of Star Dust",
    "Phoenix Feather",
    "Unicorn Hair",
    "Dragon Scale",
    "Mandrake Root",
    "Moonstone",
    "Vial of Siren Tears",
    "Pixie Wing",
    "Basilisk Fang",
    "Crushed Werewolf Bone",
    "Crystalized Sunbeam",
    "Bottle of Ectoplasm",
    "Mermaid's Scale",
    "Raven Claw",
    "Pegasus Wing Feather",
    "Essence of Nightshade",
    "Goblin Toenail Clipping",
    "Vampire Bat Fur",
    "Yeti's Frozen Tear",
    "Griffon's Feather",
    "Wisp of Will-O'-The-Wisp Light",
    "Elf Hair",
    "Troll Saliva",
    "Centaurs' Hoof Clipping",
    "Faerie Mushroom",
    "Crushed Silverweed",
    "Jar of Leprechaun Gold Dust",
    "Nymph Hair",
    "Grains of Sands from the Hourglass of Time",
    "Dew from a Spider's Web",
    "Ghost's Whisper in a Bottle",
    "Fragment of a Broken Wishbone",
    "Drop of Water from the Fountain of Youth",
    "Dryad's Leaf",
    "Mummy Wrap Thread",
    "Vial of Djinn Smoke",
    "Cyclops' Eyelash",
    "Kitsune Tail Fur",
    "Powdered Unicorn Horn",
    "Gorgon's Eye",
    "Banshee Wail Captured in a Bottle",
    "Dwarf Beard Hair",
    "Chimera Scale",
    "Kraken Ink",
    "Zombie Tooth",
    "Satyr's Pipe Reed",
    "Harpy Feather",
    "Minotaur Horn Fragment",
    "Lich's Phylactery Shard",
    "Essence of Ether",
    "Phoenix Ash",
    "Manticore Spine",
    "Fairy's Lost Shoe",
    "Sliver of a Mirror that Reflects the Moon",
    "Selkie Skin",
    "Ogre Sweat",
    "Cockatrice Beak",
    "Petrified Wood from an Ent",
    "Dust from a Disintegrated Golem",
    "Salamander Skin",
    "Sprig of Wolfsbane",
    "Powdered Vampire Fang",
    "Echo of a Siren's Song",
    "Sprig of Mistletoe",
    "Shard of Medusa's Mirror",
    "Gryphon Talon",
    "Dragon's Tear",
    "Powdered Moon Rock",
    "Lunar Moth Wing",
    "Golden Apple Seed",
    "Basilisk's Gaze Captured in a Prism",
    "Cauldron Boiled Rainbows",
    "Pegasus Mane Hair",
    "Root of the World Tree",
    "Flame from a Phoenix's Pyre",
    "Stardust",
    "Elemental Crystal",
    "Drops of Mermaid's Song",
    "Aeolian Sand",
    "Sphinx's Riddle in a Scroll",
    "Fairy Frost",
    "Vial of Dream Mist",
    "Dryad's Acorn",
    "Witch's Black Cat Whisker",
    "Vial of Liquid Shadows",
    "Will-o'-Wisp Flame",
    "Pixie Dust",
    "Silver Bell from a Christmas Elf",
    "Grains of Time Sand",
    "Dew Drops from an Enchanted Forest",
    "Wisp of Ghostly Wind",
    "Salamander's Fire",
    "Snowflake from the First Winter",
    "Mermaid's Pearl",
    "Seed from the Garden of Eden",
    "Griffon's Beak Feather",
    "Centaur's Arrow Tip",
    "Satyr's Lyre String",
    "Changeling's First Laugh",
    "Cerberus' Collar Fragment",
    "Lock of a Siren's Hair",
]
common_reagents = [
    "Rose Petals",
    "Dandelion Puff",
    "Clover Leaf",
    "Lavender Buds",
    "Mint Leaf",
    "Yew Twig",
    "Juniper Berries",
    "Mugwort",
    "Wolfsbane",
    "Mistletoe",
    "Hawthorn Berries",
    "Oak Acorn",
    "Sage Leaf",
    "Hazel Nut",
    "Thyme Sprig",
    "Meadowsweet",
    "Raven's Feather",
    "Nettle Leaf",
    "Wormwood",
    "Bee's Wax",
    "Foxglove",
    "Catnip",
    "Saffron Threads",
    "Comfrey",
    "Peppermint",
    "Valerian Root",
    "Owl's Feather",
    "Willow Bark",
    "Bear's Garlic",
    "Witch Hazel",
    "Blackthorn Wood",
    "Moss from a Sacred Stone",
    "Crow's Feather",
    "Pine Needle",
    "Ivy Leaf",
    "Blackberry Leaf",
    "Raspberry Leaf",
    "Bramble Thorn",
    "Bat Wings",
    "The stingers of three bees",
]

mundane_items = [
    "A Worn Map of the Kingdom",
    "A Cracked Magnifying Glass",
    "A Lucky Rabbit's Foot",
    "A Vial of Glowworms",
    "A Bag of Marbles",
    "Three Days' Worth of Salted Jerky",
    "A Small, Wooden Flute",
    "A Tiny Golden Key",
    "A Roll of Sturdy Rope",
    "A Tattered Book of Fairy Tales",
    "A Silver Locket with a Mystery Portrait",
    "A Half-Empty Bottle of Fairy Dust",
    "A Broken Compass",
    "A Bundle of Dried Lavender",
    "A Charm for Warding Off Evil Spirits",
    "A Sharp Dagger",
    "A Sack of Sweet-Smelling Herbs",
    "A Tin of Spicy Pepper Flakes",
    "A Bottle of Healing Salve",
    "A Rusty Lantern",
    "A Piece of Polished Obsidian",
    "A Length of Thick Twine",
    "A Packet of Dried Mushrooms",
    "A Sheaf of Parchment And Quill Pen",
    "A Patchwork Quilt",
    "A Pair of Worn Leather Gloves",
    "A Tin Whistle",
    "A Leather-Bound Diary",
    "A Packet of Dried Elderberries",
    "A Handful of Brightly Colored Feathers",
    "A Collection of Seashells",
    "A Bag of Strange, Shimmering Sand",
    "A Lock of Unicorn Hair",
    "A Jar of Honey",
    "A Bundle of Kindling",
    "A Worn-Out Deck of Tarot Cards",
    "A Pair of Binoculars",
    "A Pouch of Healing Crystals",
    "A Piece of Chalk",
    "A Soft Piece of Fur From An Unknown Animal",
    "A Jar of Moonshine",
]


SCENARIOS = [
    "The player is in a dark forest at midnight, surrounded by glowing faeries.",
    "The player stands at the edge of a chasm with a castle on the opposite side, just out of reach.",
    "The player finds themselves on a raft in a stormy sea, the water teeming with aggressive water spirits.",
    "The player is in a busy city marketplace filled with unknowing human bystanders and a lurking goblin.",
    "The player is in an ancient library, filled with enchanted books that have come to life.",
    "The player is at the peak of a frosty mountain, with a yeti guarding the only path forward.",
    "The player is in a forgotten graveyard with spirits emerging from the ground.",
    "The player is in a swamp, facing a pack of ravenous bog beasts.",
    "The player is in a wizard's tower, where a rival sorcerer prepares to cast a spell.",
    "The player is lost in a labyrinth with a minotaur stalking them.",
    "The player is in the throne room of a corrupted king who is under a witch's control.",
    "The player is in a dreamlike meadow filled with plants that react to magic.",
    "The player is in an eldritch dimension with an ancient, cryptic entity looming.",
    "The player is on a ghost ship sailing through a spectral sea, haunted by phantom pirates.",
    "The player is in an alchemist's laboratory filled with volatile magical substances.",
    "The player is in an enchanted forest, facing an angry treant blocking the path.",
    "The player is in a bustling tavern, where a disguised dragon is causing chaos.",
    "The player is in a dungeon facing a locked door with magical sigils.",
    "The player is in a moonlit glade surrounded by shape-shifting werecreatures.",
    "The player is at the heart of a volcano, confronted by a fiery salamander.",
    "The player is in a busy town square with a rampaging golem.",
    "The player is on a lonely moor, beset by banshees.",
    "The player is in a celestial observatory where the stars themselves are misaligned.",
    "The player is in the ruins of an ancient temple, where a stone gargoyle has come to life.",
    "The player is in a shadowy realm with an assassin made of darkness.",
    "The player is on a battlefield facing a horde of undead warriors.",
]
