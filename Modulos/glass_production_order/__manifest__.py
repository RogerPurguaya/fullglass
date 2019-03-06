# -*- encoding: utf-8 -*-
{
	'name': 'Ordenes de produccion Glass ',
	'category': 'production',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['sale_calculadora_it',
	'kardex_it',
	'kardex_product_saldofisico_it',
	'unidad_medida_it',
	'stock'],
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
		'security/ir.model.access.csv',
		'views/glass_order_view.xml',
		'views/glass_order_config_view.xml',
		'views/glass_lot_view.xml',
		'views/sale_order_view.xml',
		'wizard/glass_pool_wizard_view.xml',
		'wizard/glass_remove_order_view.xml',
		'wizard/glass_production_control_wizard_view.xml',
		'views/glass_production_in_tracking.xml',
		'views/glass_requisition_view.xml',
		'views/product_uom_view.xml',
		'wizard/glass_croquis_sale_wizard_view.xml',
		'wizard/modalmsg_view.xml',
		'wizard/sale_order_makeorder_view.xml',
		'views/purchase_requisition_view.xml',
		'views/glass_furnace_out_view.xml',
		'views/stock_move_view.xml',
		'views/glass_list_main_wizard_view.xml',
		'wizard/glass_in_production_wizard.xml',
		'wizard/glass_reprograming_wizard_view.xml',
		'report/glass_barcode_report.xml',
		'wizard/glass_make_uom_view.xml',
		'wizard/glass_in_stock_picking_show_details_wizard.xml',
		'wizard/show_detail_lines_entered_stock_wizard_view.xml',
		'views/stock_return_picking.xml',
        ],
    # 'css': ['static/src/css/modalg.css'],
	'installable': True
}
