# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassFurnace(models.Model):
	_name='glass.furnace'

	name = fields.Char('Lote de Horno')
	line_ids=fields.One2many('glass.furnace.line','main_id','Detalle')
	is_used = fields.Boolean('Usado')

class GlassFurnaceLine(models.Model):
	_name='glass.furnace.line'

	_rec_name = "lot_line_id"

	main_id = fields.Many2one('glass.furnace')

	lot_id = fields.Many2one('glass.lot','Lote')
	lot_line_id = fields.Many2one('glass.lot.line',u'Línea de lote')
	order_number = fields.Integer(u'Nro. Orden')
	crystal_number = fields.Char('Nro. Cristal')
	base1 = fields.Integer("Base1 (L 4)")
	base2 = fields.Integer("Base2 (L 2)")
	altura1 = fields.Integer("Altura1 (L 1)")
	altura2 = fields.Integer("Altura2 (L 3)")
	area = fields.Float(u'Área M2',digits=(20,4))
	partner_id = fields.Many2one('res.partner',string='Cliente')
	obra = fields.Char(string='Obra')
	is_used = fields.Boolean('Usado', default=False)