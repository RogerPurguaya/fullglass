# coding=utf-8

from odoo import models, api, fields, exceptions
from datetime import datetime

class Config_Payment_Terms(models.Model):
	_name = 'config.payment.term'
	date = fields.Date('Fecha', default=datetime.now().date())
	# porcentage de pago minimo 
	minimal = fields.Selection([
		(25,'Pago minimo de 25 por ciento'),
		(50,'Pago minimo de 50 por ciento'),
		(75,'Pago minimo de 75 por ciento'),
		(100,'Pago completo (100 por ciento)')
		],string='Requiere para emitir OP')
	# tipo de operacion # esto se usa para validaciones, no cambiar
	operation = fields.Selection([
		('generate_op','Generar Orden de Produccion'),
		('enter_apt','Ingresar Cristales a APT'),
		],string='Operacion')
	description = fields.Text(string='Descripcion')
	payment_term_ids = fields.Many2many('account.payment.term','config_account_payment_rel','config_id','account_payment_id',string='Terminos de Pago')

	@api.constrains('operation')
	def _verify_not_repeat_motive(self):
		configs = self.env['config.payment.term'].search([])
		repeat = configs.filtered(lambda x: x.operation == self.operation)
		if len(repeat) > 1:
			operation= dict(self._fields['operation'].selection).get(self.operation)
			raise exceptions.Warning(u'Ya existe un configuracion para esta Operacion: ' + operation)

	# @api.constrains('minimal')
	# def _verify_not_repeat_motive(self):
	# 	configs = self.env['config.payment.term'].search([])
	# 	min_repeat = configs.filtered(lambda x: x.minimal == self.minimal)
	# 	if len(min_repeat) > 1:
	# 		if min_repeat[0].operation == min_repeat[1].operation:
	# 			minimal= dict(self._fields['minimal'].selection).get(self.minimal)
	# 			minimal= dict(self._fields['minimal'].selection).get(self.minimal)
	# 			raise exceptions.Warning(u'Ya existe un configuracion para este minimo:' + minimal)

	# @api.constrains('payment_term_ids')
	# def _verify_not_repeat_payment_term_ids(self):
	# 	configs = self.env['config.payment.term'].search([])
	# 	ids = []
	# 	for item in configs:
	# 		ids += item.payment_term_ids.ids
	# 	if len(ids) != len(set(ids)):
	# 		raise exceptions.Warning('Uno o varios de los terminos de pago ingresados ya sencuentran en una configuracion')




