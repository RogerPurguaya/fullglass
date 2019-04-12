# -*- coding: utf-8 -*-
{
    'name': u"Config for Payment Terms Conditions - Fullglass",

    'description': """
        Modulo para agregar configuración de condiciones a los terminos de pago en un Pedido de venta
    """,

    'author': "ITGRUPO-POLIGLASS",
    'category': 'Extended functions',
    'version': '0.1',
    'depends': ['base', 'sale','sales_team'],
    'auto_install': False,
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/config_payment_term_view.xml',
    ],
    'installable': True
}
