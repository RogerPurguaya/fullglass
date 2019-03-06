# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
class SaleCalculatorProformaLine(models.Model):
	_inherit = 'sale.calculadora.proforma.line'

	production_id = fields.Many2one('glass.order')
	croquis = fields.Binary('Croquis')

	@api.multi
	def unlink(self):
		for line in self:
			if line.production_id:
				raise UserError(u"No se puede eliminar una línea que tiene asiganda una orden de producción")			
		return super(SaleCalculatorProformaLine,self).unlink()

class SaleCalculatorProforma(models.Model):
	_inherit = 'sale.calculadora.proforma'

	@api.one
	def getprevals(self,vals):
		prev_vals = []
		ids_changes = []
		lineref=False
		if self._context.get('active_model',False):
			if self._context.get('active_model')=='sale.order.line':
				if self._context.get('active_id',False):
					lineref = self.env['sale.order.line'].browse(self._context.get('active_id'))
			else:
				if self._context.get('active_model')=='sale.calculadora.proforma.line':
					if self._context.get('id_calc',False):
						lineref = self.env['sale.order.line'].search([('id_type','=',self._context.get('id_calc',False))])
		
		if lineref:

			if 'id_line' in vals:
				for line in vals['id_line']:
					if line[0] in [1]:
						ids_changes.append(line[1])

			actuales=self
			for line in actuales.id_line:
				if line.id in ids_changes:
					continue
				if line.production_id and lineref.order_id.before_invoice:
					continue
				cadnro = line.nro_cristal
				ncant=0
				if cadnro:
					if ',' not in cadnro:
						acadnro = cadnro.split('-')
						if len(acadnro)>1:					
							nini = int(acadnro[0])			
							nend = int(acadnro[1])+1
							for a in range(nini,nend):
								prev_vals.append(str(a))
						else:
							prev_vals.append(str(acadnro[0]))
					else:
						acadnro = cadnro.split(',')
						if len(acadnro)>0 and self.cantidad:
							for a in acadnro:
								prev_vals.append(str(a))

		return prev_vals
	@api.one
	def write(self,vals):
		res = super(SaleCalculatorProforma,self).write(vals)

		lsta=[]
		allprod = False
		havecalc=False
		allprod=True
		nonequal = []

		lineref=False

		if self._context.get('active_model',False):
			if self._context.get('active_model')=='sale.order.line':
				if self._context.get('active_id',False):
					lineref = self.env['sale.order.line'].browse(self._context.get('active_id'))
			else:
				if self._context.get('active_model')=='sale.calculadora.proforma.line':
					if self._context.get('id_calc',False):
						lineref = self.env['sale.order.line'].search([('id_type','=',self._context.get('id_calc',False))])
		if lineref:
			for line in lineref.order_id.order_line:
				if line.id_type:
					for detacalc in line.id_type_line:
						havecalc=True
						if detacalc.production_id:
							lsta.append(detacalc.production_id.id)
					if line.id_type.qty_invoiced_rest!=0:
						nonequal.append(1)
			if len(nonequal)>0:
				allprod=False
			if havecalc:
				if allprod:
					lineref.order_id.op_control='OP GENERADA'
				else:
					if len(lsta)==0:
						lineref.order_id.op_control='OP PENDIENTE'	
					else:
						lineref.order_id.op_control='OP PARCIAL'
			else:
				lineref.order_id.op_control='NO APLICA'
		return res


	@api.model
	def create(self,vals):
		res = super(SaleCalculatorProforma,self).create(vals)

		lsta=[]
		allprod = False
		havecalc=False
		allprod=True
		nonequal = []

		lineref=False

		lineref=self.env['sale.order.line'].browse(self._context['active_id'])
		if lineref:
			for line in lineref.order_id.order_line:
				if line.id_type:
					for detacalc in line.id_type_line:
						havecalc=True
						if detacalc.production_id:
							lsta.append(detacalc.production_id.id)
					if line.id_type.qty_invoiced_rest!=0:
						nonequal.append(1)
			if len(nonequal)>0:
				allprod=False
			if havecalc:
				if allprod:
					lineref.order_id.op_control='OP GENERADA'
				else:
					if len(lsta)==0:
						lineref.order_id.op_control='OP PENDIENTE'	
					else:
						lineref.order_id.op_control='OP PARCIAL'
			else:
				lineref.order_id.op_control='NO APLICA'
		return res
