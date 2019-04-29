
{
    'name': 'Initial Inventory Scraps Importer',
    'version': '10',
    'license': 'AGPL-3',
    'author': 'ITGRUPO-POLIGLASS',
    'website': 'http://www.noviat.com',
    'category': 'Production',
    'summary': """
    Importador de retazos para Inventario inicial en Fullglass 
    """,
    'depends': ['stock','glass_production_order'],
    'data': [
        'wizard/scraps_import_view_wizard.xml',
    ],
    'demo': [
        #'demo/account_move.xml',
    ],
    'installable': True,
}
