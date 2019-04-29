from odoo import api, fields, models
from datetime import datetime

class StockReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'

	@api.multi
	def create_returns(self):
		t = super(StockReturnPicking,self).create_returns()
		print('inter')
		if self._context.get('lines_to_return'):
			print('ctx',self._context.get('lines_to_return'))
			for item in self._context['lines_to_return']:
				print('lol',item['line'])
				line = self.env['glass.order.line'].browse(item['line'])
				print('lol 2: ',line)
				data = {
					'user_id':self.env.uid,
					'date':datetime.now(),
					'time':datetime.now().time(),
					'stage':'roto',
					'lot_line_id':line.lot_line_id.id,
					'date_fisical':datetime.now().date(),
					'break_motive':item['motive']
				}
				line.lot_line_id.is_break=True
				stage_obj = self.env['glass.stage.record'].create(data)
				line.write({
					'last_lot_line':line.lot_line_id.id,
					'glass_break':True,
					'lot_line_id':False,
					'is_used':False,
					'state':'process',
				})
		return t

	# Obtenemos los cristale que seran devueltos:
	@api.multi
	def get_crystals_list_for_return(self):
		for record in self:
			sql_ext = ','.join(map(str,record.product_return_moves.mapped('move_id').ids))
			self.env.cr.execute("""
			select 
			glor.name as origen,
			gl.name as lote,
			sm.product_qty as cantidad,
			sm.picking_id as picking_id,
			sm.id as sm_id,
			scpl.base1 as base1,
			scpl.base2 as base2,
			scpl.altura1 as altura1,
			scpl.altura2 as altura2,
			gol.crystal_number as numero_cristal,
			gol.state as estado,
			gol.product_id as product_id,
			gol.id as gol_id,
			gll.area as cristal_area,
			gll.templado as templado,
			gll.entregado as entregado,
			gll.ingresado as ingresado,
			gll.id as gll_id,
			grq.name as requisicion
			from 
			glass_order_line_stock_move_rel rel
			join glass_order_line gol on gol.id = rel.glass_order_line_id
			join stock_move sm on sm.id = rel.stock_move_id
			left join sale_calculadora_proforma_line scpl on scpl.id = gol.calc_line_id
			left join glass_lot_line gll on gol.lot_line_id = gll.id
			left join glass_lot gl on gl.id = gll.lot_id
			left join glass_requisition_line_lot grll on gll.lot_id = grll.lot_id
			left join glass_requisition grq on grll.requisition_id = grq.id
			left join glass_order glor on glor.id = gol.order_id
				where sm.id in  ("""+sql_ext+""")  order by origen, numero_cristal 
			""")

			results = self.env.cr.dictfetchall()
			elem = []
			for val in results:
				val['mode'] = 'return_crystals'
				tmp = self.env['detail.crystals.entered.wizard.line'].create(val)
				elem.append(tmp.id)
			
			wizard = self.env['detail.crystals.entered.wizard'].create({})
			wizard.write({'detail_lines': [(6,0,elem)]})
			view_id = self.env.ref('glass_production_order.show_detail_lines_entered_stock_wizard',False)
			return {
				'name': 'Escoger Cristales a romper o devolver',
				'res_id': wizard.id,
				'type': 'ir.actions.act_window',
				'res_model': 'detail.crystals.entered.wizard',
				'view_mode': 'form',
				'view_type': 'form',
				'views': [(view_id.id, 'form')],
				'target': 'new',
				'context': {'first_wizard': self.id,'mode':'return_crystals'} 
			}