
# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _, exceptions
from datetime import datetime
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