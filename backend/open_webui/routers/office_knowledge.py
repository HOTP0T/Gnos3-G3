"""Explicit current-user Office import. No all-user job and no deletion reconciliation."""
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
    defaults=request.app.state.config.USER_PERMISSIONS
    return await has_permission(user.id,'modules.office.read',defaults) and await has_permission(user.id,'workspace.knowledge',defaults)

async def private_knowledge(user):
    identity=str(uuid.uuid5(uuid.NAMESPACE_URL,'gnos3-office-knowledge:'+user.id))
    async with get_async_db_context() as db:
        row=await db.get(Knowledge,identity)
        if row and (row.user_id!=user.id or (row.meta or {}).get('office_module') is not True):
            raise RuntimeError('Office knowledge identity conflict')
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
    bypass=request.app.state.config.BYPASS_EMBEDDING_AND_RETRIEVAL
    if existing and (existing.meta or {}).get('office_synced_hash')==source['hash'] and (existing.meta or {}).get('office_sync_status') in ('ready','empty') and await Knowledges.has_file(knowledge_id,file_id):
        # Older imports indexed only the knowledge base. A #file reference uses
        # its own file-<id> collection, so unchanged legacy files need repair.
        text=(existing.data or {}).get('content','')
        if bypass or not text.strip() or (await ASYNC_VECTOR_DB_CLIENT.has_collection(f'file-{file_id}') and await ASYNC_VECTOR_DB_CLIENT.has_collection(knowledge_id)):
            return
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
            # Follow the standard upload -> knowledge flow. Supplying content
            # directly to the knowledge call deletes the individual file index.
            async with get_async_db_context() as db:
                await process_file(request,ProcessFileForm(file_id=file_id,content=content),user=user,db=db)
            if await ASYNC_VECTOR_DB_CLIENT.has_collection(knowledge_id):
                await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=knowledge_id,filter={'file_id':file_id})
            if not bypass:
                async with get_async_db_context() as db:
                    await process_file(request,ProcessFileForm(file_id=file_id,collection_name=knowledge_id),user=user,db=db)
        else:
            # An emptied file must not leave old text available to #file.
            if await ASYNC_VECTOR_DB_CLIENT.has_collection(f'file-{file_id}'):
                await ASYNC_VECTOR_DB_CLIENT.delete_collection(collection_name=f'file-{file_id}')
            if await ASYNC_VECTOR_DB_CLIENT.has_collection(knowledge_id):
                await ASYNC_VECTOR_DB_CLIENT.delete(collection_name=knowledge_id,filter={'file_id':file_id})
        await update_meta(file_id,user,{'office_synced_hash':source['hash'],'office_sync_status':'ready' if content.strip() else 'empty','office_sync_error':None})
    except Exception:
        await update_meta(file_id,user,{'office_sync_status':'failed','office_sync_error':'Indexing failed. Try Sync my Office files again.'})
        raise
    # Existing uploads and files removed from Office are retained. No data cleanup here.

@router.post('/sync')
async def synchronize(request:Request,user=Depends(get_verified_user)):
    if not await permitted(request,user):raise HTTPException(403,'Office and knowledge workspace access are required')
    lock=locks.setdefault(user.id,asyncio.Lock())
    if lock.locked():raise HTTPException(409,'Your Office files are already being imported')
    async with lock:
        token,_=create_k4mi_exchange_token(user,audience='gnos3-module:office')
        url=os.environ.get('OFFICE_MODULE_URL','http://office-api:8004').rstrip('/')
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
            knowledge_id=await private_knowledge(user)
            if not sources:return {'status':'empty','knowledge_id':knowledge_id,'files':0,'errors':0}
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
            if result['errors']:result['status']='partial'
            return result
