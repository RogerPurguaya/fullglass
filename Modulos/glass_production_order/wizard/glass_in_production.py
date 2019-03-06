# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime
import itertools

class GlassInProductionWizard(models.TransientModel):
	_name='glass.in.production.wizard'

	stock_type_id = fields.Many2one('stock.picking.type',u'Operación de almacén') 
	date_in = fields.Date('Fecha ingreso',default=datetime.now())
	order_ids = fields.One2many('glass.in.order','mainid','order_id')
	line_ids = fields.Many2many('glass.order.line','glass_in_lineorder_rel','in_id','line_id',string="lienas")
	order_id = fields.Many2one('glass.order','Filtrar OP')


	# @api.multi
	# def _get_default_stock_type(self):
	# 	config = self.env.['']

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


	@api.onchange('order_ids')
	def getlines(self):
		alines = []
		for order in self.order_ids:
			if order.selected:
				for line in order.order_id.line_ids:
					if line.state =='ended':
						alines.append(line.id)
					#New code
					# if line.state !='ended':
					# 	alines.append(line.id)

		if len(alines)>0:
			self.line_ids=[(6,0,alines)]

	@api.model
	def default_get(self,fields):
		res = super(GlassInProductionWizard,self).default_get(fields)
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]
		res.update({'stock_type_id':config_data.picking_type_pt.id})

		## old code
		# orders=self.env['glass.order'].search([('state','=','process')])
		# aorder=[]
		# for order in orders:
		# 	vals={
		# 	'selected':False,
		# 	'order_id':order.id,
		# 	'partner_id':order.partner_id.id,
		# 	'date_production':order.date_production,
		# 	'total_pzs':order.total_pzs,
		# 	'total_area':order.total_area,
		# 	}
		# 	aorder.append((0,0,vals))
		# res.update({'order_ids':aorder})
		return res

	@api.one
	def _prepare_picking(self,pt,motive):
		useract = self.env.user
		data= {
			'picking_type_id': pt.id,
			'partner_id': None,
			'date': datetime.now(),
			'origin': '',
			'location_dest_id': pt.default_location_dest_id.id,
			'location_id': pt.default_location_src_id.id,
			'company_id': useract.company_id.id,
			'einvoice12': motive.id,
		}

		return data


#New Code
# Se puede mejorar los algoritmos y rutinas para un mejor performance, se hizo asi por moticos de prisa, queda pendiente para el siguiente programador  mejorar el código:)
# Mejorar el algoritmo de "_processing_stock_move_lines" ya que realiza iteraciones de más
# y se puede mejorar.

	@api.multi
	def makeingreso(self):
		self.ensure_one()
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuración de producción')		
		config_data = self.env['glass.order.config'].search([])[0]

		#print('Config: ', config_data.traslate_motive_pt)

		d = self._prepare_picking(self.stock_type_id,config_data.traslate_motive_pt)
		useract = self.env.user
		picking_ids=[]
		for l1 in self.order_ids:

			# en vista q no se guardan los ids filtrados anteriormente, lo haremos de nuevo :(
			line_ids_tmp = []
			for item in l1.order_id.line_ids:
				if item.state == 'ended':
					line_ids_tmp.append(item)

			if l1.selected and len(line_ids_tmp) > 0:
				
				#Es necesario verificar el tipo de cambio y la moneda 
				#para crear correctamente el picking y evitar crear stock moves erroneos 
				#fecha_kardex = datetime.now().date()
				self.verify_constrains_for_process(self.date_in)

				data= {
					'picking_type_id': self.stock_type_id.id,
					'partner_id': None,
					'date': datetime.now(),
					'fecha_kardex': str(self.date_in),
					'origin': l1.order_id.name,
					'location_dest_id': self.stock_type_id.default_location_dest_id.id,
					'location_id': self.stock_type_id.default_location_src_id.id,
					'company_id': useract.company_id.id,
					'einvoice_12': config_data.traslate_motive_pt.id,
				}
				
				picking = self.env['stock.picking'].create(data)
				picking_ids.append(picking.id)

				moves_list = self._processing_stock_move_lines(line_ids_tmp,picking,useract,l1)
				# Hacemos el siguiente proceso para que el albaran pase a realizado una 
				# vez se genere:
				context = None
				action = picking.do_new_transfer()
				if type(action) == type({}):
					if action['res_model'] == 'stock.immediate.transfer' or action['res_model'] == 'stock.backorder.confirmation':
						context = action['context']
						sit = self.env['stock.immediate.transfer'].with_context(context).create({'pick_id': picking.id})	
						sit.process()
				
				for line in line_ids_tmp:
					line.state = 'instock'
					line.lot_line_id.ingresado = True
					vals = {
						'user_id':self.env.uid,
						'date':datetime.now(),
						'time':datetime.now().time(),
						'stage':'ingresado',
						'lot_line_id':line.lot_line_id.id,
					}
					self.env['glass.stage.record'].create(vals)

				if self._verify_complete_ending_order_lines(l1.order_id.line_ids):
					l1.order_id.state='ended'
		
		data={}
		view = self.env.ref('stock.view_picking_form')
		data = {
				'name':u'Picking',
				'view_type':'form',
				'view_mode':'tree,form',
				'res_model':'stock.picking',
				'type':'ir.actions.act_window',
				'domain':[('id','in',picking_ids)]
		}
		return data

