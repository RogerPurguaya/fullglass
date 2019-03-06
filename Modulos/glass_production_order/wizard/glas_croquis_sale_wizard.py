# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassCroquisSaleWizard(models.TransientModel):
	_name='glass.croquis.sale.wizard'

	production_id=fields.Many2one('glass.order',u'Orden de producción')
	sale_id = fields.Many2one('sale.order','Venta')
	partner_id = fields.Many2one('res.partner','Cliente',related="sale_id.partner_id")
	is_editable =fields.Boolean('editable')
	file_crokis = fields.Binary('Croquis')

	@api.onchange('production_id')
	def onchange_production(self):
		if self.production_id:
			self.is_editable = self.production_id.editable_croquis
			self.file_crokis = self.production_id.sketch

	@api.one
	def savecroquis(self):
		if self.file_crokis:
			self.is_editable = False
			self.production_id.sketch = self.file_crokis
		return True

	@api.model
	def default_get(self,fields):
		res = super(GlassCroquisSaleWizard,self).default_get(fields)
		sale_id = self._context['active_id']
		res.update({
			'sale_id':sale_id,
			})
		return res