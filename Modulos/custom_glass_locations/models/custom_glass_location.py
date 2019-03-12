# coding=utf-8

from odoo import models, api, fields, exceptions

class Custom_Glass_Location(models.Model):
	_name = 'custom.glass.location'

	name = fields.Char(u'Codigo')
	## ubicación de odoo al que pertenece:
	location_code =fields.Many2one('stock.location',u'Almacen')