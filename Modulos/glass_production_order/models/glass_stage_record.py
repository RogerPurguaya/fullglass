# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassStageRecord(models.Model):
	_name='glass.stage.record'

	user_id = fields.Many2one('res.users','Usuario')
	date = fields.Date('Fecha')
	time = fields.Char('Hora')
	stage = fields.Selection([
		('optimizado','Optimizado'),
		('requisicion',u'Requisición'),
		('corte','Corte'),
		('pulido','Pulido'),
		('entalle','Entalle'),
		('lavado','Lavado'),
		('horno','Horno'),
		('templado','Templado'),
		('compra','Comprado'),
		('entregado','Entregado'),
		('ingresado','Ingresado'),
		('roto','Rotura'),
		('retirado','Retirado'),
		],'Etapa')
	lot_line_id = fields.Many2one('glass.lot.line',u'Línea de lote')
	date_fisical=fields.Date('Fecha de Rotura')




