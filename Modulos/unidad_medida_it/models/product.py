# -*- coding: utf-8 -*-

from odoo import models, fields, api

class product_uom(models.Model):
	_inherit = 'product.uom'

	plancha = fields.Boolean('Plancha')
	ancho = fields.Float('Ancho (mm)') 
	alto = fields.Float('Alto (mm)')

	@api.onchange('plancha','ancho','alto')
	def onchange_paa(self):
		if self.plancha:
			self.uom_type = 'bigger'
			self.factor_inv = (self.ancho * self.alto) / 1000000

