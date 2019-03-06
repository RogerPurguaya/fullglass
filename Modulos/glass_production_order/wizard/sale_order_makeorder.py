# -*- coding: utf-8 -*-
from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class SaleorderMakeOrder(models.TransientModel):
	_name='sale.order.make.order'

	selected_file = fields.Many2one('glass.pdf.file','Archivo a incluir',domain="[('is_used','=',False),('is_editable','=',True),('sale_id','=',sale_id)]")
	file_crokis = fields.Binary('Croquis',related="selected_file.pdf_file")
	file_name = fields.Char('Nombre del archivo',related="selected_file.pdf_name")
	destinity_order = fields.Selection([('local','En la ciudad'),('external','En otra ciudad')],u'Lugar de entrega',default="local")
	send2partner=fields.Boolean('Entregar en ubicacion del cliente',default=False)
	in_obra = fields.Boolean('Entregar en Obra')
	obra_text = fields.Char(u'Descripción de Obra')
	sale_id = fields.Many2one('sale.order','Orden de venta')
	is_used = fields.Boolean('Usado',related="selected_file.is_used")
	is_editable = fields.Boolean('Es editable',related="selected_file.is_editable")
	comercial_area=fields.Selection([('distribucion',u'Distribución'),('obra','Obra'),('proyecto','Proyecto')],u'Área Comercial',default="distribucion" )

	# @api.onchange('selected_file')
	# def onchange_selected_file(self):
	# 	if self.selected_file:
	# 		self.file_crokis = self.selected_file.pdf_file



	@api.multi
	def create_production(self):
		self.ensure_one()
		vals={
				'selected_file':self.selected_file,
				'file_crokis':self.file_crokis,
				'file_name':self.file_name,
				'destinity_order':self.destinity_order,
				'send2partner':self.send2partner,
				'in_obra':self.in_obra,
				'obra_text':self.obra_text,
				'comercial_area':self.comercial_area,
			}
		neworder = self.sale_id.makeproduction(vals)
		self.selected_file.write(
				{
					'is_editable':False,
					'is_used':True,
					'op_id':neworder.id,
				})
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_order_tree' % module)
		idact=False
		ctx = self._context.copy()
		ctx.update({'domain':[('sale_order_id','=',self._context['active_id'])]})		
		
		data = {
				'name':u'Órdenes de producción',
				'view_type':'form',
				'view_mode':'tree,form',
				'res_model':'glass.order',
				'type':'ir.actions.act_window',
				'domain':[('sale_order_id','=',self._context['active_id'])]
		}
		
		return data		


	@api.one
	def savecroquis(self):
		if self.file_crokis:
			self.is_editable = False
			self.production_id.sketch = self.file_crokis
		return True

	@api.model
	def default_get(self,fields):
		res = super(SaleorderMakeOrder,self).default_get(fields)
		sale_id = self._context['active_id']
		saleact = self.env['sale.order'].browse(sale_id)
		res.update({
			'sale_id':sale_id,
			'selected_file':saleact.files_ids[0].id if saleact.files_ids else False,
			})
		return res