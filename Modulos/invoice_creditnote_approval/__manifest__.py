# -*- encoding: utf-8 -*-
{
	'name': u'Aprobaciones de notas de crédito',
	'category': 'sale',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['account_parametros_it'],
	'version':'1',
	'description':"""
		Aprobaciones de notas de crédito
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
		'views/invoice_creditnote_approval_view.xml',
		],
	'installable': True
}
