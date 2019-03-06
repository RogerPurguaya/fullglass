# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError


class ProductUom(models.Model):
	_inherit = 'product.uom'

	is_retazo = fields.Boolean('Retazo')

	@api.onchange('is_retazo','ancho','alto')
	def onchangeisretazo(self):
		newfactor=self.factor_inv
		if self.is_retazo:
			if self.ancho:
				if self.alto:
					newfactor = float(self.ancho*self.alto)/1000000
		print newfactor,self.ancho,self.alto
		return {'value':{'factor_inv':newfactor}}

	@api.multi
	def name_get(self):
		aresult=[]
		result=super(ProductUom,self).name_get()
		for r in result:
			pt = self.browse(r[0])
			if pt.is_retazo:
				cad=r[1]+" - R"
				aresult.append((pt.id,cad))
			else:
				aresult.append(r)
		return aresult