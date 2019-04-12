from odoo import api, fields, models, exceptions
from functools import reduce 
from datetime import datetime 

class Packing_List(models.Model):
	_name = 'packing.list'
	name = fields.Char(string="Nombre", default='Nuevo',copy=False)
	stock_location_id = fields.Many2one('stock.location','Almacen')
	order_line_ids = fields.One2many('packing.list.line','main_id',string='lines',copy=False)
	order_filter = fields.Many2one('glass.order',string='Orden de Produccion')
	selected_line_ids = fields.One2many('glass.order.line.packing.list','packing_id',string="Cristales Seleccionados",copy=False)
	grouped_lines = fields.One2many('packing.list.grouped.line','parent_id',string='Lineas resumen',copy=False)
	state = fields.Selection([('draft','Borrador'),('process','En proceso'),('done','Finalizada')],default='draft',copy=False)
	date = fields.Date('Fecha de Packing List', default=fields.Date.today)
	location = fields.Many2one('custom.glass.location',string='Ubicacion') 
	picking_type = fields.Many2one('stock.picking.type')
	traslate_motive = fields.Many2one('einvoice.catalog.12','Motivo traslado Packing List')
	stock_picking = fields.Many2one('stock.picking',string="Picking")
	picking_count = fields.Integer(compute='_compute_glass_picking', default=0)

	@api.depends('stock_picking')
	def _compute_glass_picking(self):
		if self.stock_picking:
			self.picking_count = 1
		else:
			self.picking_count = 0

	@api.model
	def default_get(self,fields):
		res = super(Packing_List,self).default_get(fields)
		config_data = self.env['packing.list.config'].search([])
		if len(config_data)==0:
			raise exceptions.Warning(u'No se encontraron los valores de configuracion para Packing List')		
		config_data = self.env['packing.list.config'].search([])[0]
		res.update({'location':config_data.custom_location.id,'traslate_motive':config_data.traslate_motive_pl.id,
		'picking_type':config_data.picking_type_pl.id,
		'stock_location_id':config_data.warehouse_default.id})
		return res

	@api.multi
	def unlink(self):
		for record in self:
			if record.state in ('process','done'):
				raise exceptions.Warning('No es posible eliminar un Packing List cuando ha sido procesado o tiene estado finalizado.')
			return super(Packing_List,self).unlink()

	@api.multi
	def get_crystals_for_op(self):
		if self.order_filter:
			moves = self.order_filter.picking_out_ids.mapped('move_lines')
			for move in moves:
				filtered=move.glass_order_line_ids.filtered(lambda x: x.lot_line_id and not x.lot_line_id.entregado and not x.in_packing_list)
				for line in filtered:
					if line.id not in self.order_line_ids.mapped('order_line_id').ids:
						new = self.env['packing.list.line'].create({
							'selected':True,
							'picking_id':move.picking_id.id,
							'origin':move.picking_id.origin,
							'invoice_id':line.order_id.invoice_ids[0].id,
							'order_line_id': line.id,
							'order_id':line.order_id.id,
							'product_id':line.product_id.id,
							'main_id':self.id,
							'decorator': 'warning' if line.id in self.selected_line_ids.mapped('order_line_id').ids else ''
							})
						self.write({'order_line_ids':[(4,new.id)]})
			self.order_filter = False
			return {'value':{'order_line_ids':self.order_line_ids.ids}}
		else:
			raise exceptions.Warning('No ha seleccionado ninguna OP')

	@api.multi
	def add_selected_items(self):
		for record in self:
			for item in record.order_line_ids:
				if item.order_line_id.id not in record.selected_line_ids.mapped('order_line_id').ids and item.selected:
					new = self.env['glass.order.line.packing.list'].create({
					'picking_id':item.picking_id.id,
					'origin':item.picking_id.origin,
					'invoice_id':item.order_id.invoice_ids[0].id,
					'order_line_id': item.order_line_id.id,
					'order_id':item.order_id.id,
					'product_id':item.product_id.id,
					'packing_id':item.main_id.id,
					'location_tmp':self.location.id,
					'measures':item.measures,
					})
					item.write({'decorator' : 'warning'})
					record.write({'selected_line_ids':[(4,new.id)]})
			record.refresh_resume_lines()

	@api.multi
	def clear_all_lines(self):
		for item in self.order_line_ids:
			item.unlink()


	@api.multi
	def execute_packing_list(self):
		if len(self.selected_line_ids) == 0:
			raise exceptions.Warning('No ha seleccionado ningun cristal para el Packing List.')
		config_data = self.env['packing.list.config'].search([])
		if len(config_data)==0:
			raise exceptions.Warning(u'No se encontraron los valores de configuracion para Packing List')		
		config_data = self.env['packing.list.config'].search([])[0]		
		self.refresh_resume_lines()
		self.clear_all_lines()
		
		currency_obj = self.env['res.currency'].search([('name','=','USD')])
		if len(currency_obj)>0:
			currency_obj = currency_obj[0]
		else:
			raise exceptions.Warning( 'Error!\nNo existe la moneda USD \nEs necesario crear la moneda USD para un correcto proceso.' )

		tipo_cambio = self.env['res.currency.rate'].search([('name','=',str(self.date)),('currency_id','=',currency_obj.id)])

		if len(tipo_cambio)>0:
			tipo_cambio = tipo_cambio[0]
		else:
			raise exceptions.Warning( u'Error!\nNo existe el tipo de cambio para la fecha: '+ str(self.date) + u'\n Debe actualizar sus tipos de cambio para realizar esta operacion')

		new = self.env['stock.picking'].create({
			'picking_type_id': self.picking_type.id,
			'partner_id': None,
			'date': datetime.now(),
			'fecha_kardex': self.date if self.date else datetime.now().date(),
			'origin': self.name,
			'packing_list_id':self.id,
			'location_dest_id': self.picking_type.default_location_dest_id.id,
			'location_id': self.picking_type.default_location_src_id.id,
			'company_id': self.env.user.company_id.id,
			'einvoice_12': self.traslate_motive.id,
		})

		for item in self.selected_line_ids.mapped('order_line_id'):
			move = self.env['stock.move'].create({
				'name': item.product_id.name or '',
				'product_id': item.product_id.id,
				'product_uom': item.product_id.uom_id.id,
				'date': datetime.now(),
				'date_expected': datetime.now(),
				'location_id': new.location_id.id,
				'location_dest_id': new.location_dest_id.id,
				'picking_id': new.id,
				'partner_id': None,
				'move_dest_id': False,
				'state': 'draft',
				'company_id': new.company_id.id,
				'picking_type_id': new.picking_type_id.id,
				'procurement_id': False,
				'origin': new.origin,
				'route_ids': new.picking_type_id.warehouse_id and [(6, 0, [x.id for x in new.picking_type_id.warehouse_id.route_ids])] or [],
				'warehouse_id': new.picking_type_id.warehouse_id.id,
				'product_uom_qty': item.lot_line_id.area,
				'glass_order_line_ids': [(6,0,[item.id])],
			})
			new.write({'move_lines': [(4,move.id)]})

		# context = None
		# action = new.do_new_transfer()
		# if type(action) == type({}):
		# 	if action['res_model'] == 'stock.immediate.transfer' or action['res_model'] == 'stock.backorder.confirmation':
		# 		context = action['context']
		# 		sit = self.env['stock.immediate.transfer'].with_context(context).create({'pick_id': new.id})	
		# 		sit.process()
		# 	elif action['res_model'] == 'confirm.date.picking':
		# 		context = action['context']
		# 		cdp = self.env['confirm.date.picking'].with_context(context).create({'pick_id':new.id,'date':new.fecha_kardex})
		# 		res = cdp.changed_date_pincking()

		for item in self.selected_line_ids:
			line = item.order_line_id
			line.write({
				'in_packing_list':True,
				'locations':[(4,item.location_tmp.id)]
			})
			
		self.write({
			'name': config_data.seq_packing_list.next_by_id(),
			'stock_picking':new.id,
			'state':'process'
		})

	@api.multi
	def ending_packing_list(self):
		print('Finalizando Packing list')

	@api.multi
	def action_view_stock_picking(self):
		return {
			'res_id': self.stock_picking.id,
			'type': 'ir.actions.act_window',
			'res_model': 'stock.picking',
			'views':[(self.env.ref('stock.view_picking_form').id, 'form')],
		}
		
		

	@api.multi
	def refresh_resume_lines(self):
		for record in self:
			for item in record.grouped_lines:
				item.unlink()
			lines = record.selected_line_ids.mapped('order_line_id')				
			for prod in set(lines.mapped('product_id')):
				fil_list = lines.filtered(lambda x:x.product_id.id == prod.id)
				total_area = reduce(lambda x,y:x+y,fil_list.mapped('area'))#changed
				total_weight = reduce(lambda x,y: x+y,fil_list.mapped('peso'))
				new = self.env['packing.list.grouped.line'].create({
				'parent_id':self.id, 
				'product_id':prod.id, 
				'count_crystals':len(fil_list), 
				'area':float(total_area), 
				'weight': float(total_weight), 
				})
				self.write({'grouped_lines': [(4,new.id)]})

