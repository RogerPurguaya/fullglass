# -*- encoding: utf-8 -*-
{
    'name': 'Reporte de seguimiento global de la produccion',
    'category': 'report',
    'author': 'ITGRUPO-POLIGLASS',
    'depends': ['import_base_it','glass_production_order'],
    'version': '1.0',
    'description':"""
        Modulo para emitir el reporte Seguimiento General de la produccion en Fullglass
    """,
    'auto_install': False,
    'demo': [],
    'data':    [
        'wizard/report_production_tracing_wizard_view.xml',
        ],
    'installable': True
}