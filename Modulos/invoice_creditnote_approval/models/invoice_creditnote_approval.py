# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from openerp.exceptions import ValidationError

class account_invoice(models.Model):
	_inherit="account.invoice"

	aproval_ids = fields.One2many('invoice.creditnote.approval','invoice_id',"Aprobaciones")
	@api.model
	def create(self,vals):
		res = super(account_invoice,self).create(vals)
		if res.type == 'out_refund':
			validacion = self.env['invoice.creditnote.approval.conf'].search([])
			print validacion
			for i in validacion:
				data={
					'orden':i.orden,
					'descripcion':i.descripcion,
					'invoice_id':res.id,
				}
				creation = self.env['invoice.creditnote.approval'].create(data)
		return res

	@api.multi
	def action_invoice_open(self):
		if self.type=='out_refund':
			aprobado = True
			for aprobal in self.aproval_ids:
				print aprobal.fecha
				if not aprobal.fecha:
					aprobado = False
					break
			if aprobado:
				res = super(account_invoice,self).action_invoice_open()
			else:
				raise ValidationError('Tiene aprobaciones pendientes, no se puede validar')				
		else:
			res = super(account_invoice,self).action_invoice_open()
		return res

class invoice_creditnote_approval(models.Model):
	_name = 'invoice.creditnote.approval'

	orden = fields.Integer('Orden')
	descripcion = fields.Char(u'Descripción')
	fecha = fields.Date('Fecha')
	is_usuario = fields.Boolean('Is',compute='get_is_usuario')
	invoice_id = fields.Many2one('account.invoice','Contenedor')
	fecha_d = fields.Date('Fecha D')

	_order = 'orden'

	@api.model
	def create(self,vals):
		t = super(invoice_creditnote_approval,self).create(vals)
		if t.orden == 1:
			t.enviar_correo()
		return t

	@api.one
	def write(self,vals):
		if 'fecha' in vals:
			vals['fecha_d'] = vals['fecha']
		t = super(invoice_creditnote_approval,self).write(vals)
		if 'fecha' in vals:
			self.enviar_next()
		return t

	@api.multi
	def enviar_correo(self):
		aprobacion_conf = self.env['invoice.creditnote.approval.conf'].search([('descripcion','=',self.descripcion)])
		print self.descripcion
		if len(aprobacion_conf)>0:
			aprobacion_conf = aprobacion_conf[0]
		base_url = self.env['ir.config_parameter'].get_param('web.base.url')
		query = {'db': self.env.cr.dbname}

		for i in aprobacion_conf.usuario:
			cadurl = base_url+"/web?#view_type=form&id="+str(self.invoice_id.id)+"&type=signup&model=purchase.requisition"
			urld = self.invoice_id.number
			if not self.invoice_id.number:
				urld=self.invoice_id.reference 
			body = """Estimado(a) """ + (aprobacion_conf.descripcion if aprobacion_conf.descripcion else '') + ": " + ( i.name if i.name else '' )+ """ <br/>
			Debe de Evaluar o Rechazar el <a href=""" +cadurl+""">"""+ urld+ """</a><br/>
			Atte.<br/>
			El equipo ODOO
						"""
			mail_values = {
				'subject': "Factura Rectificativa "+self.invoice_id.number if self.invoice_id.number else self.invoice_id.reference,
				'body_html': body,
				'email_to': i.partner_id.email,
				'email_from': self.env['res.company'].search([])[0].partner_id.email,
	   		}
			create_and_send_email = self.env['mail.mail'].create(mail_values).send() 

	@api.one
	def enviar_next(self):
		otros = self.env['invoice.creditnote.approval'].search([('invoice_id','=',self.invoice_id.id),('orden','>',self.orden),('fecha','=',False)]).sorted(key=lambda r: r.orden)
		if len(otros)>0:
			otros= otros[0]
			otros.enviar_correo()


	@api.one
	def get_is_usuario(self):
		aprobacion_conf = self.env['invoice.creditnote.approval.conf'].search([('descripcion','=',self.descripcion)])
		if len(aprobacion_conf)>0:
			aprobacion_conf = aprobacion_conf[0]

		otros = self.env['invoice.creditnote.approval'].search([('invoice_id','=',self.invoice_id.id),('orden','<',self.orden),('fecha','=',False)])
		if len(otros)>0:
			self.is_usuario = False
		else:
			self.is_usuario = True if self.env.uid in aprobacion_conf.usuario.ids else False
	
class invoice_creditnote_approval_conf(models.Model):
	_name = 'invoice.creditnote.approval.conf'

	orden = fields.Integer('Orden')
	usuario = fields.Many2many('res.users','users_aprobaciones_rel','users_id','aprobacion_id','Usuario')
	descripcion = fields.Char(u'Descripción')
	_order = 'orden'