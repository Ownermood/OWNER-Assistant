# OWNER Assistant - which commands friends may use while Fun mode is ON.
# Part of OWNER Assistant (based on Ultroid, AGPL-3.0).
#
# SAFE BY DEFAULT: a command is closed unless it is listed here. If a new
# plugin is added it stays owner-only until someone reviews it and adds it.
#
# Nothing in this list may:
#   * run code or shell          (.eval .bash .cpp .install)
#   * read or write server files (.open .ls .paste .ncode .download .webupload)
#     -> those can dump .env and leak the SESSION string = full account takeover
#   * show or change config/DB   (.get .setdb .deldb .variables)
#   * change the owner's account (.clone .setname .setbio .setpic .logout)
#   * use sudo / bot control     (.addsudo .restart .shutdown .update)
#   * spam or broadcast          (.spam .bigspam .gucast .echo)   -> ban risk
#   * do group admin             (.ban .kick .mute .promote .purge .warn ...)
#   * spend the owner's API keys (.gemini .gpt .antr .deepseek)
#   * read the owner's Drive/PMs (.gdlist .gdown .sg .logpm .listapproved)

FUN_ALLOW = frozenset(
    """
    alive ping help cmds id info ipinfo date gadget suggest

    propose love rose hearts lovecalc joke truth dare decide bored random
    randomuser hack kill fp frog xo poll

    figlet font linetext boxtext bubbletext cursive fraktify greekify rusify
    sorcify tantext tiny shift ascii type write q quot qfancy

    encode decode mdecode mencode bf qrcode qrdecode morsecode tr meaning ud
    spcheck autocorrect wreplace calc

    image img unsplash wall waifu weeb manga anime aniquote character pokemon
    pokecard apod astronomy pntrst gif icon logo phlogo

    blue border circle color glitch pixelator resize rotate round sample size
    poto rvgif stic sticker sticklet kang packkang mmf

    song saavn findsong whichsong yt getaudio extractaudio atrim vtrim
    makevoice tts stt mediainfo compress convert pdf pdtext pdscan ocr rmbg

    imdb github google search wiki wikipedia weather air cov covid webshot
    telegraph url tiny twdetail twuser uta vshots
    """.split()
)


def is_fun_command(name):
    """True if guests may run this command while Fun mode is ON."""
    return bool(name) and name.lower() in FUN_ALLOW
