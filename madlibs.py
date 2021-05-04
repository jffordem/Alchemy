# madlibs.py
# This version doesn't require the text to be a data structure.  It just requires alternate clauses to be in parens and separated by a slash.

import random

calendar_altText = "".join("""
While it may seem like trivia, it (
causes huge headaches for software developers/
is taken advantage of by high-speed traders/
triggered the (2003/2004/2005) Northeast Blackout/
has to be corrected for by GPS satellites/
cannot be used as an excuse for tax cuts/
is now recognized as a major cause of World War I).
""".split("\n"))

calendar_facts = "".join("""
Did you know that (
the (fall/spring) equinox/
the (winter/summer) (solstice/Olympics)/
the (earliest/latest) (sunrise/sunset)/
daylight (savings/saving) time/
leap (day/year)/
Easter/
the (harvest/blood/super) moon/
Toyota truck month/shark week) (
happens (earlier/later/at the wrong time) every year/
drifts out of sync with the (sun/moon/zodiac/(gregorian/mayan/lunar/iPhone) calendar/atomic clock in Colorado)/
might (not happen/happen twice) this year) 
because of (
time zone legislation in (Indiana/Arizona/Russia)/
a decree by the Pope in the 1500s/
(precession/libration/nutation/libation/eccentricity/obliquity) of the (moon/sun/Earth's axis/equator/prime meridian/(international date/Mason-Dixon) line)/
magnetic field reversal/
an arbitrary decision by (Benjamin Franklin/Isaac Newton/FDR))? Apparently (
it causes a predictable increase in car accidents/
that's why we have leap seconds/
scientists are really worried/
it was even more extreme during the (bronze age/ice age/cretaceous/1990s)/
there's a proposal to fix it, but it (will never happen/actually makes things worse/is stalled in congress/might be unconstitutional)/
it's getting worse and no one knows why).
""".split("\n"))

country_song = """
I met her (on the highway/in Sheboygan/outside Fresno/at a truck stop/on probation/in a jail cell/at a stage play/in a nightmare/incognito/in the Stone Age/in a treehouse/in a gay bar) (in September/at McDonald's/ridin' shotgun/wrestlin' gators/all hunched over/poppin' uppers/sort of pregnant/out of aspirin/with some joggers/stoned on oatmeal/with Merv Griffin/dead all over);
I can still recall (that purple dress/that little hat/that burlap bra/those training pants/the stolen goods/that plastic nose/that wild tattoo/the Stassin pin/the neon sign/that creepy smile/the hearing aid/the boxer shorts) she wore;
She was (sobbin' at the toll booth/drinkin' Dr. Pepper/weighted down with Twinkies/breakin' out with acne/crawlin' through the carpet/smellin' kind of funny/crashin' through the guardrail/chewin' on a hangnail/botherin' the padre/talkin' in Swahili/drownin' in the quicksand/slurpin' up linguini) (in the twilight/but I loved her/by the off-ramp/near Poughkeepsie/with her cobra/when she shot me/without credit/or even longer/on her elbows/with Led-Zeppelin/with Miss Piggy/in her muu-muu), and I knew (no guy would ever love her more/that she would be an easy score/she'd bought her dentures in a store/that she would be a crashing bore/I'd never rate her more than '4'/they'd hate her guts in Baltimore/it was a raven, nothing more/her dress was the one that tore/we really lost the last World War/I'd have to scrape her off the floor/what strong deodorants were for/that she was rotten to the core/that I would upchuck on the floor);
(I promised her/I knew deep down/She asked me if/I told her shrink/The judge declared/My Pooh Bear said/I shrieked in pain/The painters knew/A Klingon said/In a dream I saw/My hamster thought/The blood test showed/Her rabbi said) I'd (stay with her/warp her mind/swear off booze/change my sex/punch her out/live off her/have my rash/stay a dwarf/need my shots/hate her dog/pick my nose/play 'Go Fish'/salivate) forever;
She said to me (our love would never die/there was no other guy/man wasn't meant to fly/that Nixon didn't lie/her basset hound was shy/that Rolaids made her high/she'd have a swiss on rye/she loved my one blue eye/her brother's name was Hy/she liked 'Spy vs. Spy'/that birthdays made her cry/she couldn't stand my tie);
But who'd have thought she'd (run off/wind up/boogie/yodel/sky dive/turn green/fall down/freak out/blast off/make it/black out/bobsled/grovel) (with my best friend/in my Edsel/on a surfboard/on 'The Gong Show'/with her dentist/on her 'Workmate'/with a robot/with no clothes on/at her health club/in her Maytag/with her guru/while in labor);
(You'd think at least that she'd have said/I never had the chance to say/She told her fat friend Grace to say/I now can kiss my credit cards/I guess I was too smashed to say/I watched her melt away and sobbed/She fell beneath the wheels and cried/She sent a hired thug to say/She freaked out on the lawn and screamed/I pushed her off the bridge and waved/But that's the way that pygmies say/She sealed me in the vault and smirked) goodbye.;
"""

whip_it = "".join("""
((Has a good time turned around? You must/Have you ever lived it down? Not unless you/Has anyone gotten away? Not until they)/
(Has a problem come along?/Has the cream sat out too long?/Is something going wrong?) You must) 
whip it.
""".split("\n"))

def all(s):
    result = ""
    temp = ""
    i = 0
    for ch in s:
        if i == 0 and ch == '(':
            i += 1
        elif i == 1 and ch == ')':
            i -= 1
            result += any(temp)
            temp = ""
        elif ch == '(':
            i += 1
            temp += ch
        elif ch == ')':
            i -= 1
            temp += ch
        elif i == 0:
            result += ch
        else:
            temp += ch
    return result;

def any(s):
    result = [ ]
    temp = ""
    i = 0
    for ch in s:
        if ch == '(':
            temp += ch
            i += 1
        elif ch == ')':
            temp += ch
            i -= 1
        elif i == 0 and ch == '/':
            result.append(all(temp))
            temp = ""
        else:
            temp += ch
    if len(temp) > 0:
        result.append(all(temp))
    return random.choice(result)

def madlib(pattern):
    #return all(pattern).replace("\r", "").replace("\n", "<p>")
    return all(pattern).replace("\r", "").split('\n')

if __name__ == "__main__":
    print(all(country_song))
