# -*- encoding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassRemoveOrder(models.TransientModel):
	_name = 'glass.remove.order'

	date_remove = fields.Date('Fecha',default=datetime.now().date())
	motive_remove = fields.Char('Motivo')
	order_name = fields.Char(string='Orden de Produccion')

	@api.model
	def default_get(self, default_fields):
		res = super(GlassRemoveOrder, self).default_get(default_fields)
		order = self.env['glass.order'].browse(self._context['active_id'])
		res.update({'order_name': order.name})
		return res
		
	@api.one
	def remove_order(self):
		active_obj = self.env['glass.order'].browse(self._context['active_id'])
		used_lines = active_obj.line_ids.filtered(lambda x: x.is_used or x.lot_line_id)
		if len(used_lines) > 0:
			raise UserError(u'No se puede retirar la OP.\nUno o varios elementos de esta orden de producción ya se encuentran en los lotes de producción.')		

		active_obj.sale_order_id.action_cancel()
		active_obj.sale_order_id.action_draft()
		
		for line in active_obj.line_ids:
			line.unlink()
		
		active_obj.write({'state':'returned'})
		
		msg = 'El usuario '+self.env.user.name+' ha retirado la Orden de Produccion: ' + active_obj.name
		if self.motive_remove:
			msg += ' por el motivo: "'+ str(self.motive_remove).strip() + '"'
		if self.date_remove:
			msg += ', asignando la fecha: '+ str(self.date_remove) + '.'

		data = {
			'subject': 'Retiro de Orden de Produccion: ' + str(active_obj.name),
			'message': msg
		}

		sender = self.env['send.email.event'].create(data)
		res = sender.send_emails(motive='op_returned') 
		return res



