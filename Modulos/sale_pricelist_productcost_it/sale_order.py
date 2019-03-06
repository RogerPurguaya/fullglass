# -*- coding: utf-8 -*-
from odoo import api ,models,fields
class SaleOrder(models.Model):
	_inherit = "sale.order"

	@api.onchange('pricelist_id')
	def onchagepricelist(self):
		res = {}
		if self.pricelist_id:
			categ= self.pricelist_id.categ_client
			if categ:
				res = {'domain':{'pricelist_id':[('categ_client','=',categ)]}}			
		return res