# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta

class ProductProduct(models.Model):
	_inherit='product.template'
	type_materia_prod = fields.Char(u"Código Tipo Material")
	optima_trim = fields.Integer('Optima Trim', default=15)

class ProductProduct(models.Model):
	_inherit='product.product'
	@api.multi
	def name_get(self):
		aresult=[]
		result=super(ProductProduct,self).name_get()
		for r in result:
			pt = self.browse(r[0])
			if pt.uom_id.is_retazo:
				cad=r[1]+" ["+pt.uom_id.name+"] - R"
				aresult.append((pt.id,cad))
			else:
				if pt.uom_id.plancha:
					cad=r[1]+" ["+pt.uom_id.name+"]"
					aresult.append((pt.id,cad))
				else:
					aresult.append(r)
		return aresult

