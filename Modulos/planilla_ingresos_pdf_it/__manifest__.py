# -*- encoding: utf-8 -*-
{
	'name': 'Reporte de Diarios IT',
	'category': 'base',
	'author': 'ITGRUPO-POLYGLASS',
	'depends': ['import_base_it','account'],
	'version': '1.0.0',
	'description':"""
	Reporte de Caja
	""",
	'auto_install': False,
	'demo': [],
	'data':	['views/planilla_ingresos_pdf_reports.xml',
			'views/planilla_ingresos_pdf_template.xml',
			'views/inherit_view_account_payment.xml'],
	'installable': True
}
