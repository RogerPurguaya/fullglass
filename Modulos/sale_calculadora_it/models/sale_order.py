# -*- coding: utf-8 -*-
from odoo.osv import osv
from odoo import fields, models,api, _
from odoo.exceptions import UserError
from decimal import *
from lxml import etree
import pprint
import json
from openerp.osv import osv

class SaleOrder(models.Model):
	_inherit='sale.order'

	before_invoice = fields.Boolean('Factura Adelantada',default=False)

	@api.one
	def unlink(self):
		if self.invoice_count>0:
			raise UserError(u"No se puede eliminar un pedido de venta si ya fue facturado")
		for l in self.order_line:
			if l.id_type:
				raise UserError(u"No se puede eliminar un pedido de venta si tiene calculadora")
		return super(SaleOrder,self).unlink()

	

	# @api.one
	# def write(self,vals):

	# 	t=super(SaleOrder,self).write(vals)
	# 	self.refresh()
	# 	eseditable=False
	# 	tienefactura = False

	# 	if self.state=='draft':
	# 		eseditable=True
	# 	if self.invoice_count>0:
	# 		tienefactura=True
			
	# 	tieneoc =False
	# 	for line in self.order_line:
	# 		for l2 in line.id_type.id_line:
	# 			if l2.production_id:
	# 				tieneoc=True
	# 				break
	# 		if tieneoc:
	# 			break
	# 	if tieneoc:
	# 		if self.before_invoice:
	# 			eseditable=True
	# 		else:
	# 			eseditable=False
	# 	else:
	# 		eseditable=True
	# 	print 'po',eseditable
	# 	for line in self.order_line:
	# 		if line.id_type:
	# 			line.id_type.write({'iseditable':eseditable})
	# 			line.id_type.write({'invoiced':tienefactura})
	# 			line.id_type.write({'invoice_prev':self.before_invoice})
			
	# 	# 	else:
	# 	# 		print 3
	# 	# 		for line in self.order_line:
	# 	# 			if 'before_invoice' in vals:
	# 	# 				if vals['before_invoice']==True:
	# 	# 					print 4
	# 	# 					line.id_type.write({'iseditable':True,'invoice_prev':True})
	# 	# 				else:
	# 	# 					line.id_type.write({'iseditable':False,'invoice_prev':False})
	# 	# 			else:
	# 	# 				if self.before_invoice==True:
	# 	# 					print 6
	# 	# 					line.id_type.write({'iseditable':True,'invoice_prev':True})
	# 	# 				else:
	# 	# 					line.id_type.write({'iseditable':False,'invoice_prev':False})
	
	# 	# if 'before_invoice' in vals:
	# 	# 	if vals['before_invoice']==True:
	# 	# 		for line in self.order_line:
	# 	# 			print 4
	# 	# 			line.id_type.write({'iseditable':True,'invoice_prev':True})
	# 	# 	else:
	# 	# 		for line in self.order_line:
	# 	# 			line.id_type.write({'iseditable':False,'invoice_prev':False})

	# 	return super(SaleOrder,self).write(vals)

	


