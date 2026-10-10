"""Explicit, recoverable image drafts. Acceptance uses the existing art history."""
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from dialogue import ProviderSettings
from game import RuleError
from founder_setup import portrait_prompt, profile


class PortraitSettings(ProviderSettings):
    image_mode=True
    def __init__(self,directory):
        super().__init__(directory)
        self.path=Path(directory)/'portrait-provider-settings.json'

    def save(self,payload):
        return super().save({**payload,'maxOutputTokens':500})


def provider_image(settings,prompt):
    import provider_protocols as p
    fmt=settings.get('format','openrouter-images')
    if fmt=='gemini-images':body={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'responseModalities':['TEXT','IMAGE']}}
    elif fmt=='openrouter-images':body={'model':settings['model'],'messages':[{'role':'user','content':prompt}],'modalities':['image','text'],'stream':False}
    else:body={'model':settings['model'],'prompt':prompt,'n':1,'output_format':'png'}
    request=urllib.request.Request(p.request_url(settings),data=json.dumps(body).encode(),headers=p.headers(settings))
    try:
        with p.open_request(request,timeout=90) as response:raw=response.read(9_000_001)
        if len(raw)>9_000_000:raise RuleError('The image reply exceeded the supported size. Try a smaller image.')
        result=json.loads(raw)
        if fmt=='openrouter-images':
            data=result['choices'][0]['message']['images'][0]['image_url']['url']
            if not isinstance(data,str) or not data.startswith(('data:image/png;base64,','data:image/jpeg;base64,','data:image/webp;base64,')):raise ValueError()
            return data
        if fmt=='gemini-images':
            item=next(x['inlineData'] for x in result['candidates'][0]['content']['parts'] if 'inlineData' in x)
            mime=item['mimeType'];encoded=item['data']
        else:
            item=result['data'][0];mime=item.get('media_type','image/png');encoded=item.get('b64_json')
        if mime not in ('image/png','image/jpeg','image/webp') or not isinstance(encoded,str):raise ValueError()
        return 'data:'+mime+';base64,'+encoded
    except urllib.error.HTTPError as error:
        raise RuleError({401:'The image provider rejected the key.',402:'The image account has insufficient credit.',429:'The image provider rate limit was reached.'}.get(error.code,'The image provider rejected the request. Check its API format, endpoint and model.')) from None
    except RuleError:raise
    except Exception:raise RuleError('No usable image was received. The request may have incurred usage. No portrait was accepted.') from None


class PortraitService:
    def __init__(self,settings,transport=None):
        self.settings=settings
        self.transport=transport or provider_image

    def list(self,store):
        with store.connect() as db:
            return {'drafts':[json.loads(r[0]) for r in db.execute('SELECT result FROM portrait_drafts ORDER BY rowid DESC LIMIT 8')]}

    def abandon(self,store,payload):
        key=payload.get('draftId')
        if not isinstance(key,str):raise RuleError('Choose a pending portrait request.')
        with store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT result FROM portrait_drafts WHERE id=?',(key,)).fetchone()
            if not row:raise RuleError('Choose a portrait request in this campaign.')
            draft=json.loads(row[0])
            if draft['status']=='processing':
                draft['status']='abandoned'
                draft['error']='Put aside explicitly. This does not cancel a provider request or refund usage.'
                db.execute('UPDATE portrait_drafts SET result=? WHERE id=?',(json.dumps(draft),key))
        return draft

    def generate(self,store,payload):
        request_id=payload.get('requestId')
        if not isinstance(request_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{8,100}',request_id):raise RuleError('A valid image request identifier is required.')
        encoded=json.dumps(payload,sort_keys=True)
        with store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            old=db.execute('SELECT payload,result FROM portrait_drafts WHERE id=?',(request_id,)).fetchone()
            if old:
                if old[0]!=encoded:raise RuleError('This image request identifier was already used for a different request.')
                return json.loads(old[1])
            state=json.loads(db.execute('SELECT state FROM campaign WHERE id=1').fetchone()[0])
            if type(payload.get('expectedRevision')) is not int or payload['expectedRevision']!=state['revision']:raise RuleError('The campaign changed. Review your character before requesting a portrait.')
            if not state.get('soloLife',{}).get('characterSetup',{}).get('profileSaved'):raise RuleError('Save your character details before requesting a portrait.')
            config=self.settings.read()
            if not __import__('provider_protocols').ready(config):raise RuleError('Configure and enable an image model first, or import a portrait or keep the placeholder.')
            if db.execute("SELECT COUNT(*) FROM portrait_drafts WHERE json_extract(result,'$.status')='processing'").fetchone()[0]:raise RuleError('A portrait request is already processing. Recover its result before starting another.')
            prompt=portrait_prompt(state)
            draft={'id':request_id,'status':'processing','baseRevision':state['revision'],'model':config['model'],'prompt':prompt,'profile':profile(state)}
            db.execute('INSERT INTO portrait_drafts VALUES (?,?,?)',(request_id,encoded,json.dumps(draft)))
        try:
            image=self.transport(config,prompt)
            draft.update(status='ready',assetPath=store.upload({'imageData':image}))
        except Exception as error:
            draft.update(status='failed',error=str(error) if isinstance(error,RuleError) else 'Portrait generation failed. The request may have incurred usage. No portrait was accepted.')
        with store.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            current=json.loads(db.execute('SELECT result FROM portrait_drafts WHERE id=?',(request_id,)).fetchone()[0])
            if current['status']!='processing':return current
            db.execute('UPDATE portrait_drafts SET result=? WHERE id=?',(json.dumps(draft),request_id))
        return draft
