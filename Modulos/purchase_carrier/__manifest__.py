# -*- encoding: utf-8 -*-
{
	'name': 'Purchase Carrier',
	'category': 'account',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['import_base_it'],
	'version':'1.0',
	'description':"""
	- Adiciona un campo de transportista a cada Pedido de compra
	- Adiciona automaticamente el nro de Ruc en la pagina de Transportista
	- Adiciona nombre, ruc de transportista a reporte de compra
	""",
	'auto_install': False,
	'demo': [],
	'data':	['views/purchase_order_view.xml'],
	'installable': True
}
