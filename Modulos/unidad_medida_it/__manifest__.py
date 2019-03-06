# -*- coding: utf-8 -*-
{
    'name': "product_product_it_codigo",

    'description': """
        Long description of module's purpose
    """,

    'author': "ITGRUPO-POLIGLASS",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['kardex_it'],

    # always loaded
    'data': [
         'views/product_view.xml',
    ],
    # only loaded in demonstration mode
}
