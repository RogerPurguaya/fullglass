# -*- coding: utf-8 -*-

from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang
from math import fabs
import odoo.addons.decimal_precision as dp

class WizardPrintCaja(models.TransientModel):
	_name = 'wizard.print.caja'
	_description = 'Extencion para Imprimir Caja'
	date_i = fields.Date('Dia Inicio', default=fields.Datetime.now, required=True)
	date_f = fields.Date('Dia Fin', default=fields.Datetime.now, required=True)

	@api.model
	def get_default_diarios(self):
		return self.env['account.journal'].search([('code', 'in', ['CRE', 'CRE$', 'BCP1','BCP2','BBVA1','BBVA2'])]).ids

	diario_id = fields.Many2many(
	    'account.journal',
	    string='Diario',
	    required=True,
	    default=get_default_diarios
	)

	@api.multi
	def print_caja_report(self):
		return self.env['report'].get_action(self, 'planilla_ingresos_pdf_it.report_caja')
	
	@api.multi
	def get_document(self):
		id_x=[]
		for x in self.diario_id:
			id_x.append(x.default_debit_account_id.id)
			if(x.default_debit_account_id.id != x.default_credit_account_id.id):
				id_x.append(x.default_credit_account_id.id)
		print "\n \n \n"
		print id_x
		print "\n \n \n"
		lista_total=[]
		metodos_pago = self.env['einvoice.means.payment'].search([])
		print metodos_pago
		for i in metodos_pago:
			lista=self.env['account.move.line'].search([('account_id','in',id_x),('move_id.means_payment_it','=',i.id),('payment_id.fecha_caja','<=',self.date_f),('payment_id.fecha_caja','>=',self.date_i)])
			lista_total.append(lista)
		return lista_total
	@api.multi
	def get_vendedor(self,referencia,tipo):
		if(tipo):
			invoice = self.env['account.invoice'].search([('number','=',referencia),('type','=',"out_invoice")])
		else:
			invoice = self.env['account.invoice'].search([('number','=',referencia),('type','=',"in_invoice")])
		return invoice.user_id.name
	@api.multi
	def get_tipo(self,referencia,tipo):
		if(tipo):
			invoice = self.env['account.invoice'].search([('number','=',referencia),('type','=',"out_invoice")])
		else:
			invoice = self.env['account.invoice'].search([('number','=',referencia),('type','=',"in_invoice")])
		if invoice.it_type_document.name == False:
			return "-"
		else:
			return invoice.it_type_document.name[:3]+"-"

	@api.multi
	def sum_soles(self,lista,tipo):
		suma=0.0
		if(tipo):
			for line in lista:
				if (line.payment_id.currency_id.name == 'PEN'):
					suma+=line.debit
		else:
			for line in lista:
				if (line.payment_id.currency_id.name == 'PEN'):
					suma+=line.credit
		return suma
	@api.multi
	def sum_dolares(self,lista,tipo):
		suma=0.0
		if(tipo):
			for line in lista:
				if (line.payment_id.currency_id.name == 'USD'):
					#suma+=line.debit
					suma+=fabs(line.amount_currency)
		else:
			for line in lista:
				if (line.payment_id.currency_id.name == 'USD'):
					#suma+=line.credit
					suma+=fabs(line.amount_currency)
		return suma
	@api.multi
	def sum_gen_soles(self,lista,tipo):
		suma=0.0
		if(tipo):
			for i in lista:
				for line in i:
					if (line.payment_id.currency_id.name == 'PEN'):
						suma+=line.debit
		else:
			for i in lista:
				for line in i:
					if (line.payment_id.currency_id.name == 'PEN'):
						suma+=line.credit
		return suma
	@api.multi
	def sum_gen_dolares(self,lista,tipo):
		suma=0.0
		if(tipo):
			for i in lista:
				for line in i:
					if (line.payment_id.currency_id.name == 'USD'):
						#suma+=line.debit
						suma+=fabs(line.amount_currency)
		else:
			for i in lista:
				for line in i:
					if (line.payment_id.currency_id.name == 'USD'):
						#suma+=line.credit
						suma+=fabs(line.amount_currency)
		return suma
	@api.multi
	def get_cobradores(self,lista):
		cobradores=[]
		vendido=[]
		dic=[]
		for i in lista:
			for line in i:
				co = self.get_vendedor(line.ref,True)
				if (co not in cobradores):
					cobradores.append(co)
					temp=[0,0]
					if (line.payment_id.currency_id.name == 'PEN'):
						temp[0] += line.debit
					if (line.payment_id.currency_id.name == 'USD'):
						#temp[1] += line.debit
						temp[1]+=fabs(line.amount_currency)
					vendido.append(temp)
				else:
					indice=cobradores.index(co)
					if (line.payment_id.currency_id.name == 'PEN'):
						vendido[indice][0] += line.debit
					if (line.payment_id.currency_id.name == 'USD'):
						#vendido[indice][1] += line.debit
						vendido[indice][1]+=fabs(line.amount_currency)
		for x in range(len(cobradores)):
			temp = [[cobradores[x]],vendido[x]]
			dic.append(temp)
			
		return dic	
	@api.multi
	def get_actual_user(self):
		fmt = '%Y.%m.%d %H:%M:%S'
		return self.env.user.name+ " " + (datetime.now()-timedelta(hours=5)).strftime(fmt)


class FechaCaja(models.Model):
	_inherit = 'account.payment'

	fecha_caja = fields.Date(string="Fecha de caja",default=datetime.today())

	@api.model
	def get_payment_vals(self):
		record = super(FechaCaja,self).get_payment_vals()
		record['fecha_caja'] = self.fecha_caja
		return record

class InheritFecha(models.Model):
	_inherit = 'account.move.line'

	fecha_account_move_line = fields.Date(related='payment_id.fecha_caja')
		

