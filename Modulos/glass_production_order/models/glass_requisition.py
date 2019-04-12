# -*- coding: utf-8 -*-

from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassRequisition(models.Model):
	_name = 'glass.requisition'
	_order_by='id desc'

	name = fields.Char('Orden de Requisicion',default="/")
	table_number=fields.Char('Nro. de Mesa')
	date_order = fields.Date('Fecha Almacen',default=fields.Date.today)
	required_area = fields.Float('M2 Requeridos',compute="totals",digits=(20,4))
	required_mp = fields.Float('M2 Materia Prima',compute="totals",digits=(20,4))
	merma = fields.Float('Merma',compute="totals",digits=(20,4))
	state=fields.Selection([('draft','Borrador'),('confirm','Confirmada'),('process','Procesada'),('cancel','Cancelada')],'Estado',default='draft')
	picking_ids = fields.Many2many('stock.picking','glass_requisition_picking_rel','requisition_id','picking_id',u'Operaciones de Almacen')

	picking_mp_ids = fields.Many2many('stock.picking','glass_requisition_picking_mp_rel','requisition_id','picking_id',u'Operaciones de Almacen')
	picking_rt_ids = fields.Many2many('stock.picking','glass_requisition_picking_rt_rel','requisition_id','picking_id',u'Operaciones de Almacen')
	picking_drt_ids = fields.Many2many('stock.picking','glass_requisition_picking_drt_rel','requisition_id','picking_id',u'Operaciones de Almacen')
	picking_pt_ids = fields.Many2many('stock.picking','glass_requisition_picking_pt_rel','requisition_id','picking_id',u'Operaciones de Almacen')

	total_picking_mp = fields.Float('Total M2',compute="totals",digits=(20,4))
	total_picking_rt = fields.Float('Total M2',compute="totals",digits=(20,4))
	total_picking_drt = fields.Float('Total M2',compute="totals",digits=(20,4))


	production_order_ids = fields.Many2many('glass.order','glass_requisition_production_rel','requisition_id','order_id',u'ordenes de Produccion',compute="getprdorders")

	lot_ids = fields.One2many('glass.requisition.line.lot','requisition_id','Lotes')


	picking_type_mp = fields.Integer(u'Operacion consumo materia prima ')
	picking_type_rt = fields.Integer(u'Operacion consumo retazos')
	picking_type_drt = fields.Integer(u'Operacion devolucion retazos')
	picking_type_pr = fields.Integer(u'Operacion produccion')
	traslate_motive_mp = fields.Integer('Motivo traslado consumo materia prima ')
	traslate_motive_rt = fields.Integer('Motivo traslado consumo retazos')
	traslate_motive_drt = fields.Integer(u'Motivo traslado devolucion retazos')
	traslate_motive_pr = fields.Integer(u'Motivo traslado  produccion')

	product_id=fields.Many2one('product.product','Producto General')
	lot_id=fields.Many2one('glass.lot','Lote')	

	picking_count = fields.Integer(compute='_compute_glass_picking', string='Receptions', default=0)

	_sql_constraints = [
		('table_number_uniq', 'unique(table_number)', u'El numero de mesa debe de ser unico'),
	]

	@api.depends('picking_mp_ids','picking_rt_ids','picking_drt_ids')
	def _compute_glass_picking(self):
		pickings = self.mapped('picking_mp_ids')
		pickings_rt = self.mapped('picking_rt_ids')
		pickings_drt = self.mapped('picking_drt_ids')
		pickings = pickings + pickings_rt + pickings_drt
		self.picking_count = len(pickings)

	@api.multi
	@api.depends('table_number','name')
	def name_get(self):
		result = []
		for req in self:
			name = req.table_number + ' - ' + req.name
			result.append((req.id, name))
		return result

	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		domain = []
		if name:
			domain = ['|',('table_number', operator, name), ('name',operator,name)]
		requisitions = self.search(domain + args, limit=limit)
		return requisitions.name_get()

	@api.multi
	def call_units(self):
		view = self.env.ref('glass_production_order.view_glass_make_uom_form')
		data = {
			'name': _('Agregar unidad'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.make.uom',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 
		return data

	@api.multi
	def action_view_delivery_glass(self):
		
		action = self.env.ref('stock.action_picking_tree').read()[0]
		pickings = self.mapped('picking_mp_ids')
		pickings_rt = self.mapped('picking_rt_ids')
		pickings_drt = self.mapped('picking_drt_ids')
		pickings = pickings + pickings_rt + pickings_drt
		
		if len(pickings) > 1:
			action['domain'] = "[('id', 'in',[" + ','.join(map(str, pickings.ids)) + "])]"
			action['context'] = {
					'search_default_picking_type_id': '',
			}
		elif pickings:
			action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
			action['res_id'] = pickings.id
		return action

	@api.multi
	def create_glass_picking(self):

		#allowed_materials = self.get_allowed_materials(self.product_id,'raw_materials')
		#print('los permitidos: ', allowed_materials)
		# Pendiente de desarrollo:
		return {
			'type':'ir.actions.act_window',
			'res_model': 'stock.picking',
			'view_mode':'form',
			'view_type':'form',
			'views': [(self.env.ref('stock.view_picking_form').id, 'form')],
			'context':{
				'origin':self.name,
				'default_fecha_kardex':self.date_order,
				'default_picking_type_id':self.picking_type_mp,
				'default_einvoice_12':self.traslate_motive_mp,
				'default_origin':self.name,
				'default_identifier':'mp',
				'identificador_glass':self.id,
				'default_identificador_glass':self.id,
				#'default_move_lines': los lines
				},
		}

	@api.multi
	def create_glass_picking_rt(self):
		return {
			'type':'ir.actions.act_window',
			'res_model': 'stock.picking',
			'view_mode':'form',
			'view_type':'form',
			'views': [(self.env.ref('stock.view_picking_form').id, 'form')],
			'context':{
				'origin':self.name,
				'default_fecha_kardex':self.date_order,
				'default_picking_type_id':self.picking_type_rt,
				'default_einvoice_12':self.traslate_motive_rt,
				'default_origin':self.name,
				'default_identifier':'rt',
				'identificador_glass':self.id,
				'default_identificador_glass':self.id
				}
		}

	@api.multi
	def create_glass_picking_drt(self):
		return {
			'type':'ir.actions.act_window',
			'res_model': 'stock.picking',
			'view_mode':'form',
			'view_type':'form',
			'views': [(self.env.ref('stock.view_picking_form').id, 'form')],
			'context':{
				'origin':self.name,
				'default_fecha_kardex':self.date_order,
				'default_picking_type_id':self.picking_type_drt,
				'default_einvoice_12':self.traslate_motive_drt,
				'default_origin':self.name,
				'default_identifier':'drt',
				'identificador_glass':self.id,
				'default_identificador_glass':self.id
				}
		}

	@api.multi
	def get_allowed_materials(self,product_id,type):
		config = self.env['glass.order.config'].search([])
		if len(config) == 0:
			raise exceptions.Warning('No ha encontrado la configuracion de produccion.')
		allowed = config[0].requisition_materials_ids.filtered(lambda x: x.product_id.id == product_id.id and x.type_operation == type)
		if len(allowed) == 0:
			raise exceptions.Warning('No se ha encontrado la lista de materiales para: '+self.product_id.name + ' en este tipo de requisicion.\nConfigure su lista de materiales en: Produccion->Parametros->Orden de Requisicion->Materiales de Requisicion.')
		elif len(allowed.materials_ids) == 0:
			raise exceptions.Warning('La lista de materiales permitidos para '+self.product_id.name + ' en este tipo de operacion esta vacia')
		else:
			return allowed.materials_ids

	@api.one
	def reopen(self):
		self.update({'state':'draft'})

	@api.one
	def confirm(self):
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		if config_data.seq_requisi == False or len(config_data.seq_requisi) == 0:
			raise exceptions.Warning('No ha configurado la secuencia de Requisiciones')
		if self.name=='/':
			newname = config_data.seq_requisi.next_by_id()
			self.update({'name':newname})
		self.update({'state':'confirm'})


	@api.model
	def default_get(self,fields):
		res = super(GlassRequisition,self).default_get(fields)
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		# newname = config_data.seq_requisi.next_by_id()
		res.update({'picking_type_mp':config_data.picking_type_mp.id})
		res.update({'picking_type_rt':config_data.picking_type_rt.id})
		res.update({'picking_type_drt':config_data.picking_type_drt.id})
		res.update({'picking_type_pr':config_data.picking_type_pr.id})
		res.update({'traslate_motive_mp':config_data.traslate_motive_mp.id})
		res.update({'traslate_motive_rt':config_data.traslate_motive_rt.id})
		res.update({'traslate_motive_drt':config_data.traslate_motive_drt.id})
		res.update({'traslate_motive_pr':config_data.traslate_motive_pr.id})
		# res.update({'name':newname})
		return res


	@api.multi
	def add_mp_picking(self):

		# search_view_ref = self.env.ref('account.view_account_invoice_filter', False)
		# form_view_ref = self.env.ref('stock.view_glass_pool_wizard_form', False)
		# tree_view_ref = self.env.ref('account.invoice_tree', False)
		# module = __name__.split('addons.')[1].split('.')[0]

		vals_default={
			'default_state':'draft',
		}
		view = self.env.ref('stock.view_picking_form')
		data = {
			'name': _('Agregar Materia Prima'),
			'context': self._context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'stock.picking',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
			'context':vals_default,
		} 
		return data


	@api.model
	def create(self,vals):
		
		if 'table_number' in vals:
			vals['table_number']=self.get_table_name(vals['table_number'])
		if 'lot_ids' in vals:
			for lote in vals['lot_ids']:
				lote_act = self.env['glass.lot'].browse(lote[2]['lot_id'])
				lote[2]['m2']=lote_act.total_area
				lote[2]['user_id']=lote_act.create_uid.id
				lote[2]['crystal_count']=len(lote_act.line_ids)
		return super(GlassRequisition,self).create(vals)


	# Tener cuidado con esta vaina xq costo mucho hacer que funcione y aun asi
	# podria tener fallos:
	@api.one
	def write(self,vals):
		if 'lot_ids' in vals:
			for lote in vals['lot_ids']:
				if lote[2]:
					if 'lot_id' in lote[2]:
						lote_act = self.env['glass.lot'].browse(lote[2]['lot_id'])
						lote[2]['m2']=lote_act.total_area
						lote[2]['user_id']=lote_act.create_uid.id
						lote[2]['crystal_count']=len(lote_act.line_ids)
						# for line in lote_act.line_ids:
						# 	data = {
						# 		'user_id':self.env.uid,
						# 		'date':datetime.now(),
						# 		'time':datetime.now().time(),
						# 		'stage':'requisicion',
						# 		'lot_line_id':line.id,
						# 	}
						# 	stage_obj = self.env['glass.stage.record']
						# 	stage_obj.create(data)
						# 	line.requisicion=True

		if 'table_number' in vals:
			vals['table_number']=self.get_table_name(vals['table_number'])		
		t = super(GlassRequisition,self).write(vals)
		if 'product_id' in vals:
			return t
		# Verificamos los datos enviados relacionados a los productos:
		self.refresh()
		product = self._verify_data(self.lot_ids,self.picking_mp_ids,self.picking_rt_ids,self.picking_drt_ids)
		if product:
			self.product_id = product.id # Si todo sale bien seteamos el producto
		return t
		#return super(GlassRequisition,self).write(vals)

	# Verifica si todos los productos de los lotes de las glass.requisition.line.lot
	# son iguales y tbn verifica que el atributo (de a configuracion) coincida para 
	# los productos de los lotes de las glass.requisition.line.lot y los prods de los 
	# albaranes de materias primas etc.
	@api.multi
	def _verify_data(self,lot_lines,mp_lines,rt_lines,drt_ids):
		if len(lot_lines) == 0:
			return False
		try:
			config_attr = self.env['glass.order.config'].search([])[0].compare_attribute
		except IndexError as e:
			print('Error: ', e)
			raise UserError(u'No se ha encontrado los valores de configuracion para el Atributo de comparacion.')
		product = list(set(map(lambda x: x.lot_id.product_id , lot_lines))) # prod de los lot lines
		if len(product) > 1:
			raise UserError('Las lineas de lotes deben tener todas el mismo producto.')

		attribute = self.env['product.selecionable'].search([('atributo_id','=',config_attr.id),('product_id','=',product[0].product_tmpl_id.id)])

		if len(attribute) == 0:
			raise UserError('El atributo configurado: "'+str(config_attr.name)+'" no se ha encontrado en el producto de los lotes')
		attribute_value = attribute[0].valor_id.name
		if len(mp_lines) > 0:
			for picking in mp_lines:
				for move in picking.move_lines:
					attr = self.env['product.selecionable'].search([('atributo_id','=',config_attr.id),('product_id','=',move.product_id.product_tmpl_id.id)])
					if len(attr) == 0:
						raise UserError('El atributo configurado: "'+config_attr.name+'"  \n no se ha encontrado en el producto '+ move.product_id.name + ' de la orden de materias primas.')
					if attr[0].valor_id.name != attribute_value:
						raise UserError('El valor del atributo "'+config_attr.name+'"-'+str(attribute_value)+'\n no coincide con el del producto '+ move.product_id.name + ' de la orden de materias primas.')
		if len(rt_lines) > 0:
			for picking in rt_lines:
				for move in picking.move_lines:
					attr = self.env['product.selecionable'].search([('atributo_id','=',config_attr.id),('product_id','=',move.product_id.product_tmpl_id.id)])
					if len(attr) == 0:
						raise UserError('El atributo configurado: "'+config_attr.name+'"  \n no se ha encontrado en el producto '+ move.product_id.name + ' de la orden de Retazos.')
					if attr[0].valor_id.name != attribute_value:
						raise UserError('El valor del atributo "'+config_attr.name+'"-'+str(attribute_value)+'\n no coincide con el del producto '+ move.product_id.name + ' de la orden de Retazos.')
		if len(drt_ids) > 0:
			for picking in drt_ids:
				for move in picking.move_lines:
					attr = self.env['product.selecionable'].search([('atributo_id','=',config_attr.id),('product_id','=',move.product_id.product_tmpl_id.id)])
					if len(attr) == 0:
						raise UserError('El atributo configurado: "'+config_attr.name+'"  \n no se ha encontrado en el producto '+ move.product_id.name + ' de la orden de Devolucion-Retazos.')
					if attr[0].valor_id.name != attribute_value:
						raise UserError('El valor del atributo "'+config_attr.name+'"-'+str(attribute_value)+'\n no coincide con el del producto '+ move.product_id.name + ' de la orden de Devoluciones-Retazos.')
		return product[0]

	@api.multi
	def get_table_name(self,table):
		if not table.isnumeric():
			raise UserError('El valor ingresado "'+table+'" no es valido,\nIngrese un numero entero.')
		if len(str(table)) > 6:
			raise UserError('El valor ingresado "'+table+'" excede el limite permitido (6 cifras).')
		return 'M' + table.rjust(6,'0')


	@api.one
	def cancel(self):
		self.state='cancel'
		for line in self.picking_ids:
			line.action_cancel()
		for lot in self.lot_ids.mapped('lot_id'):
			lot.requisition_id = False
			for line in lot.line_ids.filtered(lambda x:x.requisicion and not x.is_break):
				line.write({'requisicion':False})
				stages = line.stages_ids.filtered(lambda x: x.stage == 'requisicion')
				for i in stages:
					i.unlink()
		return True 

	@api.onchange('lot_ids')
	def onchagelots(self):
		ops = []
		for line in self.lot_ids:
			for linelot in line.lot_id.line_ids:
				if linelot.order_prod_id.id not in ops:
					ops.append(linelot.order_prod_id.id)
		self.production_order_ids=ops


	@api.one
	def unlink(self):
		if self.state!='draft':
			raise UserError(u'No se puede borrar una Requisicion que ha fue Procesada')		
		return super(GlassRequisition,self).unlink()

	@api.one
	def getprdorders(self):
		ops = []
		for line in self.lot_ids:
			for linelot in line.lot_id.line_ids:
				if linelot.order_prod_id.id not in ops:
					ops.append(linelot.order_prod_id.id)
		self.production_order_ids=ops



	@api.one
	def totals(self):
		n=0
		tpmp=0
		tprt=0
		tpdrt=0
		for l in self.lot_ids:
			n=n+l.lot_id.total_area

		m=0
		for l in self.picking_mp_ids:
			for d in l.move_lines:
				m=m+(d.product_uom_qty*d.product_uom.factor_inv)
				tpmp=tpmp+(d.product_uom_qty*d.product_uom.factor_inv)
		for l in self.picking_rt_ids:
			for d in l.move_lines:
				m=m+(d.product_uom_qty*d.product_uom.factor_inv)
				tprt=tprt+(d.product_uom_qty*d.product_uom.factor_inv)
				#print tprt,d.product_uom_qty
		j=0
		for l in self.picking_drt_ids:
			for d in l.move_lines:
				j=j+(d.product_uom_qty*d.product_uom.factor_inv)				
				tpdrt=tpdrt+(d.product_uom_qty*d.product_uom.factor_inv)

		self.required_area=n
		self.required_mp=m-j
		self.merma=(m-j)-n

		self.total_picking_mp=tpmp
		self.total_picking_rt=tprt
		self.total_picking_drt=tpdrt


	@api.model
	def _prepare_picking(self,pt,motive):
		useract = self.env.user
		return {
			'picking_type_id': pt.id,
			'partner_id': None,
			'date': datetime.now(),
			'origin': self.name,
			'location_dest_id': pt.default_location_dest_id.id,
			'location_id': pt.default_location_src_id.id,
			'company_id': useract.company_id.id,
			'einvoice12': motive.id,
		}

	@api.one
	def process(self):
		if len(self.lot_ids) == 0:
			raise exceptions.Warning('No ha agregado ningun Lote de produccion')
		used_lots = self.lot_ids.mapped('lot_id').filtered(lambda x: x.requisition_id)
		if len(used_lots) > 0:
			msg = ''
			for item in used_lots:
				msg += '-> Lote: ' + item.name + ' con Requisicion: '+ item.requisition_id.name+'.\n'
			raise exceptions.Warning('Los siguientes lotes ya tienen orden de requisicion:\n'+msg)
		
		if len(self.mapped('picking_mp_ids'))==0 and len(self.mapped('picking_rt_ids'))==0:
			raise exceptions.Warning('Error:\nLa Orden de requisicion debe tener por lo menos un albaran de Materias primas o de Retazos')

		pickings = self.mapped('picking_mp_ids')+self.mapped('picking_rt_ids')+self.mapped('picking_drt_ids')
		self.transfer_pickings(pickings) # procesar los pickings de la requisition
		
		self.state='process'			
		n=0
		for l in self.lot_ids:
			n=n+l.lot_id.total_area
			l.lot_id.write({'requisition_id':l.requisition_id.id}) # record requisition id on lot
		totalsolicitado = n
		merma = self.merma

		for l in self.lot_ids:
			psol = (l.lot_id.total_area*100)/totalsolicitado
			mermaequi = merma*(psol/100)
			for sl in l.lot_id.line_ids:
				g = (sl.area*100)/l.lot_id.total_area
				mermaline = mermaequi*(g/100)
				sl.merma=mermaline


		for line in self.lot_ids.mapped('lot_id').mapped('line_ids').filtered(lambda x: not x.is_break):
			data = {
				'user_id':self.env.uid,
				'date':datetime.now(),
				'time':datetime.now().time(),
				'stage':'requisicion',
				'lot_line_id':line.id,
			}
			stage_obj = self.env['glass.stage.record'].create(data)
			line.requisicion=True

	@api.one
	def transfer_pickings(self,pickings):
		bad_lines = []
		msg = ''
		for picking in pickings:
			if picking.state == 'done':
				continue
			action = picking.do_new_transfer()
			context = None
			if type(action) == type({}):
				if action['res_model'] == 'stock.immediate.transfer' or action['res_model'] == 'stock.backorder.confirmation':
					context = action['context']
					sit = self.env['stock.immediate.transfer'].with_context(context).create({'pick_id': picking.id})	
					try:
						sit.process()
					except UserError as e:
						bad_lines.append(picking.name)
		if len(bad_lines) > 0:
			for i in bad_lines:
				msg += '-> '+ i + '\n'
			raise UserError('No es posible procesar los siguientes Pickings:\n'+msg+'Posible causa: No hay stock disponible para procesarlos.')
		

class GlassRequisitionLineLot(models.Model):
	_name = 'glass.requisition.line.lot'

	lot_id = fields.Many2one('glass.lot','Lote')
	date=fields.Date('Fecha',default=datetime.now())
	user_id=fields.Many2one('res.users','Usuario')
	m2 = fields.Float('M2',digits=(20,4))
	requisition_id = fields.Many2one('glass.requisition','requisition')
	crystal_count=fields.Integer(u'Numero de cristales')


	@api.onchange('lot_id')
	def onchangelot(self):
		### new
		self.m2 = self.lot_id.total_area
		self.date=self.lot_id.date
		self.user_id=self.lot_id.create_uid.id
		self.crystal_count=len(self.lot_id.line_ids)