class Packing_List_Line(models.Model):
	_name='packing.list.line'

	main_id = fields.Many2one('packing.list',string='Main')
	selected = fields.Boolean('Ver')
	order_line_id = fields.Many2one('glass.order.line',string='Order Line')
	order_id = fields.Many2one('glass.order','OP')
	product_id = fields.Many2one('product.product','Producto')
	picking_id = fields.Many2one('stock.picking')
	invoice_id = fields.Many2one('account.invoice')
	origin  = fields.Char(related='picking_id.origin')
	crystal_number = fields.Integer(related='order_line_id.crystal_number',string='Nro Cristal')
	partner_id = fields.Many2one(related='order_line_id.partner_id',string='Cliente')
	measures = fields.Char(compute='_get_measures_item',string='Medidas',store=True)
	#weight = fields.Float(related ='order_line_id.peso',string='Peso', digits=(20,4))
	decorator = fields.Char()

	@api.depends('order_line_id')
	def _get_measures_item(self):
		for record  in self:
			base1,base2,height1,height2 = str(record.order_line_id.base1),str(record.order_line_id.base2),str(record.order_line_id.altura1),str(record.order_line_id.altura2)
			label = ''
			if base1 == base2:
				label += base1
			else:
				label += base1 + '/' + base2
			label += 'X'
			if height1 == height2:
				label += height1
			else:
				label += height1 + '/' + height2
			record.measures = label


	@api.multi
	def add_item(self):
		if self.order_line_id.id not in self.main_id.selected_line_ids.mapped('order_line_id').ids and self.selected:
			new = self.env['glass.order.line.packing.list'].create({
			'picking_id':self.picking_id.id,
			'origin':self.picking_id.origin,
			'invoice_id':self.order_id.invoice_ids[0].id,
			'order_line_id': self.order_line_id.id,
			'order_id':self.order_id.id,
			'product_id':self.product_id.id,
			'packing_id':self.main_id.id,
			'location_tmp':self.main_id.location.id,
			'measures':self.measures,
			})
			self.main_id.write({'selected_line_ids':[(4,new.id)],})
			self.main_id.refresh_resume_lines()
			
			self.decorator = 'warning'
			self.selected = not self.selected
		else:
			raise exceptions.Warning('Este cristal ya se encuentra en la lista de seleccionados o no fue marcado como check')

	@api.multi
	def check(self):
		self.selected = not self.selected


