# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta

class GlassReprogramingWizard(models.TransientModel):
	_name='glass.reprograming.wizard'

	motive=fields.Char('Motivo')
	date = fields.Date('Fecha Reprogramada',default=datetime.now())

	@api.multi
	def reprogram(self):
		active_ids = self._context['active_ids']
		print self._context
		for lista in self.env['glass.list.wizard'].browse(active_ids):
			order = lista.order_id
			vals_wizard={}
			print order
			npiezas = 0
			tieneentalle = False

			for line in order.line_ids:
				npiezas=npiezas+1
				if line.entalle:
					tieneentalle=True

			config=self.env['glass.order.config'].search([])[0]
			limite = False
			for linec in config.limit_ids:
				if linec.motive_limit=='templado':
					limite = linec
			if not limite:
				raise UserError(u"No se ha encontra la configuración de plazos de producción")
			dias_prod = 0
			if npiezas<51:
				dias_prod = limite.zero_2_50
			if npiezas<101 and npiezas>50:
				dias_prod = limite.fifty_2_100
			if npiezas<201 and npiezas>101:
				dias_prod = limite.onehundred1_2_200
			if npiezas>200:
				dias_prod = limite.more_2_200

			if order.in_obra:
				dias_prod = dias_prod+limite.obras
					
			if tieneentalle:
				dias_prod = dias_prod+limite.entalle

			dateprod = datetime.strptime(self.date,'%Y-%m-%d')+timedelta(days=dias_prod)
			dias_send = 0
			if order.destinity_order=='local':
				dias_send = dias_send+limite.local_send
			
			if order.destinity_order=='external':
				dias_send = dias_send+limite.external_send	
			

			if order.send2partner:
				dias_send = dias_send+limite.send2partner				

			datesend = datetime.strptime(self.date,'%Y-%m-%d')+timedelta(days=dias_send)
		 	vals = {
				'date_production':dateprod,
				'date_delivery':datesend,
			}
			order.write(vals)



			# res = urlparse.urljoin(base_url, "?%s#%s" % (urllib.urlencode(query), urllib.urlencode(fragment)))
			# cadurl = base_url+"/web?#view_type=form&id="+str(self.requisition_id.id)+"&type=signup&model=purchase.requisition"

			# http://localhost:8069/web?#id=8&view_type=form&model=purchase.requisition&action=601
			body = """Estimado(a) se ha reprogramado la Orden de Producción """+order.name+"""  <br/>		
			Atte.<br/>
				  El equipo ODOO
						"""
			mail_values = {
				'subject': "Reprogramación de Orden de Producción "+order.name,
				'body_html': body,
				'email_to': oder.seller_id.partner_id.email,
				'email_from': self.env['res.company'].search([])[0].partner_id.email,
	   		}
			create_and_send_email = self.env['mail.mail'].create(mail_values).send() 

