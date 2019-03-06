# -*- encoding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassRemoveOrder(models.TransientModel):
	_name = 'glass.remove.order'

	date_remove = fields.Date('Fecha',default=datetime.now())
	motive_remove = fields.Char('Motivo')
	order_name = fields.Char(u'Orden de Producción')

	@api.model
	def default_get(self, default_fields):
		res = super(GlassRemoveOrder, self).default_get(default_fields)
		order = self.env['glass.order'].browse(self._context['active_id'])
		res.update({'order_name': order.name})
		return res
		
	@api.one
	def remove_order(self):

		active_obj = self.env['glass.order'].browse(self._context['active_id'])
		for line in active_obj.line_ids:
			if line.is_used:
				raise UserError(u'Uno o varios elementos de esta orden de producción ya se encuentran en los lotes de producción')		
		active_obj.message_post(body="Retirada<br/>Fecha: "+self.date_remove+"<br/>Motivo: "+self.motive_remove+"<br/>")
		active_obj.sale_order_id.message_post(body="OP retirada: <br/>Fecha: "+self.date_remove+"<br/>Motivo: "+self.motive_remove+"<br/>")
		active_obj.sale_order_id.action_cancel()
		active_obj.sale_order_id.action_draft()
		for line in active_obj.line_ids:
			line.unlink()
		
		return True



