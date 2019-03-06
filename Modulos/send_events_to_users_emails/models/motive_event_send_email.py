# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class MotiveEvent(models.Model):
	_name = 'motive.event.send.email'
	config_id = fields.Many2one('glass.order.config',string='Configuracion')
	motive = fields.Selection([('reprograming_op','Reprogramacion de OP'),('break_crystal','Rotura de Cristal')],string='Motivo')
	description = fields.Text(string='Descripcion')
	## Usuarios  de reprogramacion:
	users_ids = fields.Many2many('res.partner','motive_send_email_res_users_rel','motive_id','user_id',string='Usuarios')

	@api.constrains('motive')
	def _verify_not_repeat_motive(self):
		motives = list(filter(lambda x: x.motive == self.motive,self.config_id.motive_event_send_email_ids))
		if len(motives) > 1:
			raise UserError('El motivo ingresado ya existe para esta configuracion')

class GlassOrderConfig(models.Model):
	_inherit='glass.order.config'
	motive_event_send_email_ids = fields.One2many('motive.event.send.email','config_id',string='Motivos de Envio de Emails')


class ResPartner(models.Model):
	_inherit = 'res.partner'
	motive_send_email_ids = fields.Many2many('motive.event.send.email','motive_send_email_res_users_rel','user_id','motive_id',string='Motivos envio de email')


