# -*- encoding: utf-8 -*-
{
	'name': 'Cash Settlement Report',
	'category': 'account',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['account','report'],
	'version':'1',
	'description':"""
	Reporte de Liquidación de Caja
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'wizard/account_report_print_cash_view.xml',
		'views/report_invoice_report.xml',
		'views/report_invoice.xml'],
	'installable': True
}
