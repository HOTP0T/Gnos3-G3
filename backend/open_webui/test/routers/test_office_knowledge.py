"""Exercise the real sync function with isolated storage/vector boundaries.

No application startup, live database, source records or model requests are used.
The process_file double models its content-update deletion of file-<id> indexes.
"""
import ast
import asyncio
import base64
from contextlib import asynccontextmanager
import hashlib
import io
import mimetypes
from pathlib import Path
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch
import uuid


ROUTER = Path(__file__).resolve().parents[2] / 'routers' / 'office_knowledge.py'


class OfficeFileSourceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.user = SimpleNamespace(id='synthetic-owner', role='user')
        self.request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
            config=SimpleNamespace(BYPASS_EMBEDDING_AND_RETRIEVAL=False, USER_PERMISSIONS={})
        )))
        binary = b'Synthetic local Office file'
        self.source = {'id':'source-one', 'hash':hashlib.sha256(binary).hexdigest(),
                       'name':'Example.docx', 'path':'Example.docx'}
        self.file_id = str(uuid.uuid5(uuid.NAMESPACE_URL,
            'gnos3-office-file:' + self.user.id + ':' + self.source['id']))
        self.file_collection = 'file-' + self.file_id
        self.knowledge = 'synthetic-private-knowledge'
        self.collections = set()
        self.existing = None
        self.membership = False
        self.text = 'A synthetic document with traceable local text.'
        self.fail_knowledge = False
        self.processed = []
        self.permissions = AsyncMock(return_value=True)
        self.files = SimpleNamespace(
            get_file_by_id=AsyncMock(side_effect=lambda _: self.existing),
            insert_new_file=AsyncMock(return_value=SimpleNamespace(id=self.file_id)),
            update_file_data_by_id=AsyncMock(),
        )
        self.knowledges = SimpleNamespace(
            has_file=AsyncMock(side_effect=lambda *_: self.membership),
            add_file_to_knowledge_by_id=AsyncMock(),
        )

        async def delete_collection(*, collection_name):
            self.collections.discard(collection_name)

        self.vectors = SimpleNamespace(
            has_collection=AsyncMock(side_effect=lambda name: name in self.collections),
            delete=AsyncMock(), delete_collection=AsyncMock(side_effect=delete_collection),
        )

        async def process_file(request, form, user, db):
            self.processed.append(form)
            if form.content:
                self.collections.discard(self.file_collection)
            if form.collection_name:
                if self.fail_knowledge:
                    raise RuntimeError('Synthetic knowledge indexing failure')
                if not form.content:
                    self.assertIn(self.file_collection, self.collections)
            if not request.app.state.config.BYPASS_EMBEDDING_AND_RETRIEVAL:
                self.collections.add(form.collection_name or self.file_collection)

        retrieval = ModuleType('open_webui.routers.retrieval')
        retrieval.process_file = process_file
        def form(**kw):
            return SimpleNamespace(**{'content':None, 'collection_name':None, **kw})
        retrieval.ProcessFileForm = form
        vector_module = ModuleType('open_webui.retrieval.vector.async_client')
        vector_module.ASYNC_VECTOR_DB_CLIENT = self.vectors
        modules = patch.dict('sys.modules', {
            'open_webui.routers.retrieval':retrieval,
            'open_webui.retrieval.vector.async_client':vector_module,
        })
        modules.start(); self.addCleanup(modules.stop)

        @asynccontextmanager
        async def database():
            yield object()

        self.update_meta = AsyncMock()
        self.storage = SimpleNamespace(upload_file=Mock(return_value=(binary, '/synthetic/upload.docx')))
        namespace = dict(asyncio=asyncio, base64=base64, hashlib=hashlib, io=io,
            mimetypes=mimetypes, uuid=uuid, Path=Path, Files=self.files,
            FileForm=lambda **kw:SimpleNamespace(**kw), Knowledges=self.knowledges,
            Storage=self.storage, update_meta=self.update_meta,
            get_async_db_context=database, has_permission=self.permissions)
        tree = ast.parse(ROUTER.read_text())
        functions = [n for n in tree.body if isinstance(n, ast.AsyncFunctionDef)
                     and n.name in ('import_file','permitted')]
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(ROUTER), 'exec'), namespace)
        self.import_file, self.permitted = namespace['import_file'], namespace['permitted']
        response = SimpleNamespace(raise_for_status=lambda:None,
            json=lambda:{'dataBase64':base64.b64encode(binary).decode(), 'text':self.text})
        self.client = SimpleNamespace(get=AsyncMock(return_value=response))

    def legacy_file(self, status='ready'):
        self.existing = SimpleNamespace(user_id=self.user.id, data={'content':self.text}, meta={
            'office_source_id':self.source['id'], 'office_synced_hash':self.source['hash'],
            'office_sync_status':status})
        self.membership = True
        self.collections.add(self.knowledge)

    async def sync(self):
        await self.import_file(self.request, self.client, {}, self.knowledge, self.user, self.source)

    async def test_new_import_indexes_individual_file_before_knowledge(self):
        await self.sync()
        self.assertEqual(len(self.processed), 2)
        self.assertEqual(self.processed[0].content, self.text)
        self.assertIsNone(self.processed[0].collection_name)
        self.assertIsNone(self.processed[1].content)
        self.assertEqual(self.processed[1].collection_name, self.knowledge)
        self.assertEqual(self.collections, {self.file_collection, self.knowledge})
        self.assertEqual(self.update_meta.await_args.args[2]['office_sync_status'], 'ready')

    async def test_unchanged_legacy_import_repairs_missing_file_index(self):
        self.legacy_file()
        await self.sync()
        self.assertIn(self.file_collection, self.collections)
        self.assertEqual(len(self.processed), 2)

    async def test_healthy_unchanged_file_skips_download_and_embedding(self):
        self.legacy_file(); self.collections.add(self.file_collection)
        await self.sync()
        self.client.get.assert_not_awaited()
        self.assertEqual(self.processed, [])

    async def test_failed_same_hash_import_is_retried(self):
        self.legacy_file('failed'); self.collections.add(self.file_collection)
        await self.sync()
        self.client.get.assert_awaited_once()
        self.assertEqual(len(self.processed), 2)

    async def test_empty_update_removes_stale_text_from_both_indexes(self):
        self.legacy_file(); self.collections.add(self.file_collection)
        self.existing.meta['office_synced_hash'] = 'outdated'
        self.text = ''
        await self.sync()
        self.assertNotIn(self.file_collection, self.collections)
        self.vectors.delete.assert_awaited_once_with(collection_name=self.knowledge, filter={'file_id':self.file_id})
        self.assertEqual(self.processed, [])
        self.assertEqual(self.update_meta.await_args.args[2]['office_sync_status'], 'empty')

    async def test_bypass_uses_saved_text_without_knowledge_vector_copy(self):
        self.request.app.state.config.BYPASS_EMBEDDING_AND_RETRIEVAL = True
        await self.sync()
        self.assertEqual(len(self.processed), 1)
        self.assertEqual(self.processed[0].content, self.text)
        self.assertEqual(self.collections, set())

    async def test_indexing_failure_remains_failed_and_retryable(self):
        self.fail_knowledge = True
        with self.assertRaisesRegex(RuntimeError, 'Synthetic knowledge'):
            await self.sync()
        self.assertIn(self.file_collection, self.collections)
        self.assertEqual(self.update_meta.await_args.args[2]['office_sync_status'], 'failed')

    async def test_foreign_file_identity_is_rejected_before_read_or_write(self):
        self.legacy_file(); self.existing.user_id = 'another-user'
        with self.assertRaisesRegex(RuntimeError, 'identity conflict'):
            await self.sync()
        self.client.get.assert_not_awaited()
        self.storage.upload_file.assert_not_called()

    async def test_normal_users_need_office_and_knowledge_permissions(self):
        self.permissions.side_effect = [True, False]
        self.assertFalse(await self.permitted(self.request, self.user))
        self.assertEqual([c.args[1] for c in self.permissions.await_args_list],
                         ['modules.office.read', 'workspace.knowledge'])


if __name__ == '__main__':
    unittest.main()
