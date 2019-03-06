# -*- encoding: utf-8 -*-
{
	'name': 'Sale Order Line Limit Discount',
	'category': 'sale',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['import_base_it'],
	'version':'1',
	'description':"""
		Define limite de descuento realizable basado en:
		-Tarifas
		-Usuarios
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'views/sale_order_line_limit_discount_view.xml',
		],
	'installable': True
}
