# -*- coding: utf-8 -*-

from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError


class PsckingListConfig(models.Model):
	_name = 'packing.list.config'
	
	name = fields.Char(u'Parámetros',default=u"Parámetros")
	seq_packing_list=fields.Many2one('ir.sequence',u'Secuencia para los Packing List')
	picking_type_pl = fields.Many2one('stock.picking.type',u'Tipo Picking - Packing List')
	traslate_motive_pl = fields.Many2one('einvoice.catalog.12','Motivo traslado Packing List')
	warehouse_default = fields.Many2one('stock.location',string='Almacen de Origen')
	custom_location = fields.Many2one('custom.glass.location',u'Ubicación por defecto')



#config_data.seq_packing_list.next_by_id()




