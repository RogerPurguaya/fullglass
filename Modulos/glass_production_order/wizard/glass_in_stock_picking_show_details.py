from odoo import fields,models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import reduce
import itertools

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	# @api.multi
	# def do_transfer(self):
	# 	t = super(StockPicking,self).do_transfer()		
	# 	Si el albaran es de de salida, se asignan los campos necesarios:
	# 	if self.picking_type_id.code == 'outgoing':
	# 		for item in self.move_lines:
	# 			for line in item.glass_order_line_ids:
	# 				line.write({'state':'send2partner'})
	# 				line.lot_line_id.write({'entregado':True})
	# 				vals = {
	# 					'user_id':self.env.uid,
	# 					'date':datetime.now().date(),
	# 					'time':datetime.now().time(),
	# 					'stage':'entregado',
	# 					'lot_line_id':line.lot_line_id.id
	# 				}
	# 				self.env['glass.stage.record'].create(vals)
	# 	return t

# Wizard contenedor para ver los cristales de cada stock_move:
class Get_glass_lines_for_move(models.TransientModel):
	_name = 'glass.lines.for.move.wizard'
	move_glass_wizard_line_ids = fields.One2many('move.glass.wizard.line','main_id')
	show_button = fields.Boolean(string='Show button', compute='_get_show_button')
	warning_message = fields.Char()

	@api.depends('move_glass_wizard_line_ids')
	def _get_show_button(self):
		for item in self:
			if len(item.move_glass_wizard_line_ids) > 0:
				picking = item.move_glass_wizard_line_ids.mapped('picking_id')[0]
				if picking.state == 'done':
					item.show_button = False
				else:
					item.show_button = True
			else:
				item.show_button = False

	@api.multi
	def delivery_process(self):
		self.ensure_one()
		try:
			config = self.env['glass.order.config'].search([])[0]
		except IndexError as e:
			raise exceptions.Warning('No se han encontrado los valores de configuracion necesarios para esta operacion (Nro. cristales por guia)')
		
		lines = self.move_glass_wizard_line_ids.filtered(lambda x: x.check)
		if len(lines) > 0:
			sended       = lines.filtered(lambda x: x.entregado)
			not_entried  = lines.filtered(lambda x: not x.ingresado)
			packing_list = lines.filtered(lambda x: x.packing_list)
			msg = ''
			for item in sended:
				msg+=item.order_id.name+' '+str(item.crystal_num)+' : Ya Entregado'+'\n'
			for item in not_entried:
				msg+=item.order_id.name+' '+str(item.crystal_num)+' : No ingresado'+'\n'
			for item in packing_list:
				msg+=item.order_id.name+' '+str(item.crystal_num)+' : En Packing List'+'\n'
			if msg != '':
				raise UserError('No es posible procesar los siguientes cristales:\n'+msg)
		else:
			lines = self.move_glass_wizard_line_ids.filtered(lambda x: not x.entregado and x.ingresado and not x.packing_list)
		
		if len(lines) == 0:
			raise UserError(u'No hay lineas que cumplan los requisitos para procesarse (ingresadas y no entregadas).')

		max_items = config.nro_cristales_guia
		lines = lines[:max_items]
		picking = lines.mapped('picking_id')[0]
		product = lines.mapped('product_id')[0]
		move    = lines.mapped('move_id')[0]
		quantity = reduce(lambda x,y: x+y,lines.mapped('area'))
		try:
			picking.action_assign()
		except UserError as e:
			raise UserError('No fue posible procesar los cristales:\nPosible Causa:\n'+e)
		
		pack_operation = picking.pack_operation_product_ids.filtered(lambda x: x.product_id.id == product.id)
		print('pack: ',pack_operation)
		pack_operation.write({'qty_done':quantity})
		
		action = picking.do_new_transfer()
		context,bad_execution,motive = None,None,None
		if type(action) == type({}):
			if action['res_model'] == 'stock.immediate.transfer' or action['res_model'] == 'stock.backorder.confirmation':
				context = action['context']
				sit = self.env['stock.immediate.transfer'].with_context(context).create({'pick_id': picking.id})	
				try:
					sit.process()
				except UserError as e:
					bad_execution = picking.name
					motive = str(e)
		if bad_execution:
			raise UserError('No fue posible procesar los siguiente Picking: '+bad_execution+'\nPosible causa: '+motive)
		move.write({'glass_order_line_ids':[(6,0,lines.mapped('glass_line_id').ids)]})
		for line in lines:
			line.glass_line_id.write({'state':'send2partner'})
			line.lot_line_id.write({'entregado':True})
			stage = self.env['glass.stage.record'].create({
				'user_id':self.env.uid,
				'date':datetime.now().date(),
				'time':datetime.now().time(),
				'stage':'entregado',
				'lot_line_id':line.lot_line_id.id
			})
		a = b
		return True

class MoveGlassWizardLines(models.TransientModel):
	_name = 'move.glass.wizard.line'

	check     = fields.Boolean(string='Seleccion')
	main_id = fields.Many2one('glass.lines.for.move.wizard')
	move_id = fields.Many2one('stock.move')
	glass_line_id = fields.Many2one('glass.order.line')
	order_id = fields.Many2one(related='glass_line_id.order_id')
	lot_line_id = fields.Many2one('glass.lot.line')
	quantity    = fields.Float(related='move_id.product_qty') 
	picking_id  = fields.Many2one(related='move_id.picking_id') 
	sale_qty    = fields.Float(related='move_id.procurement_id.sale_line_id.product_uom_qty')
	base1   = fields.Integer(related='glass_line_id.base1',string='Base 1')
	base2   = fields.Integer(related='glass_line_id.base2',string='Base 2')
	height1 = fields.Integer(related='glass_line_id.altura1',string='Altura 1')
	height2 = fields.Integer(related='glass_line_id.altura2',string='Altura 2')
	crystal_num =  fields.Integer(related='glass_line_id.crystal_number',string='Num. Cristal')
	state = fields.Selection(related='glass_line_id.state',string='Estado')
	product_id = fields.Many2one(related='glass_line_id.product_id',string='Producto')
	area = fields.Float(related='glass_line_id.area',string='Area')
	templado  = fields.Boolean(related='lot_line_id.templado',string='Templado')
	ingresado = fields.Boolean(related='lot_line_id.ingresado',string='Ingresado')
	entregado = fields.Boolean(related='lot_line_id.entregado',string='Entregado') 
	packing_list = fields.Boolean(related='glass_line_id.in_packing_list',string='Packing List')
	req_id = fields.Many2one(related='lot_line_id.lot_id.requisition_id',string='Requisicion')
	numberg = fields.Char('Guia remision', compute='_get_numberg')

	@api.depends('order_id')
	def _get_numberg(self):
		for rec in self:
			pickings = rec.order_id.sale_order_id.mapped('picking_ids')
			picking  = pickings.filtered(lambda x: rec.glass_line_id.id in x.move_lines.mapped('glass_order_line_ids').ids and x.numberg)
			if len(picking) == 1:
				rec.numberg = picking[0].numberg
			else:
				rec.numberg = ''