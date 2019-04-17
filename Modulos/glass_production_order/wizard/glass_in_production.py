# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime,timedelta
from functools import reduce

class GlassInProductionWizard(models.TransientModel):
	_name='glass.in.production.wizard'
	
	# def get_now_date(self):
	# 	now = datetime.now() - timedelta(hours=5) # hora peruana
	# 	return now.date()

	stock_type_id = fields.Many2one('stock.picking.type',u'Operación de almacén') 
	date_in = fields.Date('Fecha ingreso',default=datetime.now().date())
	order_ids = fields.One2many('glass.in.order','mainid','order_id')
	line_ids = fields.Many2many('glass.order.line','glass_in_lineorder_rel','in_id','line_id',string="Lineas")
	order_id = fields.Many2one('glass.order','Filtrar OP')
	search_param = fields.Selection([('glass_order','Orden de Produccion'),('search_code','Lectura de barras')],string='Busqueda por',default='search_code')
	message_erro = fields.Char()
	location_id  = fields.Many2one('custom.glass.location',string='Ubicacion')
	search_code  = fields.Char(string='Codigo de busqueda')

	@api.multi
	def get_new_element(self):
		wizard = self.env['glass.in.production.wizard'].create({})
		return {
			'res_id':wizard.id,
			'name':'Ingreso a la Produccion',
			'type': 'ir.actions.act_window',
			'res_model': 'glass.in.production.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def get_all_available(self):
		self.ensure_one()
		lines = self.env['glass.order.line'].search([('state','=','ended')])
		for item in lines.ids:
			if item not in self.line_ids.ids:
				self.write({'line_ids':[(4,item)]})
		return {"type": "ir.actions.do_nothing",}


	@api.multi
	def refresh_selected_lines(self):
		will_removed = self.line_ids.filtered(lambda x: x.order_id.id not in self.order_ids.mapped('order_id').ids)
		for item in will_removed.ids:
			self.write({'line_ids':[(3,item)]})
		return {"type": "ir.actions.do_nothing",}

	@api.depends('line_ids')
	@api.onchange('search_code')
	def onchangecode(self):
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]
		if self.search_code:			
			existe = self.env['glass.lot.line'].search([('search_code','=',self.search_code)])
			if len(existe)==1:
				line = existe.order_line_id
				if line.state!='ended':
					self.message_erro = 'La linea de orden no se encuentra en estado finalizado'
					self.search_code=""
					return
				this_obj=self.env['glass.in.production.wizard'].browse(self._origin.id) 
				if line not in this_obj.line_ids:
					line.location_tmp = self.location_id.id
					this_obj.write({'line_ids':[(4,line.id)]})
					self.search_code=""
					return {'value':{'line_ids':this_obj.line_ids.ids,'order_ids':this_obj.order_ids.ids}}
				else:
					self.message_erro = 'El registro ya se encuentra en la lista'
					self.search_code=""
			else:
				self.message_erro="Registro no encontrado!"
				self.search_code=""
				return
		else:
			return
	
	@api.onchange('order_id')
	def onchange_order_id(self):
		vals = {}
		aorder=[]
		for existente in self.order_ids:
			vals={
				'selected':existente.selected,
				'order_id':existente.order_id.id,
				'partner_id':existente.partner_id.id,
				'date_production':existente.date_production,
				'total_pzs':existente.total_pzs,
				'total_area':existente.total_area,
				}	
			aorder.append((0,0,vals))
		if self.order_id:
			vals={
				'selected':True,
				'order_id':self.order_id.id,
				'partner_id':self.order_id.partner_id.id,
				'date_production':self.order_id.date_production,
				'total_pzs':self.order_id.total_pzs,
				'total_area':self.order_id.total_area,
				}
			aorder.append((0,0,vals))
		return {'value':{'order_ids':aorder}}

	@api.depends('line_ids')
	@api.onchange('order_ids')
	def getlines(self):	
		lines = self.order_ids.filtered(lambda x:x.selected).mapped('order_id').mapped('line_ids').filtered(lambda x:x.state=='ended')
		if len(lines)>0:
			this_obj = self.env['glass.in.production.wizard'].browse(self._origin.id)
			for item in lines:
				if item not in this_obj.line_ids:
					item.location_tmp = self.location_id.id
					this_obj.write({'line_ids':[(4,item.id)]})
			return {'value':{'line_ids':this_obj.line_ids.ids}}

	@api.model
	def default_get(self,fields):
		res = super(GlassInProductionWizard,self).default_get(fields)
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]
		res.update({'stock_type_id':config_data.picking_type_pt.id})
		return res

	@api.multi
	def makeingreso(self):
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]
		#Es necesario verificar el tipo de cambio y la moneda 
		#para crear correctamente el picking y evitar crear stock moves erroneos, ya tambien verificar que todos los cristales tengan un orden de requisicion
		self.verify_constrains_for_process(self.date_in)
		
		grouped_lines = []
		picking_ids=[]
		useract = self.env.user
		grouped_ids =  set(self.line_ids.mapped('order_id').ids)
		#print('el primer agrupado : ', grouped_ids)
		for i in grouped_ids:
			sub = self.line_ids.filtered(lambda x: x.order_id.id == i)
			grouped_lines.append(list(sub))
		#print('el agrupado : ', grouped_lines)
		for lines in grouped_lines:
			order = lines[0].order_id
			data= {
				'picking_type_id': self.stock_type_id.id,
				'partner_id': None,
				'date': datetime.now(),
				'fecha_kardex': str(self.date_in),
				'origin': order.name,
				'order_source_id':order.id,
				'location_dest_id': self.stock_type_id.default_location_dest_id.id,
				'location_id': self.stock_type_id.default_location_src_id.id,
				'company_id': useract.company_id.id,
				'einvoice_12': config_data.traslate_motive_pt.id,
			}
			picking = self.env['stock.picking'].create(data)
			picking_ids.append(picking.id)
			moves_list = self._processing_stock_move_lines(lines,picking,useract,order)
			# pasamos el albaran generado a realizado:
			context = None
			action = picking.do_new_transfer()
			if type(action) == type({}):
				if action['res_model'] == 'stock.immediate.transfer' or action['res_model'] == 'stock.backorder.confirmation':
					context = action['context']
					sit = self.env['stock.immediate.transfer'].with_context(context).create({'pick_id': picking.id})	
					sit.process()
				elif action['res_model'] == 'confirm.date.picking':
					context = action['context']
					cdp = self.env['confirm.date.picking'].with_context(context).create({'pick_id':picking.id,'date':picking.fecha_kardex})
					res = cdp.changed_date_pincking()
			
			for line in lines:
				if line.location_tmp:
					line.write({
						'locations': [(4,line.location_tmp.id)],
						'state' : 'instock',
						})
				else:
					line.write({'state' : 'instock',})
				line.lot_line_id.ingresado = True
				line.location_tmp = False
				vals = {
					'user_id':self.env.uid,
					'date':datetime.now(),
					'time':datetime.now().time(),
					'stage':'ingresado',
					'lot_line_id':line.lot_line_id.id,
				}
				self.env['glass.stage.record'].create(vals)

			not_ended = order.line_ids.filtered(lambda x: x.state != 'instock')
			if len(not_ended) == 0:
				order.state='ended'

		return {
				'name':u'Picking',
				'view_type':'form',
				'view_mode':'tree,form',
				'res_model':'stock.picking',
				'type':'ir.actions.act_window',
				'domain':[('id','in',picking_ids)]
		}
