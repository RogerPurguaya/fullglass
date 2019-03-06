# -*- encoding: utf-8 -*-
{
    'name': 'Reporte Ordenes de Requisicion',
    'category': 'report',
    'author': 'ITGRUPO-POLIGLASS',
    'depends': ['import_base_it','glass_production_order','glass_reporte_procesos'],
    'version': '1.0',
    'description':"""
        Modulo para emitir el reporte de Ordenes de Requisicion en Fullglass
    """,
    'auto_install': False,
    'demo': [],
    'data':    [
        'wizard/report_of_requisitions_orders_view.xml',
        ],
    'installable': True
}