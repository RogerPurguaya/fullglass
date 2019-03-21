from odoo import fields,models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import reduce

# Wizard contenedor para ver los cristales de los stock_moves a retornar:
class Crystals_For_Packinglist_Wizard(models.TransientModel):
	_name = 'crystals.for.packinglist.wizard'
	detail_lines = fields.One2many('crystals.for.packinglist.wizard.line','wizard_id')
	# para mostrar el boton de confirmacion:
	show_button = fields.Boolean(string='Show button', compute='_get_show_button')
	warning_message = fields.Char()
	
	@api.depends('detail_lines')
	def _get_show_button(self):
		for item in self:
			if len(item.detail_lines) > 0:
				item.show_button = True
			else:
				item.show_button = False

	@api.multi
	def select_crystals_to_packing_list(self):
		for record in self:
			selected_lines = record.detail_lines.filtered(lambda i: i.check)
			if len(selected_lines) == 0:
				raise exceptions.Warning('No ha seleccionado ningun cristal para el Packing List.')
			else:
				bad_lines = selected_lines.filtered(lambda x: x.entregado or x.packing)
				if len(bad_lines) > 0:
					msg = ''
					for bad in bad_lines:
						msg+='-> '+str(bad.origen)+' - '+str(bad.numero_cristal)+'\n' 
					raise exceptions.Warning('No es posible agregar los siguientes cristales:\n'+msg+'Posibles motivos:\n-Ya se encuentran agregados al Packing List.\n-Ya fueron entregados al cliente.')
				
				print('el id actual: ', self._context.get('main_id'))

				obj_main = self.env['packing.list'].browse(self._context.get('main_id'))
				obj_parent = self.env['packing.list.line'].browse(self._context.get('parent_id'))

				for line_id in selected_lines.mapped('gol_id'):
					order_line = self.env['glass.order.line'].browse(line_id)
					self.env['glass.order.line.packing.list'].create({
						'glass_line_id':order_line.id,
						'packing_id':obj_main.id,
						'parent_id':obj_parent.id, 
					})
					obj_main.write({'order_line_ids':[(4,line_id)]})
				
				for prod_id in set(selected_lines.mapped('product_id')):
					fil_list = selected_lines.filtered(lambda x:x.product_id == prod_id)
					total_area = reduce(lambda x,y:x+y,fil_list.mapped('cristal_area'))

					exists = obj_main.grouped_lines.filtered(lambda x: x.product_id.id == prod_id)

					if len(exists) == 1:
						exists.area += float(total_area)
						exists.count_crystals += len(fil_list)
					else:
						new = self.env['packing.list.grouped.line'].create({
					'parent_id':obj_main.id, 
					'product_id':self.env['product.product'].browse(prod_id)[0].id, 
					'count_crystals':len(fil_list), 
					'area':float(total_area),  
						})
						obj_main.write({'grouped_lines': [(4,new.id)]})

				view_id = self.env.ref('packing_list_fullglass.view_packing_list_form')
				return {
						'res_id': obj_main.id,
						'type': 'ir.actions.act_window',
						'res_model': 'packing.list',
						'view_mode': 'form',
						'view_type': 'form',
						'views': [(view_id.id, 'form')],
						'target': 'main',
					}

 # Cristale a seleccionar para el packing list
class Crystals_For_Packinglist_Wizard_Line(models.TransientModel):
	_name = 'crystals.for.packinglist.wizard.line'
	
	check = fields.Boolean(string='Seleccion')
	wizard_id = fields.Many2one('crystals.for.packinglist.wizard')
	origen = fields.Char(string='Origen')
	lote= fields.Char(string='Lote') 
	cantidad = fields.Float('Cantidad' ,digits=(12,4))
	picking_id = fields.Integer('Picking')
	venta = fields.Char(string='Venta')
	base1 = fields.Integer(string='Base 1')
	base2 = fields.Integer(string='Base 2')
	altura1 = fields.Integer(string='Altura 1')
	altura2 = fields.Integer(string='Altura 1')
	numero_cristal = fields.Integer(string='Numero Cristal')
	product_id = fields.Integer(string='Producto ID')
	cristal_area = fields.Float(string='Cristal Area' ,digits=(12,4))
	templado = fields.Boolean(string='Templado')
	ingresado = fields.Boolean(string='Ingresado')
	entregado = fields.Boolean(string='Entregado') 
	requisicion = fields.Char(string='Requisicion')
	gol_id = fields.Integer('Glass order line id')
	gll_id = fields.Integer('Glass Lote Line id')
	sm_id  =  fields.Integer('Move ID')
	packing = fields.Integer('Packing')
	# aun no funciona :(
	@api.multi
	def checking_field(self):
		self.ensure_one()
		check = self.check
		self.check = not check
		return {"type": "ir.actions.do_nothing"}