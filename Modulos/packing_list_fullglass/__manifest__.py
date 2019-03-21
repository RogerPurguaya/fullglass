# -*- encoding: utf-8 -*-
{
	'name': 'Packing List for FullGlass',
	'category': 'production',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': [
	'stock','glass_production_order'],
	'version':'1',
	'description':"""
	Modulo para generar packing list en Fullglass
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'security/groups.xml',
		'security/ir.model.access.csv',
		'views/packing_list_view.xml',
		'views/packing_list_config_view.xml',
		'views/glass_order_line_packing_list.xml',
        ],
    # 'css': [
		# 'static/src/css/sheet.css'
		# ],
	'installable': True
}