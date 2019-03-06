# -*- coding: utf-8 -*-

from openerp import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class tipo_cambio_comercial(models.Model):
	_name = 'tipo.cambio.comercial'

	name = fields.Date('Fecha',required=True)
	tipo_venta = fields.Float('Tipo de Venta',digits=(12,3),required=True)


class sale_order(models.Model):
	_inherit = 'sale.order'

	@api.one
	def cambiar_lista_precio(self):
		for i in self.order_line:
			i.product_id_change()
			i.product_uom_change()

class sale_order_line(models.Model):
	_inherit = 'sale.order.line'

	@api.multi
	@api.onchange('product_id')
	def product_id_change(self):
		if self.product_id:
			currency_obj = self.env['res.currency'].search([('name','=','USD')])
			if len(currency_obj)>0:
				currency_obj = currency_obj[0]
			else:
				raise UserError( 'Error!\nNo existe la moneda USD' )

			from datetime import datetime, timedelta
			fecha = False
			if self.order_id.date_order:
				fecha = str(datetime(day=int(str(self.order_id.date_order)[:10].split('-')[2]),month=int(str(self.order_id.date_order)[:10].split('-')[1]),year=int(str(self.order_id.date_order)[:10].split('-')[0]),hour=  int(str(self.order_id.date_order).split(' ')[1].split(':')[0]), minute=int(str(self.order_id.date_order).split(' ')[1].split(':')[1]), second=int(str(self.order_id.date_order).split(' ')[1].split(':')[2])) - timedelta(hours=5))[:10]
			else:
				raise UserError( 'Seleccione la fecha de pedido.' )

			tipo_cambio = self.env['res.currency.rate'].search([('name','=',fecha),('currency_id','=',currency_obj.id)])

			if len(tipo_cambio)>0:
				tipo_cambio = tipo_cambio[0]
			else:
				raise UserError( 'Error!\nNo existe el tipo de cambio para la fecha: '+ str(fecha) )
			
			vactual = 0
			ractual = 0

			vactual = tipo_cambio.type_sale
			ractual = tipo_cambio.rate

			tipo_cambio_comercial_t = self.env['tipo.cambio.comercial'].search([('name','<=',fecha)]).sorted(key=lambda r: r.name)
			if len(tipo_cambio_comercial_t)>0:
				tipo_cambio_comercial_t = tipo_cambio_comercial_t[-1]
			else:
				tipo_cambio_comercial_t = False

			if tipo_cambio_comercial_t and tipo_cambio_comercial_t.id:
				self.env.cr.execute("""
					update res_currency_rate set type_sale = """ +"%.3f"%(tipo_cambio_comercial_t.tipo_venta)+ """, rate = """ + "%.10f"%(1.0 / tipo_cambio_comercial_t.tipo_venta)+ """
					where id = """ +str(tipo_cambio.id)+ """
					""")
				#tipo_cambio.type_sale = tipo_cambio_comercial_t.tipo_venta
				#tipo_cambio.rate = 1.0 / tipo_cambio_comercial_t.tipo_venta


			ttip = super(sale_order_line,self).product_id_change()

			if tipo_cambio_comercial_t and tipo_cambio_comercial_t.id:

				self.env.cr.execute("""
					update res_currency_rate set type_sale = """ +"%.3f"%(vactual)+ """, rate = """ + "%.10f"%(ractual)+ """
					where id = """ +str(tipo_cambio.id)+ """
					""")
				#tipo_cambio.type_sale = vactual
				#tipo_cambio.rate = ractual
			return ttip
		else:
			ttip = super(sale_order_line,self).product_id_change()
			return ttip


	@api.onchange('product_uom', 'product_uom_qty')
	def product_uom_change(self):
		if self.product_id:
			currency_obj = self.env['res.currency'].search([('name','=','USD')])
			if len(currency_obj)>0:
				currency_obj = currency_obj[0]
			else:
				raise UserError( 'Error!\nNo existe la moneda USD' )

			from datetime import datetime, timedelta
			fecha = False
			if self.order_id.date_order:
				fecha = str(datetime(day=int(str(self.order_id.date_order)[:10].split('-')[2]),month=int(str(self.order_id.date_order)[:10].split('-')[1]),year=int(str(self.order_id.date_order)[:10].split('-')[0]),hour=  int(str(self.order_id.date_order).split(' ')[1].split(':')[0]), minute=int(str(self.order_id.date_order).split(' ')[1].split(':')[1]), second=int(str(self.order_id.date_order).split(' ')[1].split(':')[2])) - timedelta(hours=5))[:10]
			else:
				raise UserError( 'Seleccione la fecha de pedido.' )

			tipo_cambio = self.env['res.currency.rate'].search([('name','=',fecha),('currency_id','=',currency_obj.id)])

			if len(tipo_cambio)>0:
				tipo_cambio = tipo_cambio[0]
			else:
				raise UserError( 'Error!\nNo existe el tipo de cambio para la fecha: '+ str(fecha) )
			
			vactual = 0
			ractual = 0

			vactual = tipo_cambio.type_sale
			ractual = tipo_cambio.rate

			tipo_cambio_comercial_t = self.env['tipo.cambio.comercial'].search([('name','<=',fecha)]).sorted(key=lambda r: r.name)

			if len(tipo_cambio_comercial_t)>0:
				tipo_cambio_comercial_t = tipo_cambio_comercial_t[-1]
			else:
				tipo_cambio_comercial_t = False

			if tipo_cambio_comercial_t and tipo_cambio_comercial_t.id:
				self.env.cr.execute("""
					update res_currency_rate set type_sale = """ +"%.3f"%(tipo_cambio_comercial_t.tipo_venta)+ """, rate = """ + "%.10f"%(1.0 / tipo_cambio_comercial_t.tipo_venta)+ """
					where id = """ +str(tipo_cambio.id)+ """
					""")
				#tipo_cambio.type_sale = tipo_cambio_comercial_t.tipo_venta
				#tipo_cambio.rate = 1.0 / tipo_cambio_comercial_t.tipo_venta


			super(sale_order_line,self).product_uom_change()

			self.env.cr.execute("""
				update res_currency_rate set type_sale = """ +"%.3f"%(vactual)+ """, rate = """ + "%.10f"%(ractual)+ """
				where id = """ +str(tipo_cambio.id)+ """
				""")
			#if tipo_cambio_comercial_t and tipo_cambio_comercial_t.id:
			#	tipo_cambio.type_sale = vactual
			#	tipo_cambio.rate = ractual
			
		else:
			ttip = super(sale_order_line,self).product_uom_change()
			
