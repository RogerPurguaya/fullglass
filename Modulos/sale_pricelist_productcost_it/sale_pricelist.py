# -*- coding: utf-8 -*-
from odoo import models,fields
class Pricelist(models.Model):
    _inherit = "product.pricelist"

    categ_client = fields.Selection([('categ_','A'),
    	('categ_b','B'),
    	('categ_c','C'),
    	('categ_d','D'),
    	('categ_e','E'),
    	],u'Categoría de Cliente')