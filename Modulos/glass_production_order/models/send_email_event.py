
# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _, exceptions
from datetime import datetime,timedelta
import re
import time
import collections
import base64

class SendEmailModel(models.Model):
	_name = 'send.email.event'
	subject = fields.Char('Asunto', default='Sin Asunto')
	message = fields.Text('Mensaje', default='Nuevo Mensaje')
	@api.multi
	def send_emails(self,motive=None):
		motive_obj = self.env['motive.event.send.email'].search([('motive','=',motive)])
		if len(motive_obj) == 0:
			raise exceptions.Warning('El motivo '+ str(motive) + ' no ha sido configurado.')
		
		emails = map(lambda x: x.email, motive_obj.users_ids)
		sends = []
		sends = 0
		for user in motive_obj.users_ids:
			email_data = {
						'subject': self.subject,
						'body_html':'Estimado (a) '+user.name+',<br/>' + str(self.message),
						'email_to': user.email
						}
			email = self.env['mail.mail'].create(email_data)
			email_sended = email.send()
			if email_sended:
				sends += 1

		if sends != len(motive_obj.users_ids):
			return {
				'warning':{
					'title':'No todos los emails fueron entregados',
					'message':'Es posible que algunos emails de Reprogramacion de OP \n no hayan llegado a los destinatarios: \n'
				}
			}
		else:
			return {
				'warning':{
					'title':'Envios Realizados con Exito',
					'message':'Los emails de Reprogramacion de OP \n han sido enviados  los destinatarios encargados.'
				}
			} 

class MotiveEvent(models.Model):
	_name = 'motive.event.send.email'
	config_id = fields.Many2one('glass.order.config',string='Configuracion')
	motive = fields.Selection([
		('reprograming_op','Reprogramacion de OP'),
		('break_crystal','Rotura de Cristal'),
		('op_returned','Devolucion de OP')],string='Motivo')
	description = fields.Text(string='Descripcion')
	## Usuarios  de reprogramacion:
	users_ids = fields.Many2many('res.partner','motive_send_email_res_users_rel','motive_id','user_id',string='Usuarios')

	@api.constrains('motive')
	def _verify_not_repeat_motive(self):
		motives = list(filter(lambda x: x.motive == self.motive,self.config_id.motive_event_send_email_ids))
		if len(motives) > 1:
			raise exceptions.Warning('El motivo ingresado ya existe para esta configuracion')

class ResPartner(models.Model):
	_inherit = 'res.partner'
	motive_send_email_ids = fields.Many2many('motive.event.send.email','motive_send_email_res_users_rel','user_id','motive_id',string='Motivos envio de email')