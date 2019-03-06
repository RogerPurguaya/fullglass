# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta

class glass_pdf_file(models.Model):
	_name='glass.pdf.file'

	pdf_file = fields.Binary('Croquis')
	pdf_name = fields.Char('Archivo')
	file_name = fields.Char('Archivo')
	is_used = fields.Boolean('Usado',default=False)
	op_id = fields.Many2one('glass.order',u'Orden de Producción')
	sale_id = fields.Many2one('sale.order','Pedido de venta')
	is_editable = fields.Boolean('Es editable',default=True)
	_rec_name="pdf_name"

	@api.model
	def create(self,vals):
		if 'file_name' in vals:
			vals.update({'pdf_name':vals['file_name']})
		super(glass_pdf_file,self).create(vals)

	@api.one
	def write(self,vals):
		if 'file_name' in vals:
			vals.update({'pdf_name':vals['file_name']})
		super(glass_pdf_file,self).write(vals)


	@api.one
	def save_pdf(self):
		self.editable_croquis=False
		return True

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	op_count = fields.Integer(u'Ordenes de producción',compute="getops")
	op_control = fields.Char('Control de OP',default="NO APLICA")
	op_ids = fields.One2many('glass.order',string=u'Ordenes de producción',compute="getops")
	files_ids = fields.One2many('glass.pdf.file','sale_id','Croquis')
	reference_order = fields.Char(string='Referencia OP')


	@api.one
	def getstateop(self):
		lsta=[]
		allprod = False
		havecalc=False
		allprod=True
		nonequal = []
		generated_order = self.env['glass.order'].search([('sale_order_id','=',self.id)])
		for line in self.order_line:
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
			if allprod and len(generated_order) > 0:
				self.op_control='OP GENERADA'
			else:
				if len(lsta)==0:
					self.op_control='OP PENDIENTE'	
				else:
					self.op_control='OP PARCIAL'
		else:
			self.op_control='NO APLICA'

	@api.one
	def getops(self):
		lsta=[]
		for line in self.order_line:
			if line.id_type:
				for detacalc in line.id_type_line:
					if detacalc.production_id:
						if detacalc.production_id.id not in lsta:
							lsta.append(detacalc.production_id.id)
		self.op_count=len(lsta)
		self.op_ids=lsta

	@api.multi
	def makeproduction(self,vals_wizard):
		self.ensure_one()
		if self.invoice_count==0:
			raise UserError(u"No se puede generar OP cuando no se tiene una factura")
		lsta=[]
		generar = False
		for line in self.order_line:
			if line.id_type:
				for detacalc in line.id_type_line:
					if detacalc.production_id:
						if detacalc.production_id.id not in lsta:
							lsta.append(detacalc.production_id.id)
					else:
						generar=True
		if len(lsta)>0:
			if not self.before_invoice:
				raise UserError(u"El pedido ya tiene ordenes de porducción asignadas")
		newname = self.name
		nextnumber = len(lsta)

		if nextnumber>0:
			newname = newname+"."+str(nextnumber)

		if generar:
			

			area = 0
			tieneentalle = False
			for line in self.order_line:
				if line.id_type:
					for detacalc in line.id_type_line:
						if not detacalc.production_id:
							area=area+detacalc.area
							if detacalc.entalle or detacalc.descuadre:
								tieneentalle=True

			config=self.env['glass.order.config'].search([])
			if len(config)==0:
			    raise UserError(u'No se encontraron los valores de configuración de produccion')
			config=self.env['glass.order.config'].search([])[0]
			limite = False
			for linec in config.limit_ids:
				if linec.motive_limit=='templado':
					limite = linec
			if not limite:
				raise UserError(u"No se ha encontra la configuración de plazos de producción")
			dias_prod = 0
			if area<51:
				dias_prod = limite.zero_2_50
			if area<101 and area>50:
				dias_prod = limite.fiftyone_2_100
			if area<201 and area>101:
				dias_prod = limite.onehundred1_2_200
			if area>200:
				dias_prod = limite.more_2_200

			# 'selected_file':self.selected_file,
			# 'file_crokis':self.file_crokis,
			# 'file_name':self.file_name,
			# 'destinity_order':self.destinity_order,
			# 'send2partner':self.send2partner,
			# 'in_obra':self.in_obra,
			# 'obra_text':self.obra_text,
			if vals_wizard['in_obra']:
				dias_prod = dias_prod+limite.obras
					
			if tieneentalle:
				dias_prod = dias_prod+limite.entalle
				

			dateprod = datetime.now()+timedelta(days=dias_prod)
			
			if dateprod.weekday()==6:
				dateprod = dateprod+timedelta(days=1)

			dias_send = 0
			aux = False # auxiliar
			if vals_wizard['destinity_order']=='local':
				dias_send = dias_send+limite.local_send
				aux = True
			
			if vals_wizard['destinity_order']=='external':
				dias_send = dias_send+limite.external_send	
			datesend = dateprod+timedelta(days=dias_send)

			if vals_wizard['send2partner']:
				dias_send = dias_send+limite.send2partner				

			if aux: # si la entrega es en la ciudad, delivery_date es igual a la send_date
				datedeli = datesend
			else:
				datedeli = datesend+timedelta(days=dias_send)
				
		 	vals = {
				'sale_order_id':self.id,
				'name':newname,
				'date_production':dateprod,
				'date_send':datesend,
				'date_delivery':datedeli,
				'sketch':vals_wizard['selected_file'].pdf_file,
				'file_name':vals_wizard['selected_file'].file_name,
				'obra':vals_wizard['obra_text'],
				'destinity_order':vals_wizard['destinity_order'],
				'send2partner':vals_wizard['send2partner'],
				'in_obra':vals_wizard['in_obra'],
				'sketch':vals_wizard['file_crokis'],
				'comercial_area':vals_wizard['comercial_area'],
				'reference_order': self.reference_order if self.reference_order else ''
			}

			neworder = self.env['glass.order'].create(vals)
			vals_wizard['selected_file'].write(
				{
					'is_editable':False,
					'is_used':True,
					'op_id':neworder.id,
				}),
		

			for line in self.order_line:
				if line.id_type:
					for detacalc in line.id_type_line:
						if not detacalc.production_id:
							detacalc.write({'production_id':neworder.id})
							if self.before_invoice==False:
								line.id_type.iseditable=False
			neworder.validate_order()

		self.getstateop()
		return neworder

		


	@api.multi
	def loadproductionwizard(self):
		self.ensure_one()
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.saleorder_makeorder_view' % module)


		data = {
					
				'name':u'Generar Órdenes de Producción',
				'view_type':'form',
				'view_mode':'form',
				'res_model':'sale.order.make.order',
				'type':'ir.actions.act_window',
				'target': 'new',
				'view_id': view.id,
		}
		return data	

	@api.multi
	def show_po_list(self):
		self.ensure_one()
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_order_tree' % module)
		idact=False
		data = {
					
				'name':u'Órdenes de producción',
				'view_type':'form',
				'view_mode':'tree,form',
				'res_model':'glass.order',
				'type':'ir.actions.act_window',
				'domain':[('sale_order_id','=',self.id)]
		}
		return data		

	@api.multi
	def call_crokis(self):
		form_view_ref = self.env.ref('glass_production_order.view_glass_croquis_sale_wizard_form', False)
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_croquis_sale_wizard_form' % module)
		data = {
			'name': _('Croquis'),
			'context': self._context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.croquis.sale.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 
		return data




		
	
	
