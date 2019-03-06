from odoo import fields,models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
import itertools

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	@api.multi
	def do_transfer(self):
		t = super(StockPicking,self).do_transfer()		
		# Si el albaran es de de salida, se asignan los campos necesarios:
		if self.picking_type_id.code == 'outgoing':
			for item in self.move_lines:
				for line in item.glass_order_line_ids:
					line.write({'state':'send2partner'})
					line.lot_line_id.write({'entregado':True})
					vals = {
						'user_id':self.env.uid,
						'date':datetime.now(),
						'time':datetime.now().time(),
						'stage':'entregado',
						'lot_line_id':line.lot_line_id.id
					}
					self.env['glass.stage.record'].create(vals)
		return t


# Wizard contenedor para ver los cristales de cada stock_move:
class Get_glass_lines_for_move(models.TransientModel):
	_name = 'glass.lines.for.move.wizard'
	get_glass_lines_for_move_ids = fields.One2many('get.glass.lines.for.move','wizard_id')
	# para mostrar el boton de generar lineas:
	show_button = fields.Boolean(string='Show button', compute='_get_show_button')
	warning_message = fields.Char()

	@api.depends('get_glass_lines_for_move_ids')
	def _get_show_button(self):
		for item in self:
			if len(item.get_glass_lines_for_move_ids) > 0:
				picking_id = item.get_glass_lines_for_move_ids[0].picking_id
				picking = self.env['stock.picking'].search([('id','=',picking_id)])
				if picking.state == 'done':
					item.show_button = False
				else:
					item.show_button = True
			else:
				item.show_button = False

	@api.multi
	def delivery_process(self):
		for item in self:
			selected_items = []
			bad_lines = []
			ext = '' #para mostrar los mensajitos
			for line in item.get_glass_lines_for_move_ids:
				if line.check:
					if line.ingresado and not line.entregado:
						selected_items.append(line)
					else:
						bad_lines.append(line)

			if len(bad_lines) > 0:
				message = 'No se pueden procesar las siguientes lineas: \n'
				for bad_line in bad_lines:
					motive = ' Ya entregado' if bad_line.entregado else ' No ingresado'
					ext += '-> '+str(bad_line.origen) + ' - ' +str(bad_line.numero_cristal) + motive +'\n'
				raise exceptions.Warning(message + ext)
			quantity = 0
			if len(selected_items) > 0:
				for item in selected_items:
					quantity += item.cristal_area
			else:
				selected_items = list(filter(lambda x: x.ingresado and not x.entregado, item.get_glass_lines_for_move_ids))
				if len(selected_items) == 0:
					raise exceptions.Warning(u'No hay lineas que cumplan los requisitos para procesarse (ingresadas y no entregadas).')
				for item in selected_items:
					quantity += item.cristal_area
			try:
				config = self.env['glass.order.config'].search([])[0]
			except IndexError as e:
				raise exceptions.Warning('No se han encontrado los valores de configuracion necesarios para esta operacion (Nro. cristales por guia)')
			
			if len(selected_items) > config.nro_cristales_guia:
				self.warning_message = 'El Numero de cristales a procesar es superior al valor maximo configurado. \n solo se han procesado los '+str(config.nro_cristales_guia)+' primeros cristales.'
				selected_items = selected_items[:config.nro_cristales_guia]

			pack_operation = self.env['stock.pack.operation'].search([('picking_id','=',int(line.picking_id)),('product_id','=',int(line.product_id))])
			pack_operation.write({'qty_done':quantity})

			glass_order_lines_ids = map(lambda x: int(x.gol_id), selected_items)
			move_out = self.env['stock.move'].search([('id','=',int(line.sm_id))])
			move_out.write({'glass_order_line_ids':[(6,0,glass_order_lines_ids)]})


class Get_glass_lines_for_move(models.TransientModel):
	_name = 'get.glass.lines.for.move'
	
	check = fields.Boolean(string='Seleccion')
	wizard_id = fields.Many2one('glass.lines.for.move.wizard')
	origen = fields.Char(string='Origen') 
	cantidad = fields.Float('Cantidad' ,digits=(12,4))
	picking_id = fields.Integer('Picking')
	venta = fields.Char(string='Venta')
	base1 = fields.Integer(string='Base 1')
	base2 = fields.Integer(string='Base 2')
	altura1 = fields.Integer(string='Altura 1')
	altura2 = fields.Integer(string='Altura 1')
	numero_cristal = fields.Integer(string='Numero Cristal')
	product_id = fields.Char(string='Producto ID')
	cristal_area = fields.Float(string='Cristal Area' ,digits=(12,4))
	templado = fields.Boolean(string='Templado')
	ingresado = fields.Boolean(string='Ingresado')
	entregado = fields.Boolean(string='Entregado') 
	requisicion = fields.Char(string='Requisicion')
	remision = fields.Char('Nro. Guia Remision')
	#add
	gol_id = fields.Char('Glass order line id')
	gll_id = fields.Char('Glass Lote Line id')
	sm_id  =  fields.Integer('Move ID')

	# aun no funciona :(
	@api.multi
	def checking_field(self):
		self.ensure_one()
		check = self.check
		self.check = not check
		return {"type": "ir.actions.do_nothing"}




