from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class StockPicking(models.Model):
	_inherit = 'stock.picking'
	
	packing_list_id = fields.Many2one('packing.list',string='Packing List') 
	# picking_ids = fields.Many2many('stock.picking','packing_list_stock_picking_rel','picking_id','packing_id')