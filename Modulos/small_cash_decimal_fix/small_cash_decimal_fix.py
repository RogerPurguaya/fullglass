# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class account_transfer_it(models.Model):
	_inherit = 'account.transfer.it'

	tc_personalizado = fields.Float('T.C. Personalizado',digits=(12,5))

class account_move_line(models.Model):
	_inherit = 'account.move.line'

	tc = fields.Float('T.C.',digits=(12,5))