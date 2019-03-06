from odoo import fields,models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import reduce

# Wizard contenedor para ver los cristales de los stock_moves a retornar:
class Detail_Crystals_Entered_Wizard(models.TransientModel):
	_name = 'detail.crystals.entered.wizard'
	detail_lines = fields.One2many('detail.crystals.entered.wizard.line','wizard_id')
	# para mostrar el boton de confirmacion:
	show_button = fields.Boolean(string='Show button', compute='_get_show_button')
	warning_message = fields.Char()

	@api.depends('detail_lines')
	def _get_show_button(self):
		for item in self:
			mode = self._context['mode']
			if mode == 'view_origin': # si el albaran es de entrada no muetsra el boton
				item.show_button = False
			elif len(item.detail_lines) > 0:
				item.show_button = True
			else:
				item.show_button = False

	@api.multi
	def select_crystals_to_return(self):
		for record in self:
			selected_lines = list(filter(lambda i: i.check, self.detail_lines))
			if len(selected_lines) == 0:
				raise exceptions.Warning('Debe seleccionar un(os) cristal(es) para devolver.')
			else:
				bad_lines = list(filter(lambda x: x.entregado or not x.gll_id, selected_lines))
				if len(bad_lines) > 0:
					msg = ''
					for bad in bad_lines:
						msg+='-> '+str(bad.origen)+' - '+str(bad.numero_cristal)+'\n' 
					raise exceptions.Warning('Los siguientes cristales ya se han marcado como entregados o ya fueron devueltos: \n' + msg)
				product_ids = set(map(lambda x: x.product_id, selected_lines))
				for prod_id in product_ids:
					filter_list = list(filter(lambda x:x.product_id == prod_id,selected_lines))
					quantitys = map(lambda x: x.cristal_area,filter_list)
					total_area = reduce(lambda x,y: x+y,quantitys)
					return_line = self.env['stock.return.picking.line'].search([('wizard_id','=',self._context['first_wizard']),('product_id','=',prod_id)])

					return_line.write({'quantity': float(total_area)})


				lines_to_return_ids = map(lambda x: x.gol_id, selected_lines)
				new_wizard = self.env['stock.return.picking'].search([('id','=',self._context['first_wizard'])])

				view_id = self.env.ref('stock.view_stock_return_picking_form')

				return {
						'name':'Revertir transferencia',
						'res_id': new_wizard.id,
						'type': 'ir.actions.act_window',
						'res_model': 'stock.return.picking',
						'view_mode': 'form',
						'view_type': 'form',
						'views': [(view_id.id, 'form')],
						'target': 'new',
						'context': {'lines_to_return':lines_to_return_ids}
					}

			


 # Contenedor para lineas de cristles a devolver desde APT
class Detail_Crystals_Entered_Wizard_Lines(models.TransientModel):
	_name = 'detail.crystals.entered.wizard.line'
	
	check = fields.Boolean(string='Seleccion')
	wizard_id = fields.Many2one('detail.crystals.entered.wizard')
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
	#add
	gol_id = fields.Integer('Glass order line id')
	gll_id = fields.Integer('Glass Lote Line id')
	sm_id  =  fields.Integer('Move ID')

	# aun no funciona :(
	@api.multi
	def checking_field(self):
		self.ensure_one()
		check = self.check
		self.check = not check
		return {"type": "ir.actions.do_nothing"}




