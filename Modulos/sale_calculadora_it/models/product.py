# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models,api, _
from odoo.exceptions import UserError

class ProductCategory(models.Model):
	_inherit = 'product.category'

	min_sale=fields.Float(u'Mínimo Vendible')
	uom_min_sale=fields.Many2one('product.uom',u'Unidad')
