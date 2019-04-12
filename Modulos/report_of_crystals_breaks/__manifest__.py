# -*- encoding: utf-8 -*-
{
    'name': 'Reporte de Cristales Rotos',
    'category': 'report',
    'author': 'ITGRUPO-POLIGLASS',
    'depends': ['import_base_it','glass_production_order'],
    'version': '1.0',
    'description':"""
        Modulo para emitir el reporte de Cristales rotos en Fullglass
    """,
    'auto_install': False,
    'demo': [],
    'data':    [
        'wizard/report_of_breaks_wizard_view.xml',
        ],
    'installable': True
}