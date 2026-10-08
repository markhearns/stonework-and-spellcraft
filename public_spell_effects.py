"""Exact finite state transitions for the public experimental forms.
These states describe the bounded inert setup; none creates inventory or income.
"""
STATES={
'loosen-a-practice-knot':('knot','loosened'),
'guide-a-basin-pour':('liquidPosition','basin'),
'hold-an-ink-sample-steady':('inkSample','separated-for-comparison'),
'compare-two-margins':('display','two-authorized-margins'),
'rootline-witness':('display','visible-root-boundary'),
'copy-a-drawn-outline':('display','temporary-authorized-outline'),
'sequence-a-demonstration':('display','supplied-next-step'),
'carry-a-wash-along-thread':('washPosition','prepared-thread'),
'shade-a-sample-edge':('shadow','softened'),
'hold-two-fibres-together':('fibres','aligned-not-joined'),
'mark-an-invited-threshold':('display','entered-invitation-state'),
'warm-a-clay-rest':('restWarmth','gently-warm'),
'return-a-harmless-drip':('liquidPosition','open-catch-cup'),
'shield-a-practice-label':('labelShield','active'),
'keep-a-question-attached':('display','unanswered-question-with-source'),
'compare-leaf-positions':('display','supplied-leaf-drawings'),
'trace-a-waterline':('display','visible-waterline-impression'),
'label-a-control-sample':('display','author-supplied-control-label'),
'thread-a-narrow-wick':('liquidPosition','wick-catch-dish'),
'match-two-blunt-edges':('sampleEdges','aligned-not-joined'),
'temporary-label-tack':('temporaryLabel','attached'),
'hovering-test-weight':('testWeight','above-own-catch-tray'),
'quiet-vibration-window':('display','local-sample-vibration'),
'sliding-sample-lane':('samplePosition','lane-end'),
'gentle-bench-breeze':('draft','through-demonstration-duct'),
'echo-from-a-visible-wall':('display','local-authorized-echo-comparison'),
'separate-pencil-from-wash':('display','two-visible-drawing-layers'),
'close-a-local-light-mask':('screen','masked'),
'recall-a-measured-outline':('display','previously-recorded-outline'),
'measured-sand-release':('sandPosition','own-catch-cup'),
'wet-only-the-practice-line':('washPosition','declared-practice-line'),
'share-a-cup-s-warmth':('warmth','shared-between-supplied-cups'),
'return-a-cane-curve':('sampleShape','recorded-rest-curve'),
'sort-visible-bead-shapes':('beads','sorted-by-declared-shape'),
'compare-two-cloth-swatches':('display','same-light-swatch-comparison'),
'open-one-scent-sample':('scentLid','selected-cup-open'),
'show-a-settling-boundary':('display','visible-sediment-boundary'),
'gather-pane-droplets':('liquidPosition','pane-catch-dish'),
'hold-a-teaching-boundary':('display','supplied-mixture-interface'),
'buffer-a-sample-box':('sampleBox','bounded-humidity-moderation'),
'dim-a-study-pane':('screen','diffuse'),
'align-two-sample-faces':('sampleFaces','same-reference-plane'),
'shelter-a-loose-diagram':('dripPath','diagram-catch-tray'),
'remove-a-trial-finish':('trialFinish','removed'),
'float-a-level-reference':('display','supplied-level-reference'),
'quietly-display-an-echo':('display','local-authorized-visual-echo'),
'separate-and-compare-swatches':('display','visible-swatch-layers'),
'mask-a-reference-overlay':('overlay','hidden'),
'guide-a-damp-line-slowly':('washPosition','practice-line-catch-tray'),
'return-a-warm-test-curve':('sampleShape','recorded-warm-rest-curve'),
'compare-a-sorted-sediment':('display','identified-grains-and-settled-sample'),
'keep-scent-behind-a-screen':('scentLid','screen-controlled'),
'catch-a-pane-s-runoff':('liquidPosition','designated-runoff-dish'),
'show-a-moisture-exchange':('display','supplied-current-and-dry-reference'),
'hold-a-sheltering-test-plane':('splashScreen','aligned-around-practice-drawing'),
'release-a-temporary-label':('temporaryLabel','released'),
'paired-circle-freight-fold':('freight','transferred-between-local-circles'),
'archive-cabinet-dry-interlude':('emptyCabinet','attended-moisture-stabilization'),
'suspended-roof-model':('scaleRoofModel','suspended-for-comparison'),
'isolated-residual-unweaving':('registeredResidual','removed'),
'short-span-cargo-support':('inertCargo','supported-over-bench-gap'),
'two-station-study-impression':('display','two-authorized-local-screens'),
'pattern-from-accepted-reference':('display','preserved-accepted-reference-outline'),
'cleared-workpit-test-boundary':('testPit','declared-mild-disturbance-redirected'),
'permissioned-object-recovery':('ownedTool','returned-to-inspected-cradle'),
'layered-waterwork-demonstration':('display','supplied-scale-water-channels'),
'bounded-acoustic-canopy':('sampleVibration','locally-dampened'),
'shared-reversible-sample-finish':('trialFinish','temporary-comparison-finish')}

