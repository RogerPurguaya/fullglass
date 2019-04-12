# -*- encoding: utf-8 -*-
{
	'name': 'Remover Orden de Produccion',
	'category': 'production',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['sale_calculadora_it',
	'kardex_it',
	'kardex_product_saldofisico_it',
	'unidad_medida_it',
	'stock','custom_glass_locations'],
	'version':'1',
	'description':"""
		Ordenes de produccion Glass
		install poppler 
		Windows https://blog.alivate.com.au/poppler-windows/ and add bin folder to path
		In linux: apt-get install poppler
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/groups.xml',
		'glass_remove_order_view.xml'
		]
    'css': [
		'static/src/css/sheet.css'
		],
	'installable': True
}