# procesar las lineas del picking
	@api.multi
	def _processing_stock_move_lines(self,lines,picking,useract,order):
		move_list = []
		products_ids = set(map(lambda x: x.product_id.id,lines))
		
		for item in products_ids:
			filtered = list(filter(lambda x: x.product_id.id == item,lines))
			product = filtered[0].product_id #el prod sera el mismo
			areas = map(lambda x: x.area,filtered)
			total_area = reduce(lambda x,y: x+y,areas)

			vals = {
				'name': product.name or '',
				'product_id': product.id,
				'product_uom': product.uom_id.id,
				'date': datetime.now(),
				'date_expected': datetime.now(),
				'location_id': self.stock_type_id.default_location_src_id.id,
				'location_dest_id': self.stock_type_id.default_location_dest_id.id,
				'picking_id': picking.id,
				'partner_id': order.partner_id.id,
				'move_dest_id': False,
				'state': 'draft',
				'company_id': useract.company_id.id,
				'picking_type_id': self.stock_type_id.id,
				'procurement_id': False,
				'origin': order.name,
				'route_ids': self.stock_type_id.warehouse_id and [(6, 0, [x.id for x in self.stock_type_id.warehouse_id.route_ids])] or [],
				'warehouse_id': self.stock_type_id.warehouse_id.id,
				'product_uom_qty': total_area,
				'glass_order_line_ids': [(6,0,map(lambda x: x.id,filtered))]
			}
			move = self.env['stock.move'].create(vals)
			move_list.append(move)
		return move_list

#Metodo que verifica los tipos de cambio y moneda para la fecha de kardex, se realiza en 
# el proceso futuro, pero es necesario para evitar crear stock.moves incorrectos
	@api.multi
	def verify_constrains_for_process(self,date):
		
		currency_obj = self.env['res.currency'].search([('name','=','USD')])
		if len(currency_obj)>0:
			currency_obj = currency_obj[0]
		else:
			raise UserError( 'Error!\nNo existe la moneda USD \nEs necesario crear la moneda USD para un correcto proceso.' )

		tipo_cambio = self.env['res.currency.rate'].search([('name','=',str(date)),('currency_id','=',currency_obj.id)])

		if len(tipo_cambio)>0:
			tipo_cambio = tipo_cambio[0]
		else:
			raise UserError( u'Error!\nNo existe el tipo de cambio para la fecha: '+ str(date) + u'\n Debe actualizar sus tipos de cambio para realizar esta operación')

		bad_lines = self.line_ids.mapped('lot_line_id').mapped('lot_id').filtered(lambda x: not x.requisition_id)
		if len(bad_lines) > 0:
			msg = ''
			for item in bad_lines:
				msg += '-> Lote: ' + item.name +'.\n'
			raise UserError(u'Los siguientes Lotes no tienen order de Requisicion:\n'+msg+'Recuerde: Los lotes de los cristales a ingresar deben tener Orden de requisicion')


class GlassInOrder(models.TransientModel):
	_name = "glass.in.order"

	selected = fields.Boolean('Seleccionada')
	order_id = fields.Many2one('glass.order','Orden')
	partner_id = fields.Many2one('res.partner','Cliente')
	date_production = fields.Date(u'Fecha de Producción')
	total_pzs = fields.Float("Cantidad")
	total_area = fields.Float(u'M2')
	
	mainid=fields.Many2one('glass.in.production.wizard','mainid')