def slug(r):return r['id'].removeprefix('ss-mag-spell-construction-')

def validate(s,a,r,who,setup):
    import game as g,public_workshop as w
    key=slug(r);g.require(key in STATES,'No typed effect adapter for this exact form.')
    result={}
    targeted={'paired-circle-freight-fold','permissioned-object-recovery','isolated-residual-unweaving','remove-a-trial-finish','release-a-temporary-label','shared-reversible-sample-finish'}
    if key not in targeted:return result
    obj=w.item(s,a.get('targetItemId'),who)
    g.require(not w.locked(s,obj['id']) and obj['id']!=setup['id'],'Choose a separate, unreserved owned inert target.')
    g.require(obj.get('contentKind') not in ('food-or-drink','garden-specimen') and obj['kind'] in ('experiment','equipment','artifact','furnishing','household-object'),'Only an established inert object can be targeted.')
    g.require(not obj['roomId'] or obj['kind']=='experiment','Uninstall the object before manipulating it.')
    if key=='release-a-temporary-label':g.require(obj.get('experimentalState',{}).get('temporaryLabel')=='attached','This exact target has no registered temporary label.')
    if key in ('remove-a-trial-finish','isolated-residual-unweaving'):g.require(obj.get('trialFinish') is not None,'This target has no registered removable trial finish.')
    if key=='permissioned-object-recovery':g.require(obj['kind']=='equipment','This recovery form targets an owned inert tool.')
    if key=='shared-reversible-sample-finish':g.require(obj.get('trialFinish') is None,'Remove this target’s earlier finish first.')
    result['targetItemId']=obj['id']
    if key=='shared-reversible-sample-finish':
        extra=a.get('additionalTargetItemIds',[])
        g.require(isinstance(extra,list) and all(isinstance(k,str) for k in extra),'Select the actual additional inert samples.')
        targets=[obj['id']]+extra
        g.require(2<=len(targets)<=3 and len(set(targets))==len(targets),'Choose two or three distinct owned inert samples for the shared finish.')
        for target in targets:
            sample=w.item(s,target,who)
            g.require(sample['kind'] in ('experiment','equipment','artifact','furnishing','household-object') and sample.get('contentKind') not in ('food-or-drink','garden-specimen') and target!=setup['id'] and not w.locked(s,target) and sample.get('trialFinish') is None,'Every actual sample must be inert, owned, unreserved and free of an earlier finish.')
        result['targetItemIds']=targets
    if key=='paired-circle-freight-fold':
        from public_progression import ADJACENT
        destination=w.item(s,a.get('destinationItemId'),who)
        g.require(destination['kind']=='experiment' and destination['definitionId']==r['id'] and not w.locked(s,destination['id']),'Build a second compatible local freight-circle setup first.')
        g.require(frozenset((setup['roomId'],destination['roomId'])) in ADJACENT,'Use two distinct, connected main-wing rooms with reviewed local endpoints.')
        g.require(obj.get('locationRoomId')==setup['roomId'],'The actual parcel must already be at the source circle.')
        result['destinationItemId']=destination['id'];result['destinationRoomId']=destination['roomId']
    return result

def apply(s,p,r,setup):
    import public_workshop as w
    key=slug(r);field,value=STATES[key]
    obj=w.item(s,p['targetItemId']) if p.get('targetItemId') else setup
    obj.setdefault('experimentalState',{})[field]=value
    if key in ('paired-circle-freight-fold','permissioned-object-recovery'):
        obj['locationRoomId']=p.get('destinationRoomId',setup['roomId'])
    if key=='shared-reversible-sample-finish':
        for target in p['targetItemIds']:
            sample=w.item(s,target);sample['trialFinish']={'receiptId':p['id'],'description':'Removable fictional comparison finish; original surface unchanged.'}
            sample.setdefault('experimentalState',{})[field]=value
    if key in ('remove-a-trial-finish','isolated-residual-unweaving'):obj['trialFinish']=None
    return {'targetId':obj['id'],'changedField':field,'state':value}
