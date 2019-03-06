# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassMakeUom(models.TransientModel):
	_name='glass.make.uom'

	alto=fields.Float('Alto',digits=(12,2))
	ancho=fields.Float('Ancho',digits=(12,2))

	@api.one
	def makeunit(self):
		config_data = self.env['glass.order.config'].search([])
		
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		
		if config_data.uom_categ_id==False:
			raise UserError(u'No se encontraron en los valores de configuración la categoría de unidad por defecto')		

		vals ={
			'name':str(self.ancho)+"x"+str(self.alto)+"mm",
			'uom_type':'bigger',
			'factor_inv':(self.alto*self.ancho)/1000000,
			'is_retazo':True,
			'ancho':self.ancho,
			'alto':self.alto,
			'category_id':config_data.uom_categ_id.id
		}
		self.env['product.uom'].create(vals)
		