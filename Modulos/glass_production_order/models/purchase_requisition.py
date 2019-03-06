# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError


class PurchaseRequisitionLine(models.Model):
	_inherit = 'purchase.requisition.line'

	description = fields.Char(u'Descripción')

class PurchaseRequisition(models.Model):
	_inherit = 'purchase.requisition'	
	
	sketch = fields.Binary('Croquis')
	file_name = fields.Char("Archivo")