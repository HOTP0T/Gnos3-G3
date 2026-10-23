"""Current-user Office import into the user's private "Office Files" knowledge base.

Run by the Office page in Gnos3 (on open, every few minutes while open, on
leave, and by the Sync files button). Files deleted in Office leave the base
too. No all-user job: only the signed-in user's own files are read.
"""
import asyncio
import base64
import hashlib
import io
import logging
import mimetypes
import os
import time
import uuid
from pathlib import Path
import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from open_webui.internal.db import get_async_db_context
from open_webui.models.files import Files, File, FileForm
from open_webui.models.knowledge import Knowledges, Knowledge
from open_webui.storage.provider import Storage
from open_webui.utils.auth import get_verified_user, create_k4mi_exchange_token
from open_webui.utils.access_control import has_permission

router = APIRouter()
log = logging.getLogger(__name__)
locks = {}

async def permitted(request, user):
    if user.role not in ('user','admin','superadmin'):
        return False
    if user.role in ('admin','superadmin'):
        return True
    # The base holds only the user's own Office files and is created for them,
    # so Office access is enough; workspace.knowledge gates hand-made bases.
    return await has_permission(user.id,'modules.office.read',request.app.state.config.USER_PERMISSIONS)

async def private_knowledge(user, create=True):
    identity=str(uuid.uuid5(uuid.NAMESPACE_URL,'gnos3-office-knowledge:'+user.id))
    async with get_async_db_context() as db:
        row=await db.get(Knowledge,identity)
        if row and (row.user_id!=user.id or (row.meta or {}).get('office_module') is not True):
            raise RuntimeError('Office knowledge identity conflict')
        if not row and not create:
            return None
        if not row:
            row=Knowledge(id=identity,user_id=user.id,name='Office Files',description='Your Office documents. Use Sync my Office files to import the latest saved versions.',meta={'office_module':True},created_at=int(time.time()),updated_at=int(time.time()))
            db.add(row)
            await db.commit()
    return identity

async def update_meta(file_id,user,values,**columns):
    async with get_async_db_context() as db:
        row=await db.get(File,file_id)
        if not row or row.user_id!=user.id:
            raise RuntimeError('Office file ownership changed')
        row.meta={**(row.meta or {}),**values}
        for name,value in columns.items():setattr(row,name,value)
        row.updated_at=int(time.time())
        await db.commit()

async def import_file(request,client,headers,knowledge_id,user,source):
    from open_webui.routers.retrieval import process_file,ProcessFileForm
    from open_webui.retrieval.vector.async_client import ASYNC_VECTOR_DB_CLIENT
    file_id=str(uuid.uuid5(uuid.NAMESPACE_URL,'gnos3-office-file:'+user.id+':'+source['id']))
    existing=await Files.get_file_by_id(file_id)
    if existing and (existing.user_id!=user.id or (existing.meta or {}).get('office_source_id')!=source['id']):
        raise RuntimeError('Office file identity conflict')
    if existing and (existing.meta or {}).get('office_synced_hash')==source['hash'] and await Knowledges.has_file(knowledge_id,file_id):return
    response=await client.get('/api/knowledge-export',headers=headers,params={'id':source['id'],'hash':source['hash']});response.raise_for_status()
    payload=response.json()
    data=base64.b64decode(payload['dataBase64'],validate=True)
    if hashlib.sha256(data).hexdigest()!=source['hash']:raise RuntimeError('Office file changed during import')
    content=payload.get('text')
    meta={'name':source['name'],'size':len(data),'content_type':mimetypes.guess_type(source['name'])[0] or 'application/octet-stream','office_source_id':source['id'],'office_source_user':user.id,'office_source_hash':source['hash'],'office_source_path':source['path'],'office_sync_status':'indexing'}
    stored_name=file_id+'_'+source['hash'][:16]+'_'+Path(source['name']).name
    _,path=await asyncio.to_thread(Storage.upload_file,io.BytesIO(data),stored_name,{'OpenWebUI-File-Id':file_id,'OpenWebUI-User-Id':user.id})
    if not existing:
        file=await Files.insert_new_file(user.id,FileForm(id=file_id,filename=source['name'],path=path,meta=meta))
        if file is None:raise RuntimeError('Could not create Office knowledge file')
    else:
        await update_meta(file_id,user,meta,filename=source['name'],path=path)
    # The private knowledge UI shows the file even if embedding is unavailable.
    if not await Knowledges.has_file(knowledge_id,file_id):
        await Knowledges.add_file_to_knowledge_by_id(knowledge_id,file_id,user.id)
    try:
        if content is None:
            from open_webui.routers.retrieval import build_loader_from_config,get_loader_config
            loader=build_loader_from_config(request,await get_loader_config())
            loader.user=user
            loader.metadata={'file_id':file_id,'file_name':source['name'],'file_content_type':meta['content_type']}
            local=await asyncio.to_thread(Storage.get_file,path)
            documents=await loader.aload(source['name'],meta['content_type'],local)
            content='\n'.join(document.page_content for document in documents)
        await Files.update_file_data_by_id(file_id, {'content':content, 'status':'processing' if content.strip() else 'completed'})
        if content.strip():
            if await ASYNC_VECTOR_DB_CLIENT.has_collection(knowledge_id):
                await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=knowledge_id,filter={'file_id':file_id})
            async with get_async_db_context() as db:
                await process_file(request,ProcessFileForm(file_id=file_id,content=content,collection_name=knowledge_id),user=user,db=db)
        elif await ASYNC_VECTOR_DB_CLIENT.has_collection(knowledge_id):
            await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=knowledge_id,filter={'file_id':file_id})
        await update_meta(file_id,user,{'office_synced_hash':source['hash'],'office_sync_status':'ready' if content.strip() else 'empty','office_sync_error':None})
    except Exception:
        await update_meta(file_id,user,{'office_sync_status':'failed','office_sync_error':'Indexing failed. Try Sync my Office files again.'})
        raise

