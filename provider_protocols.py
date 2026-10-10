"""Small explicit adapters for configurable text and image endpoints.

The endpoint is chosen by the server owner, never by generated content.
Secrets are headers only; redirects cannot forward them to a different host.
"""
import ipaddress
import urllib.parse
import urllib.request
from game import RuleError

TEXT_FORMATS = ('openai', 'anthropic', 'gemini')
IMAGE_FORMATS = ('openai-images', 'openrouter-images', 'gemini-images')
TEXT_DEFAULT = 'https://openrouter.ai/api/v1/chat/completions'
IMAGE_DEFAULT = TEXT_DEFAULT

def endpoint(value):
    if not isinstance(value, str) or len(value)>1000 or any(c.isspace() for c in value):
        raise RuleError('Enter a complete API endpoint URL without whitespace.')
    try:
        u=urllib.parse.urlsplit(value)
        port=u.port
        local=u.hostname=='localhost'
        try: local=local or ipaddress.ip_address(u.hostname).is_private
        except ValueError: pass
        if not u.hostname or u.username or u.password or u.query or u.fragment or not u.path:
            raise ValueError()
        if u.scheme!='https' and not (u.scheme=='http' and local):raise ValueError()
    except (ValueError,TypeError):
        raise RuleError('Use an HTTPS endpoint, or HTTP on a local/private server. Put credentials in the API key field, not the URL.') from None
    return value

def headers(c):
    h={'Content-Type':'application/json'}
    if c.get('authMode','key')=='key':
        key=c.get('apiKey','')
        if c.get('format')=='anthropic':h['x-api-key']=key
        elif c.get('format','').startswith('gemini'):h['x-goog-api-key']=key
        else:h['Authorization']='Bearer '+key
    if c.get('format')=='anthropic':h['anthropic-version']='2023-06-01'
    return h

def ready(c):
    return bool(c.get('enabled') and c.get('model') and (c.get('authMode','key')=='none' or c.get('apiKey')))

def request_url(c):
    return endpoint(c.get('endpoint',TEXT_DEFAULT)).replace('{model}',urllib.parse.quote(c['model'].removeprefix('models/'),safe=''))

def text_request(c,messages):
    fmt=c.get('format','openai');limit=c['maxOutputTokens']
    system='\n\n'.join(m['content'] for m in messages if m['role']=='system')
    dialogue=[m for m in messages if m['role']!='system']
    if fmt=='anthropic':return {'model':c['model'],'system':system,'messages':dialogue,'max_tokens':limit,'stream':False}
    if fmt=='gemini':return {'systemInstruction':{'parts':[{'text':system}]},'contents':[{'role':'model' if m['role']=='assistant' else 'user','parts':[{'text':m['content']}]} for m in dialogue],'generationConfig':{'maxOutputTokens':limit}}
    return {'model':c['model'],'messages':messages,c.get('tokenParameter','max_tokens'):limit,'stream':False}

def text_reply(c,result):
    fmt=c.get('format','openai')
    if fmt=='anthropic':
        content='\n'.join(p['text'] for p in result['content'] if p.get('type')=='text')
        raw=result.get('usage') or {};usage={'prompt_tokens':raw.get('input_tokens'),'completion_tokens':raw.get('output_tokens')}
    elif fmt=='gemini':
        content='\n'.join(p['text'] for p in result['candidates'][0]['content']['parts'] if 'text' in p and not p.get('thought'))
        raw=result.get('usageMetadata') or {};usage={'prompt_tokens':raw.get('promptTokenCount'),'completion_tokens':raw.get('candidatesTokenCount'),'total_tokens':raw.get('totalTokenCount')}
    else:
        content=result['choices'][0]['message']['content'];usage=result.get('usage') or {}
        if isinstance(content,list):content='\n'.join(p['text'] for p in content if p.get('type')=='text')
    if not isinstance(content,str) or not content.strip() or len(content)>12000:raise ValueError()
    usage={k:usage[k] for k in ('prompt_tokens','completion_tokens','total_tokens') if type(usage.get(k)) is int and usage[k]>=0}
    if 'total_tokens' not in usage and 'prompt_tokens' in usage and 'completion_tokens' in usage:usage['total_tokens']=usage['prompt_tokens']+usage['completion_tokens']
    return {'text':content.strip(),'usage':usage}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise RuleError('The API redirected the request. Save its final endpoint URL before trying again; your key was not forwarded.')

def open_request(request,timeout):
    return urllib.request.build_opener(NoRedirect()).open(request,timeout=timeout)