class Packing_List_Grouped_Line(models.Model):
	_name='packing.list.grouped.line'
	parent_id = fields.Many2one('packing.list',string='Parent')
	product_id = fields.Many2one('product.product')
	count_crystals = fields.Integer('Nro de cristales')
	area = fields.Float(string='Area', digits=(20,4))
	weight = fields.Float('Peso', digits=(20,4))

class Glass_Order_Line_Packing_List(models.Model):
	_name = 'glass.order.line.packing.list'
	packing_id = fields.Many2one('packing.list',string="Packing List")
	order_line_id = fields.Many2one('glass.order.line',string='Order Line')
	order_id = fields.Many2one('glass.order','OP')
	product_id = fields.Many2one('product.product','Producto')
	picking_id = fields.Many2one('stock.picking')
	invoice_id = fields.Many2one('account.invoice')
	origin  = fields.Char(related='picking_id.origin')
	crystal_number = fields.Integer(related='order_line_id.crystal_number',string='Nro Cristal')
	lot_id = fields.Many2one(related='order_line_id.lot_line_id.lot_id',string='Lote')
	requisition_id = fields.Many2one(related='lot_id.requisition_id',string='Requisicion')
	partner_id = fields.Many2one(related='order_line_id.partner_id',string='Cliente')
	location_tmp = fields.Many2one('custom.glass.location',string='Ubicacion')
	warehouse_tmp = fields.Many2one(related='location_tmp.location_code',string='Almacen')
	measures = fields.Char(string='Medidas')
	weight = fields.Float(related ='order_line_id.peso',string='Peso', digits=(20,4))
	area = fields.Float(related='order_line_id.lot_line_id.area',string="Area",digits=(12,4))

class Glass_Order_Line(models.Model):
	_inherit = 'glass.order.line'
	in_packing_list = fields.Boolean('En Packing List')