async def remove_missing(knowledge_id,user,present_ids):
    """Files deleted in Office leave the user's Office Files base as well."""
    from open_webui.retrieval.vector.async_client import ASYNC_VECTOR_DB_CLIENT
    removed=0
    for file in await Knowledges.get_files_by_id(knowledge_id):
        meta=file.meta or {}
        if file.user_id!=user.id or meta.get('office_source_user')!=user.id or meta.get('office_source_id') in present_ids:
            continue
        await Knowledges.remove_file_from_knowledge_by_id(knowledge_id,file.id)
        if await ASYNC_VECTOR_DB_CLIENT.has_collection(knowledge_id):
            await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=knowledge_id,filter={'file_id':file.id})
        try:
            await asyncio.to_thread(Storage.delete_file,file.path)
        except Exception:
            log.warning('Office knowledge: stored copy already gone file=%s',file.id)
        await Files.delete_file_by_id(file.id)
        removed+=1
    return removed

@router.post('/sync')
async def synchronize(request:Request,auto:bool=False,user=Depends(get_verified_user)):
    """auto=true: background run from the Office page; creates no empty base."""
    if not await permitted(request,user):raise HTTPException(403,'Office and knowledge workspace access are required')
    lock=locks.setdefault(user.id,asyncio.Lock())
    if lock.locked():raise HTTPException(409,'Your Office files are already being imported')
    async with lock:
        token,_=create_k4mi_exchange_token(user,audience='gnos3-module:office')
        url=os.environ.get('OFFICE_MODULE_URL','http://assistant:8080').rstrip('/')
        async with httpx.AsyncClient(base_url=url,timeout=120,trust_env=False) as client:
            try:
                exchange=await client.post('/api/auth/exchange',json={'gnos3_token':token});exchange.raise_for_status()
            except httpx.HTTPError:
                raise HTTPException(502,'Cannot sign in to Office for import. Check the module connection and shared SSO configuration.')
            headers={'Authorization':'Bearer '+exchange.json()['access_token']}
            try:
                manifest=await client.get('/api/knowledge-export',headers=headers);manifest.raise_for_status()
            except httpx.HTTPError:
                raise HTTPException(502,'Cannot read your saved Office files. Check the Office module is available.')
            sources=manifest.json()['files']
            if not isinstance(sources,list) or any(not isinstance(source,dict) or not isinstance(source.get('id'),str) or not isinstance(source.get('hash'),str) for source in sources):
                raise HTTPException(502,'Invalid Office manifest')
            knowledge_id=await private_knowledge(user,create=not auto or bool(sources))
            if not sources:
                removed=await remove_missing(knowledge_id,user,set()) if knowledge_id else 0
                return {'status':'empty','knowledge_id':knowledge_id,'files':0,'errors':0,'removed':removed}
            result={'status':'ready','knowledge_id':knowledge_id,'files':0,'errors':0,'failures':[]}
            for source in sources:
                if source.get('error'):
                    result['errors']+=1;result['failures'].append({'name':source.get('name','File'),'reason':source['error']});continue
                try:
                    async with asyncio.timeout(120):await import_file(request,client,headers,knowledge_id,user,source)
                    result['files']+=1
                except Exception:
                    result['errors']+=1
                    result['failures'].append({'name':source.get('name','File'),'reason':'Could not extract or index this file. Check the embedding service and retry.'})
                    log.exception('Office knowledge import failed user=%s source=%s',user.id,source['id'])
            result['removed']=await remove_missing(knowledge_id,user,{source['id'] for source in sources})
            if result['errors']:result['status']='partial'
            return result
