import json

def enable_authoring(store):
    state=store.read()
    state['testing']['enabled']=True
    with store.connect() as db:
        db.execute('UPDATE campaign SET state=? WHERE id=1',(json.dumps(state),))
