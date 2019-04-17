# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Reporte vale de entregas de stock picking',
    'category': 'deliveryslip',
    'author': ' ITGRUPO-POLIGLASS',
    'version': '1.1',
    'description': """
    Agregar al reporte en PDF el campo transporte y guia de remision de stock picking

    """,
    'depends': ['stock','reporte_vale_entrega'],
    'auto_install': False,
    'demo': [],
    'data': ['pdf_report_view.xml'],
    'installable': True
}
