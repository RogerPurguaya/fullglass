from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	identificador_glass = fields.Integer(index=True)
	identifier = fields.Char(index=True)
	#campo para almacenar la op origen de un albaran de ingreso a apt
	order_source_id = fields.Many2one('glass.order','OP origen')

	@api.model
	def create(self,vals):
		record = super(StockPicking,self).create(vals)
		if record.identificador_glass > 0:		
			requisition = self.env['glass.requisition'].search([('id','=',record.identificador_glass)])
			aux = []
			if record.identifier == 'mp':
				print('lo que va llegando: ', vals)
				for i in requisition.picking_mp_ids:
					aux.append(i[0].id)
				aux.append(record.id)
				requisition.picking_mp_ids = [(6,0,aux)]
			if record.identifier == 'rt':
				for i in requisition.picking_rt_ids:
					aux.append(i[0].id)
				aux.append(record.id)
				requisition.picking_rt_ids = [(6,0,aux)]
			if record.identifier == 'drt':
				for i in requisition.picking_drt_ids:
					aux.append(i[0].id)
				aux.append(record.id)
				requisition.picking_drt_ids = [(6,0,aux)]
		return record
