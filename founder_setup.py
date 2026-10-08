"""Player-authored identity. Descriptive choices never grant mechanics."""
from copy import deepcopy

BACKGROUNDS = {
    'unspecified':'Leave my past open',
    'independent':'Independent scholar',
    'apprentice':'Former apprentice',
    'bookbinder':'Bookbinder or archivist',
    'traveller':'Travelling researcher',
    'craftsperson':'Practical craftsperson',
    'custom':'My own background',
}


def apply(s, a):
    import game as g
    kind=a.get('type')
    if kind not in ('save-founder-profile','finish-character-setup','use-founder-placeholder'):return False
    if kind=='finish-character-setup':
        g.require(s.get('soloLife',{}).get('characterSetup',{}).get('profileSaved'), 'Save your character details first.')
        s['soloLife']['characterSetup']['finished']=True
        return True
    if kind=='use-founder-placeholder':
        old=s['assetOverrides'].pop('founder',None)
        if old:s['assetHistory'].setdefault('founder',[]).append(old)
        return True
    g.require(g.character_at_castle(s,'founder'),'Return home before editing your character.')
    name=a.get('name');age=a.get('age');background=a.get('background','unspecified')
    g.require(isinstance(name,str) and 1<=len(name.strip())<=40 and not any(ord(c)<32 for c in name),'Enter a name of 1–40 characters.')
    g.require(type(age) is int and 18<=age<=120,'Choose an adult human age from 18 to 120.')
    g.require(isinstance(background,str) and background in BACKGROUNDS,'Choose an offered background.')
    fields={}
    for key,limit,label in [('pronouns',40,'pronouns'),('appearanceDescription',600,'appearance notes'),('backgroundNotes',600,'background notes')]:
        value=a.get(key,'')
        g.require(isinstance(value,str) and len(value)<=limit and not any(ord(c)<32 and c not in '\n\t' for c in value),'Use at most '+str(limit)+' characters for '+label+'.')
        fields[key]=value.strip()
    p=s['people']['founder']
    p.update(name=name.strip(),adultAgeYears=age,role='Human scholar · '+str(age),background=background,**fields)
    p['identityRevision']=p.get('identityRevision',1)+1
    record=s['soloLife'].setdefault('characterSetup',{'finished':True})
    record['profileSaved']=True
    g.add_journal(s,'Character details saved for '+p['name']+'. Background and appearance are descriptive; existing knowledge, possessions and abilities are unchanged.')
    return True


def profile(s):
    p=s['people']['founder']
    return {k:deepcopy(p.get(k,default)) for k,default in [('name','Your scholar'),('adultAgeYears',40),('pronouns',''),('appearanceDescription',''),('background','unspecified'),('backgroundNotes','')]}


def portrait_prompt(s):
    p=profile(s)
    import character_customization
    extra=character_customization.portrait_brief(s,'founder') if character_customization.person(s,'founder').get('appearance') or character_customization.style(s,'founder') else ''
    return (extra+' '+'Create a portrait of one clearly adult human scholar of practical magic for Stonework and Spellcraft. '
        f"Name: {p['name']}. Age: {p['adultAgeYears']}. Pronouns: {p['pronouns'] or 'unspecified; do not infer gender from the name'}. "
        f"Appearance: {p['appearanceDescription'] or 'adult features, practical scholarly clothes; choose an understated appearance'}. "
        'Natural eye-level perspective. Modest useful stone-and-timber castle, worn objects. Antique engraving–inspired fantasy illustration. Intricate etched linework, fine hatching and crosshatching, subtly worn print texture, and richly detailed aged materials. Historically grounded craftsmanship, understated fantasy, and believable proportions. Midnight navy and charcoal, muted violet, natural wood/plant/fabric colours, sparse dull brass. Dim but readable and welcoming. Avoid palatial luxury, glossy CGI, photorealism, glowing magic spectacle and crushing all detail into black. '
        'If footwear is visible, use flat shoes or boots only; no high heels, wedges or platforms. Natural proportions, readable face, calm clean contours without jittery edges, subtle paper texture, quiet background. '
        'Head-and-shoulders composition with the full head visible and breathing room around it. Opaque everyday clothing. '
        'No lettering, captions, ornamental border, interface elements or watermark. Portrait only; do not invent story events or powers.')
