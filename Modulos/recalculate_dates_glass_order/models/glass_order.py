# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class GlassOrder(models.Model):
	_inherit='glass.order'

	@api.multi
	def get_form_postpone(self):

		dateprod = datetime.strptime(self.date_production.replace('-',''),'%Y%m%d').date()
		if dateprod.weekday()==5:
			dateprod = dateprod + timedelta(days=2)
		else:
			dateprod = dateprod + timedelta(days=1)

		wizard = self.env['postpone.op.wizard'].create({
			'date_production': dateprod
		})

		return {
			'name':'Postergar Fecha de OP',
			'res_id': wizard.id,
			'type': 'ir.actions.act_window',
			'res_model': 'postpone.op.wizard',
			'view_type': 'form',
			'view_mode': 'form',
			'views': [(False,'form')],
			'target':'new',
			#'context':{self.id}
		}
