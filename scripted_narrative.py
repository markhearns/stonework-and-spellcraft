"""Deterministic accounts of already resolved game events. No external service."""

def journal(state):
    import game as g
    rows=state.get('lastPhaseSummary',[])
    g.require(bool(rows),'Advance once to create an account of resolved events.')
    # Exact authoritative outcomes; no inferred accomplishments or hidden-lore context.
    return 'Day '+str(state['dayNumber'])+', '+state['currentDayPhase']+' — results of the last Advance\n\n'+'\n'.join('• '+line for line in rows)
