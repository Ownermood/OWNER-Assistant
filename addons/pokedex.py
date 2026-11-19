# Creator - @THE_BL_ACK_HAT @Shivam_Patel
#
# Ultroid - UserBot
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://www.github.com/TeamUltroid/Ultroid/blob/main/LICENSE/>.

"""
✘ Commands Available -

• `{i}pokemon <query>`
    Send details of Pokemon.

• `{i}pokecard <query>`
    Send Card of Pokemon.
"""

from . import async_searcher, ultroid_cmd

POKEAPI = "https://pokeapi.co/api/v2"


def _title(text):
    return text.replace("-", " ").title()


@ultroid_cmd(pattern="pokemon( (.*)|$)")
async def pokedex(event):
    pokemon = event.pattern_match.group(1).strip().lower().replace(" ", "-")
    if not pokemon:
        return await event.eor("`Give a Pokemon Name`")
    xx = await event.eor("`Booting up the pokedex.......`")
    try:
        poke = await async_searcher(f"{POKEAPI}/pokemon/{pokemon}", re_json=True)
        species = await async_searcher(poke["species"]["url"], re_json=True)
    except Exception:
        return await xx.edit("`Be sure To give correct Name`")

    types = ", ".join(_title(t["type"]["name"]) for t in poke["types"])
    abilities = ", ".join(_title(a["ability"]["name"]) for a in poke["abilities"])
    stats = {s["stat"]["name"]: s["base_stat"] for s in poke["stats"]}
    moves = [_title(m["move"]["name"]) for m in poke["moves"][:7]]
    moves += ["None"] * (7 - len(moves))
    genus = next(
        (g["genus"] for g in species.get("genera", []) if g["language"]["name"] == "en"),
        "Unknown",
    )
    description = next(
        (
            f["flavor_text"].replace("\n", " ").replace("\f", " ")
            for f in reversed(species.get("flavor_text_entries", []))
            if f["language"]["name"] == "en"
        ),
        "No description.",
    )
    generation = _title(species.get("generation", {}).get("name", "unknown"))

    # Evolution line
    line = "None"
    try:
        chain = (await async_searcher(species["evolution_chain"]["url"], re_json=True))[
            "chain"
        ]
        names, stack = [], [chain]
        while stack:
            node = stack.pop(0)
            names.append(_title(node["species"]["name"]))
            stack.extend(node.get("evolves_to", []))
        line = ", ".join(names)
    except Exception:
        pass

    # Weaknesses: types that deal double damage to any of this pokemon's types
    weak = set()
    try:
        for t in poke["types"]:
            rel = await async_searcher(t["type"]["url"], re_json=True)
            weak.update(
                _title(x["name"]) for x in rel["damage_relations"]["double_damage_from"]
            )
    except Exception:
        pass

    sprite = (
        poke["sprites"].get("other", {}).get("official-artwork", {}).get("front_default")
        or poke["sprites"].get("front_default")
    )
    cap = f"""
**NAME** : `{_title(poke['name'])}`
**TYPE** : `{types}`
**SPECIES** : `{genus}`
**Evolution Line** : `{line}`
**Generation** : `{generation}`
**ABILITIES** : `{abilities}`
**WEAKNESSES** : `{', '.join(sorted(weak)) or 'None'}`
**HEIGHT** : `{poke['height'] / 10} m`
**WEIGHT** : `{poke['weight'] / 10} kg`

**Stats**
**Hp** : `{stats.get('hp')}` | **Attack** : `{stats.get('attack')}` | **Defense** : `{stats.get('defense')}`
**Sp_atk** : `{stats.get('special-attack')}` | **Sp_def** : `{stats.get('special-defense')}` | **Speed** : `{stats.get('speed')}`
**Total** : `{sum(stats.values())}`

**Moves** : `{', '.join(moves)}`

**DESCRIPTION** : `{description}`
"""
    if sprite:
        await event.client.send_file(event.chat_id, sprite, caption=cap[:1024])
        if len(cap) > 1024:
            await event.respond(cap[1024:])
    else:
        await event.respond(cap)
    await xx.delete()


@ultroid_cmd(pattern="pokecard( (.*)|$)")
async def pokecard(event):
    pokename = event.pattern_match.group(1).strip().lower()
    if not pokename:
        return await event.eor("`Give A Pokemon name`")
    try:
        a = await async_searcher(
            "https://api.pokemontcg.io/v2/cards",
            params={"q": f'name:"{pokename}"', "pageSize": 1},
            re_json=True,
        )
        o = a["data"][0]["images"]["large"]
        await event.client.send_file(event.chat_id, o)
        await event.delete()
    except BaseException:
        await event.eor("`Be sure To give correct Name`")