# campo = glass_order_line_ids
#Verifica si el producto de cada linea es el mismo, en ese caso suma las areas para generar un solo albarán acumulativo

	@api.multi
	def _processing_stock_move_lines(self,lines,picking,useract,l1):
		acum_area = 0
		tmp_line = None
		list_lines = [] #acumulador de lista por move
		move_list = []
		move = None

		sorted_lines = sorted(lines, key = lambda line:line.product_id[0].id)
		products_ids = map(lambda x: x.product_id[0].id , sorted_lines) 		
		products_ids = set(products_ids)

		for id in products_ids:
			for line in sorted_lines:				
				if line.product_id[0].id == id:
					tmp_line = line
					list_lines.append(tmp_line.id)
					acum_area += line.area
			
			#tmp_line.sum_area = acum_area
			vals = {
				'name': tmp_line.product_id.name or '',
				'product_id': tmp_line.product_id.id,
				'product_uom': tmp_line.product_id.uom_id.id,
				'date': datetime.now(),
				'date_expected': datetime.now(),
				'location_id': self.stock_type_id.default_location_src_id.id,
				'location_dest_id': self.stock_type_id.default_location_dest_id.id,
				'picking_id': picking.id,
				'partner_id': tmp_line.order_id.partner_id.id,
				'move_dest_id': False,
				'state': 'draft',
				'company_id': useract.company_id.id,
				'picking_type_id': self.stock_type_id.id,
				'procurement_id': False,
				'origin': l1.order_id.name,
				'route_ids': self.stock_type_id.warehouse_id and [(6, 0, [x.id for x in self.stock_type_id.warehouse_id.route_ids])] or [],
				'warehouse_id': self.stock_type_id.warehouse_id.id,
				'product_uom_qty': acum_area,
				'glass_order_line_ids': [(6,0,list_lines)]
			}
			move = self.env['stock.move'].create(vals)
			move_list.append(move)
			acum_area = 0
			list_lines = []
		
		return move_list

#VErifica si el total de las ineas de la orden de producción han sido entregadas
# y de acuerdo a eso setar el estado de la orden de producción a finalizado
	@api.multi
	def _verify_complete_ending_order_lines(self,array):
		aux = True
		for item in array:
			if item.state != 'instock':
				aux = False
				break
		return aux

#Método que verifica los tipos de cambio y moneda para la fecha de kardex, se realiza en 
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


class GlassInOrder(models.TransientModel):
	_name = "glass.in.order"

	selected = fields.Boolean('Seleccionada')
	order_id = fields.Many2one('glass.order','Orden')
	partner_id = fields.Many2one('res.partner','Cliente')
	date_production = fields.Date(u'Fecha de Producción')
	total_pzs = fields.Float("Cantidad")
	total_area = fields.Float(u'M2')
	
	mainid=fields.Many2one('glass.in.production.wizard','mainid')
