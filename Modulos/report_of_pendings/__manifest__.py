# -*- encoding: utf-8 -*-
{
    'name': 'Reporte de Pendientes - Fullglass',
    'category': 'report',
    'author': 'ITGRUPO-POLIGLASS',
    'depends': ['import_base_it','glass_production_order'],
    'version': '1.0',
    'description':"""
        Modulo para emitir el reporte de Pendientes en Fullglass
    """,
    'auto_install': False,
    'demo': [],
    'data':    [
        'wizard/report_of_pendings_wizard_view.xml',
        ],
    'installable': True
}