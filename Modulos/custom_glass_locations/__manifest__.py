# -*- coding: utf-8 -*-
{
    'name': u"Custom Locations Fullglass",

    'description': """
        Modulo para agregar Ubicaciones personalizadas en fullglass
    """,

    'author': "ITGRUPO-POLIGLASS",
    'category': 'Extended functions',
    'version': '0.1',
    'depends': ['base', 'stock'],
    'auto_install': False,
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/custom_glass_location_view.xml',
    ],
    'installable': True
}
