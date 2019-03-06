# -*- encoding: utf-8 -*-
{
    'name': 'Kardex x Plancha',
    'version': '1.0',
    'author': 'ITGRUPO-POLIGLASS',
    'website': '',
    'category': 'stock',
    'depends': ['import_base_it','stock_account','product','stock','mrp','purchase_requisition','kardex_campos_it','account_move_advanceadd_it','sale_stock','account_parametros_it'],
    'description': """KARDEX x Plancha""",
    'demo': [],
    'data': [
        'wizard/make_kardex_plancha_view.xml',

    ],
    'auto_install': False,
    'installable': True
}
