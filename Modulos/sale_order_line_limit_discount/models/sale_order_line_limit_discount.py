# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from openerp.exceptions import ValidationError

class ResUserAdditionalDiscount(models.Model):
	_inherit = "res.users"
	additional_discount = fields.Float(string ="Descuento Adicional %", size=10)

class SaleOrderLineLimitDiscount(models.Model):
	_inherit = "sale.order.line"

	@api.constrains('discount')
	def _check_something(self):

		if not (self.product_id and self.product_uom and
				self.order_id.partner_id and self.order_id.pricelist_id and
				self.order_id.pricelist_id.discount_policy == 'without_discount' and
				self.env.user.has_group('sale.group_discount_per_so_line')):
			return

		# self.discount = 0.0
		product = self.product_id.with_context(
			 lang=self.order_id.partner_id.lang,
			 partner=self.order_id.partner_id.id,
			 quantity=self.product_uom_qty,
			 date=self.order_id.date_order,
			 pricelist=self.order_id.pricelist_id.id,
			 uom=self.product_uom.id,
			 fiscal_position=self.env.context.get('fiscal_position')
		)

		product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

		price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
		new_list_price, currency_id = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
		des_final=0
		add_dis_user= self.env.user[0].additional_discount
		if new_list_price != 0:
			if self.order_id.pricelist_id.currency_id.id != currency_id:
				new_list_price = self.env['res.currency'].browse(currency_id).with_context(product_context).compute(new_list_price, self.order_id.pricelist_id.currency_id)
			des_final = (new_list_price - price) / new_list_price * 100
			if des_final > 0:
				des_final =des_final+add_dis_user
				if round(float(self.discount),2) > round(float(des_final),2):
					raise ValidationError("No puede realizar un descuento mayor, para el producto: "+self.name+" al: " + str(des_final))

		# sql = """
		# select ppi.price_discount, base_pricelist_id from
		# sale_order as so
		# inner join product_pricelist_item as ppi
		# on so.pricelist_id = ppi.pricelist_id
		# where so.id = '%d'
		# """ %(self.order_id)
		# #print "Este es el numero de orden", self.order_id
		# self.env.cr.execute(sql)
		# max_val = self.env.cr.fetchall()
		# #print "max value*******************",max_val 
		# des_final=max_val[0][0]
		# if(max_val[0][0]==0):
		#	 sql = """
		#	 select price_discount from product_pricelist_item where pricelist_id = '%d'
		#	 """ %(int(max_val[0][1]))
		#	 self.env.cr.execute(sql)
		#	 sal = self.env.cr.fetchone()[0]
		#	 #print sal
		#	 des_final = sal
		# add_dis_user= self.env.user[0].additional_discount
		# if des_final:
		#	 des_final =des_final+add_dis_user
		#	 if self.discount > des_final:
		#		 raise ValidationError("No puede realizar un descuento mayor al: " + str(des_final))