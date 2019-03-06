# -*- encoding: utf-8 -*-
{
	'name': 'Calculadora de Cotizaciones',
	'category': 'sale',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['sale','account','sale_order_contact'],
	'version':'1',
	'description':"""
	Calculdade Cotizaciones para productos de Venta
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/ir.model.access.csv',
		'views/sale_calculadora_view.xml',
		'views/product_view.xml',
		'views/custom_keyboard_shortcuts.xml'
        ],
    # 'css': ['static/src/css/modalg.css'],
	'installable': True
}
