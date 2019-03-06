# -*- encoding: utf-8 -*-
{
	'name': 'Envio de Logs a Emails de Usuarios',
	'category': 'production',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['base','glass_production_order','res_partner_it'],
	'version':'1',
	'description':"""
		Modulo para el envio de eventos (roturas, cancelaciones etc.) a los emails de los usuarios seleccionados.
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/glass_order_config_extended_view.xml',
        ],
	'installable': True
}
