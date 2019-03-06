# -*- encoding: utf-8 -*-
{
	'name': 'Recalcular Fechas de OP',
	'category': 'production',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['base','glass_production_order','send_events_to_users_emails'],
	'version':'1',
	'description':"""
		Modulo para recalcular las fechas de una orden de produccion (OP)
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/glass_order_extended_view.xml',
		'views/postpone_op_wizard_form_view.xml',
        ],
	'installable': True
}
