# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
from pyPdf import PdfFileReader,PdfFileWriter
import base64
from StringIO import StringIO
import os
import sys
from subprocess import Popen, PIPE
import tempfile
from pdf2image import convert_from_path
from PIL import Image

class GlassProductionControlWizard(models.Model):
	_name='glass.productioncontrol.wizard'

	stage = fields.Selection([('corte','Corte'),('pulido','Pulido'),('entalle','Entalle'),('lavado','Lavado')],'Etapa')
	search_code = fields.Char('Producto')
	lot_line_id = fields.Many2one('glass.lot.line',u'Línea de lote')
	production_order = fields.Many2one('glass.order','OP')
	partner_id = fields.Many2one('res.partner',string='Cliente')
	product_id = fields.Many2one('product.product',string='Cristal')
	lot_id = fields.Many2one('glass.lot')
	obra = fields.Char(string='Obra')

	image_glass = fields.Binary("imagen")
	image_page = fields.Binary("Page")
	image_page_r90 = fields.Binary("Page")
	image_page_r180 = fields.Binary("Page")
	image_page_r270 = fields.Binary("Page")
	sketch = fields.Binary("Croquis")
	sketch_page = fields.Binary("Croquis")
	nro_cristal = fields.Char("Nro. Cristal",related="lot_line_id.nro_cristal")
	is_used = fields.Boolean('usado',default=False)
	existe = fields.Integer('existe')
	messageline= fields.Char('Mensaje',default='El elemento ya fue registrado en esta etapa')
	rotate = fields.Boolean('Rotar', default=False)

	@api.multi
	def get_new_element(self):
		import PyPDF2
		direccion = self.env['main.parameter'].search([])[0].download_directory

		writer = PyPDF2.PdfFileWriter()
		writer.insertBlankPage(width=500, height=500, index=0)
		with open(direccion+'previsualizacion_op.pdf', "wb") as outputStream: 
			writer.write(outputStream) #write pages to new PDF

		return {
			'name':'Control de Produccion',
			'type': 'ir.actions.act_window',
			'res_model': 'glass.productioncontrol.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.one
	def get_asf(self):
		self.sketch_page = False


	@api.one
	def setrotate(self):
		self.rotate= not self.rotate


	@api.model
	def default_get(self,fields):
		res =super(GlassProductionControlWizard,self).default_get(fields)
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]
		ustage = False
		for userstage in config_data.userstage:
			if userstage.user_id.id == self.env.user.id:
				ustage=userstage
		if ustage:
			res.update({'stage':ustage.stage})
		else:
			raise UserError(u'El usuario actual no tiene permisos para acceder a esta funcionalidad')		
		return res



	@api.onchange('search_code')
	def onchangecode(self):
		self.ensure_one()
		vals={}
		if self.search_code:
			config_data = self.env['glass.order.config'].search([])
			if len(config_data)==0:
				raise UserError(u'No se encontraron los valores de configuración de producción')		
			config_data = self.env['glass.order.config'].search([])[0]
			existe = self.env['glass.lot.line'].search([('search_code','=',self.search_code)])

			if len(existe)>0:
				lsttmp=[]
				page_one=False
				existe_act = existe[0]
				self.is_used=False
				self.lot_line_id=False
				self.production_order=False
				self.partner_id=False
				self.product_id=False
				self.lot_id=False
				self.obra=False
				self.image_glass=False
				self.sketch=False
				self.search_code=False

				vals={}
				
				vals.update({
					'lot_line_id':existe_act.id,
					'production_order':existe_act.order_prod_id.id,
					'partner_id':existe_act.order_prod_id.partner_id.id,
					'product_id':existe_act.product_id.id,
					'lot_id':existe_act.lot_id.id,
					'obra':existe_act.order_prod_id.obra,
					'image_glass':existe_act.image_glass,
					'nro_cristal':existe_act.nro_cristal,
				})
				self.lot_line_id=existe_act.id
				self.production_order=existe_act.order_prod_id.id
				self.partner_id=existe_act.order_prod_id.partner_id.id
				self.product_id=existe_act.product_id.id
				self.lot_id=existe_act.lot_id.id
				self.obra=existe_act.order_prod_id.obra
				self.image_glass=existe_act.image_glass
				self.nro_cristal=existe_act.nro_cristal

				data = existe_act
				file = open(data.order_line_id.image_page_number,'rb')
				cont_t = file.read()
				file.close()
				direccion = self.env['main.parameter'].search([])[0].download_directory
				
				file_new = open(direccion + 'previsualizacion_op.pdf','wb')
				file_new.write(cont_t)
				file_new.close()

				self.messageline=''
				stage_obj = self.env['glass.stage.record']
				
				if self.stage=='entalle':
					if self.lot_line_id.calc_line_id.entalle==0:
						self.messageline='El cristal no tiene etapa de entalle'
						vals.update({'messageline':'El cristal no tiene etapa de entalle'})
						self.search_code=''
						self.is_used=True
						self.write(vals)
						return {'value':vals}		
				ext = stage_obj.search([('stage','=',self.stage),('lot_line_id','=',existe_act.id)])
				if len(ext)==0:
					self.save_stage()
				else:
					self.messageline='El cristal ya fue procesado en esta etapa'
					vals.update({'messageline':'El cristal ya fue procesado en esta etapa'})
					self.is_used=True
				

			else:
				self.write({
					'is_used':False,
					'lot_line_id':False,
					'production_order':False,
					'partner_id':False,
					'product_id':False,
					'lot_id':False,
					'obra':False,
					'image_glass':False,
					'sketch':False,
					'sketch_page':False,
					'search_code':False,
				})
				
				direccion = self.env['main.parameter'].search([])[0].download_directory
				import PyPDF2
				writer = PyPDF2.PdfFileWriter()
				writer.insertBlankPage(width=500, height=500, index=0)
				with open(direccion+'previsualizacion_op.pdf', "wb") as outputStream: 
					writer.write(outputStream) 
				self.image_page=False

		self.search_code=''
		self.write(vals)
		
		return {'value':vals}

	@api.one
	def save_stage(self):
		stage_obj = self.env['glass.stage.record']
		if self.lot_line_id:
			existe = self.env['glass.lot.line'].search([('search_code','=',self.search_code)])
			if len(existe)>0:
				existe_act = existe[0]
				ext = stage_obj.search([('stage','=',self.stage),('lot_line_id','=',existe_act.id)])
				# si ya se registró solo se muestran los valores pero no se registra nuevamente
				if len(ext)>0:
					self.is_used=True
					self.lot_line_id=existe_act.id
					return
					# raise UserError(u'El cristal seleccionado ya fue registrado en la etapa seleccionada')		
				self.lot_line_id=existe_act.id
			#print 1
			if self.lot_line_id:
				#print 2
				if self.stage=='lavado':
					#print 3
				
					if self.lot_line_id.calc_line_id.entalle:
						#print 4,self.lot_line_id.calc_line_id.entalle
						pasoentalle = stage_obj.search([('stage','=','entalle'),('lot_line_id','=',self.lot_line_id.id)])
						if len(pasoentalle)==0:
							self.is_used=True
							self.lot_line_id=False
							self.production_order=False
							self.partner_id=False
							self.product_id=False
							self.lot_id=False
							self.obra=False
							self.image_glass=False
							self.sketch=False
							self.search_code=False
							return
							# raise UserError(u'No se puede registrar LAVADO si no se ha pasado por ENTALLE')		
				data = {
						'user_id':self.env.uid,
						'date':datetime.now(),
						'time':datetime.now().time(),
						'stage':self.stage,
						'lot_line_id':self.lot_line_id.id,
					}

				stage_obj.create(data)
				if self.stage == 'corte':
					self.lot_line_id.write({'corte':True})
					self.lot_line_id.corte = True
				if self.stage == 'pulido':
					self.lot_line_id.write({'pulido':True})
					self.lot_line_id.pulido = True
				if self.stage == 'entalle':
					self.lot_line_id.write({'entalle':True})
					self.lot_line_id.entalle = True
				if self.stage == 'lavado':
					self.lot_line_id.write({'lavado':True})
					self.lot_line_id.lavado = True

		return True