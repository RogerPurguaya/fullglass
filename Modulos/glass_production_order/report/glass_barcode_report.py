# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassBarcodeReport(models.Model):
	_name='glass.barcode.report'

	order_name=fields.Char('O/P')
	cristal_number =fields.Char('Cristal Nro.')
	product_id = fields.Many2one('')