# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Reporte guia de operaciones stock picking',
    'category': 'transport',
    'author': ' ITGRUPO-POLIGLASS',
    'version': '1.1',
    'description': """
    Agregar al reporte en PDF el campo transporte y guia de remision a stock.picking.operations

    """,
    'depends': ['stock'],
    'auto_install': False,
    'demo': [],
    'data': ['pdf_report_view.xml'],
    'installable': True
}
