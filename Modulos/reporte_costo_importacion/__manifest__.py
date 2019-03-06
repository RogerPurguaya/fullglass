# -*- encoding: utf-8 -*-
{
    'name': 'Reporte Costo Importacion',
    'version': '1.0',
    'author': 'ITGRUPO-POLIGLASS',
    'website': '',
    'category': 'stock',
    'depends': ['import_base_it','stock_account','product','stock','mrp','purchase_requisition','kardex_campos_it','account_move_advanceadd_it','sale_stock','account_parametros_it'],
    'description': """Calcula Costo de Importacion""",
    'demo': [],
    'data': [
        'wizard/make_costo_importacion_view.xml',

    ],
    'auto_install': False,
    'installable': True
}
