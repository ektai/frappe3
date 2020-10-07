# -*- coding: utf-8 -*-
# Copyright (c) 2019, Frappe Technologies and Contributors
# See license.txt
from __future__ import unicode_literals

import frappe
import unittest
import requests
from frappe.utils import get_url

scripts = [
	dict(
		name='test_todo',
		script_type = 'DocType Event',
		doctype_event = 'Before Insert',
		reference_doctype = 'ToDo',
		script = '''
if "test" in doc.description:
	doc.status = 'Closed'
'''
	),
	dict(
		name='test_todo_validate',
		script_type = 'DocType Event',
		doctype_event = 'Before Insert',
		reference_doctype = 'ToDo',
		script = '''
if "validate" in doc.description:
	raise frappe.ValidationError
'''
	),
	dict(
		name='test_api',
		script_type = 'API',
		api_method = 'test_server_script',
		allow_guest = 1,
		script = '''
frappe.response['message'] = 'hello'
'''
	)
]
class TestServerScript(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.db.commit()
		frappe.db.sql('truncate `tabServer Script`')
		frappe.get_doc('User', 'Administrator').add_roles('Script Manager')
		for script in scripts:
			script_doc = frappe.get_doc(doctype ='Server Script')
			script_doc.update(script)
			script_doc.insert()

		frappe.db.commit()

	@classmethod
	def tearDownClass(cls):
		docs = frappe.get_all("Server Script")
		for doc in docs:
			frappe.delete_doc("Server Script", doc.name)

	def setUp(self):
		frappe.cache().delete_value('server_script_map')

	def test_doctype_event(self):
		todo = frappe.get_doc(dict(doctype='ToDo', description='hello')).insert()
		self.assertEqual(todo.status, 'Open')

		todo = frappe.get_doc(dict(doctype='ToDo', description='test todo')).insert()
		self.assertEqual(todo.status, 'Closed')

		self.assertRaises(frappe.ValidationError, frappe.get_doc(dict(doctype='ToDo', description='validate me')).insert)

	def test_api(self):
		response = requests.post(get_url() + "/api/method/test_server_script")
		self.assertEqual(response.status_code, 200)
		self.assertEqual("hello", response.json()["message"])