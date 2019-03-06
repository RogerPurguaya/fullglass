# -*- coding: utf-8 -*-
from odoo import api ,models,fields


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"

	calculator_txt = fields.Char('Calculadora Linea',compute="get_calculador_txt")

	@api.one
	def get_calculador_txt(self):
		rpt = ''
		for i in self.id_type_line:
			rpt += i.nro_cristal +'('+ str(i.base1)+'x'+ str(i.altura1)+')'
		if rpt == '':
			rpt = False
		self.calculator_txt = rpt
