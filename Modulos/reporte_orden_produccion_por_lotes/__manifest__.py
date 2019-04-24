# -*- encoding: utf-8 -*-
{
	'name': u'Reporte Orden Produccion para almacén',
	'category': 'reports',
	'author': 'ITGRUPO-POLIGLASS',
	'depends': ['glass_production_order','stock'],
	'version': '1.0.0',
	'description':"""
	Módulo que habilita el el action menu para emitir el reporte de orden de producción(nuevo, basado en los lotes de producción)
	""",
	'auto_install': False,
	'demo': [],
	'data':	[
		'wizard/reporte_orden_produccion_wizard_view.xml',
		],
	'installable': True
}
