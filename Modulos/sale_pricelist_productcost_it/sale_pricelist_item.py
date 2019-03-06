# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
class PricelistItem(models.Model):
	_inherit = "product.pricelist.item"

	product_cost = fields.Float(u'Costo Promedio USD',compute="getpricecost",store=False)
		# related='product_tmpl_id.standard_price')
	product_last_price = fields.Float(u'Último Costo de Compra USD',compute="getlastprice",digist=(20,8),store=False)

	@api.one
	def getpricecost(self):
		price = self.product_tmpl_id.standard_price
		currency=self.env['res.currency'].search([('name','=','USD')])
		cambio = self.env.user.company_id.currency_id.compute(price, currency)
		self.product_cost=cambio




	@api.one
	def getlastprice(self):
		price = self.product_tmpl_id.standard_price
		currency=self.env['res.currency'].search([('name','=','USD')])
		cambio = currency.compute(price, self.env.user.company_id.currency_id)
		product_cost=cambio

		producto = self.env['product.product'].search([('product_tmpl_id','=',self.product_tmpl_id.id)])
		if not producto:
			return
		productos = '{'+str(producto[0].id)+'}'
		locations = self.env['stock.location'].search([('usage','=','internal')])
		almacenes='{'
		for l in locations:
			almacenes=almacenes +str(l.id)+','
		almacenes=almacenes[:-1]+'}'
		date_ini = str(datetime.now().year)+'-01-01'
		date_fin = str(datetime.now())[:10]


		cadsql = """ 
				select 
				fecha_albaran as "Fecha Alb.",	
				fecha as "Fecha",
				type_doc as "T. Doc.",
				serial as "Serie",
				nro as "Nro. Documento",
				stock_doc as "Nro. Documento",
				doc_partner as "Nro Doc. Partner",
				name as "Proveedor",							
				operation_type as "Tipo de operacion",				 
				name_template as "Producto",
				unidad as "Unidad",				 
				ingreso as "Ingreso Fisico",
				round(debit,6) as "Ingreso Valorado.",
				salida as "Salida Fisico",
				round(credit,6) as "Salida Valorada",
				saldof as "Saldo Fisico",
				round(saldov,6) as "Saldo valorado",
				round(cadquiere,6) as "Costo adquisicion",
				round(cprom,6) as "Costo promedio",
					origen as "Origen",
					destino as "Destino",
				almacen AS "Almacen"
				from get_kardex_v("""+ str(date_ini).replace('-','') + "," + str(date_fin).replace('-','') + ",'" + productos + """'::INT[], '""" + almacenes + """'::INT[]) 
			"""
		# raise UserError(cadsql)
		self.env.cr.execute(cadsql)
		datasql = self.env.cr.fetchall()
		cambio =0.000000
		if len(datasql)>0:
			lasline = datasql[len(datasql)-1]
			price = self.product_tmpl_id.standard_price
			currency=self.env['res.currency'].search([('name','=','USD')])

			cambio = self.env.user.company_id.currency_id.compute(lasline[17], currency, round=False)
			print lasline[17],cambio
		self.product_last_price=cambio







