# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class StockMove(models.Model):
	_inherit='stock.move'

	retazo_origen = fields.Char('Retazo Origen', compute="getretazo_product_id")
	glass_order_line_ids = fields.Many2many('glass.order.line','glass_order_line_stock_move_rel','stock_move_id','glass_order_line_id',string='Glass Order Lines')
	show_buttons = fields.Char('Mostrar_botones', compute='_get_show_buttons')

	# Visualizar los botones en funcion a si es un albaran de entrada o de salida:
	@api.depends('picking_id')
	def _get_show_buttons(self):
		for record in self:
			pick = record.picking_id.picking_type_id.code
			if pick == 'internal':
				record.show_buttons = 'source'
			elif pick == 'outgoing':
				record.show_buttons = 'to_deliver'

	@api.one
	@api.depends('product_id')
	def getretazo_product_id(self):
		cad=""
		if self.product_id:
			if self.product_id.uom_id.is_retazo:
				cad=str(self.product_id.uom_id.ancho)+"x"+ str(self.product_id.uom_id.alto)
				self.retazo_origen = cad

# Obtiene los del detalle de los cristales que conforman 
# el stock_move de salida (para entrega a clientes)
	@api.multi
	def get_results(self):
		calc_line_ids = self.procurement_id.sale_line_id.id_type.id_line.ids
		lines = self.env['glass.order.line'].search([('calc_line_id','in',calc_line_ids)])
		wizard = self.env['glass.lines.for.move.wizard'].create({})
		for line in lines:
			wizard_line = self.env['move.glass.wizard.line'].create({
				'main_id':wizard.id,
				'move_id':self.id,
				'glass_line_id':line.id,
				'lot_line_id':line.lot_line_id.id,
			})
		module = __name__.split('addons.')[1].split('.')[0]
		view_id = self.env.ref('%s.glass_lines_for_move_wizard_form_view' % module,False)
		return {
			'name': 'Seleccionar Cristales',
			'res_id': wizard.id,
			'type': 'ir.actions.act_window',
			'res_model': 'glass.lines.for.move.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [(view_id.id, 'form')],
			'target': 'new',
		}

# Obtiene los del detalle de los cristales que conforman 
# el stock_move ingresado a almacen, se us para devolver cristales rotos en almacen,
	@api.multi
	def get_detail_lines_entered_to_stock(self):
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
		left join stock_picking sp on sp.id = sm.picking_id
		left join stock_picking_type spt on spt.id = sp.picking_type_id
	where sm.id = '"""+str(self.id)+"""' and spt.code='internal' order by origen, numero_cristal
		""")

		results = self.env.cr.dictfetchall()
		elem = []
		for val in results:
			val['mode'] = 'view_origin'
			tmp = self.env['detail.crystals.entered.wizard.line'].create(val)
			elem.append(tmp.id)
		
		wizard = self.env['detail.crystals.entered.wizard'].create({})
		wizard.write({'detail_lines': [(6,0,elem)]})
		module = __name__.split('addons.')[1].split('.')[0]
		view_id =self.env.ref('%s.show_detail_lines_entered_stock_wizard' % module,False)
		return {
			'name':'Ver cristales de origen',
			'res_id': wizard.id,
			'type': 'ir.actions.act_window',
			'res_model': 'detail.crystals.entered.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'views': [(view_id.id, 'form')],
			'target': 'new',
			'context': {'mode':'view_origin'}
		}