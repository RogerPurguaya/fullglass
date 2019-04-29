# -*- coding: utf-8 -*-

from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassRequisition(models.Model):
	_name = 'glass.requisition'
	_order_by='id desc'

	name = fields.Char('Orden de Requisicion',default="/")
	table_number=fields.Char('Nro. de Mesa')
	date_order = fields.Date('Fecha Almacen',default=datetime.now().date())
	required_area = fields.Float('M2 Requeridos',compute="totals",digits=(20,4))
	required_mp   = fields.Float('M2 Materia Prima',compute="totals",digits=(20,4))
	merma = fields.Float('Merma',compute="totals",digits=(20,4))
	state = fields.Selection([('draft','Borrador'),('confirm','Confirmada'),('process','Procesada'),('cancel','Cancelada')],'Estado',default='draft')
	picking_ids = fields.Many2many('stock.picking','glass_requisition_picking_rel','requisition_id','picking_id',u'Operaciones de Almacen',compute='_get_picking_ids')

	picking_mp_ids = fields.Many2many('stock.picking','glass_requisition_picking_mp_rel','requisition_id','picking_id',u'Operaciones de Almacen')
	picking_rt_ids = fields.Many2many('stock.picking','glass_requisition_picking_rt_rel','requisition_id','picking_id',u'Operaciones de Almacen')
	picking_drt_ids = fields.Many2many('stock.picking','glass_requisition_picking_drt_rel','requisition_id','picking_id',u'Operaciones de Almacen')
	#picking_pt_ids = fields.Many2many('stock.picking','glass_requisition_picking_pt_rel','requisition_id','picking_id',u'Operaciones de Almacen') ??
	total_picking_mp  = fields.Float('Total M2',compute="totals",digits=(20,4))
	total_picking_rt  = fields.Float('Total M2',compute="totals",digits=(20,4))
	total_picking_drt = fields.Float('Total M2',compute="totals",digits=(20,4))
	production_order_ids = fields.Many2many('glass.order','glass_requisition_production_rel','requisition_id','order_id',u'ordenes de Produccion',compute="getprdorders")

	lot_ids    = fields.One2many('glass.requisition.line.lot','requisition_id','Lotes')
	product_id = fields.Many2one('product.product','Producto General')
	lot_id     = fields.Many2one('glass.lot','Lote')	

	picking_count = fields.Integer(compute='_compute_glass_picking', string='Receptions', default=0)

	raw_materials = fields.One2many('requisition.worker.material','requisition_id',string='Materias Primas')
	scraps = fields.One2many('requisition.worker.scraps','requisition_id',string='Retazos')
	return_scraps = fields.One2many('requisition.worker.scraps.return','requisition_id',string='Devolucion de Retazos')

	_sql_constraints = [('table_number_uniq', 'unique(table_number)', u'El numero de mesa debe de ser unico'),]

	@api.depends('picking_mp_ids','picking_rt_ids','picking_drt_ids')
	def _get_picking_ids(self):
		for rec in self:
			pickings      = rec.mapped('picking_mp_ids')
			pickings_rt   = rec.mapped('picking_rt_ids')
			pickings_drt  = rec.mapped('picking_drt_ids')
			rec.picking_ids = pickings + pickings_rt + pickings_drt
	
	@api.depends('picking_ids')
	def _compute_glass_picking(self):
		for rec in self:
			rec.picking_count = len(rec.picking_ids)

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

	# boton de pickings
	@api.multi
	def action_view_delivery_glass(self):
		action = self.env.ref('stock.action_picking_tree').read()[0]
		if len(self.picking_ids) > 1:
			action['domain'] = "[('id','in',["+','.join(map(str,self.picking_ids.ids)) + "])]"
			action['context'] = {'search_default_picking_type_id': '',}
		elif len(self.picking_ids) == 1:
			action['views'] = [(self.env.ref('stock.view_picking_form').id, 'form')]
			action['res_id'] = self.picking_ids[0].id
		return action

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
	def confirm(self):
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		if config_data.seq_requisi == False or len(config_data.seq_requisi) == 0:
			raise exceptions.Warning('No ha configurado la secuencia de Requisiciones')
		
		products = self.lot_ids.mapped('lot_id').mapped('product_id')
		if len(products) == 0:
			raise exceptions.Warning('No ha agregado Lotes en la Orden de Requisicion.')
		if len(products) > 1:
			raise exceptions.Warning('El producto de los Lotes agregados debe ser unico')
		self.write({
			'name':config_data.seq_requisi.next_by_id(),
			'state':'confirm',
			'product_id':products[0].id,
		})

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

		if 'table_number' in vals:
			vals['table_number']=self.get_table_name(vals['table_number'])		
		return super(GlassRequisition,self).write(vals)

	@api.multi
	def get_table_name(self,table):
		if not table.isnumeric():
			raise UserError('El valor ingresado "'+table+'" no es valido,\nIngrese un numero entero.')
		if len(str(table)) > 6:
			raise UserError('El valor ingresado "'+table+'" excede el limite permitido (6 cifras).')
		return 'M' + table.rjust(6,'0')

	@api.one
	def cancel(self):
		for line in self.picking_ids:
			line.action_cancel()
		for lot in self.lot_ids.mapped('lot_id'):
			lot.requisition_id = False
			for line in lot.line_ids.filtered(lambda x:x.requisicion and not x.is_break):
				line.write({'requisicion':False})
				stages = line.stages_ids.filtered(lambda x: x.stage == 'requisicion')
				for i in stages:
					i.unlink()
		self.state='cancel'
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
		n,m,j,tpmp,tprt,tpdrt=0,0,0,0,0,0
		for l in self.lot_ids:
			n=n+l.lot_id.total_area

		for l in self.picking_mp_ids:
			for d in l.move_lines:
				m=m+(d.product_uom_qty*d.product_uom.factor_inv)
				tpmp=tpmp+(d.product_uom_qty*d.product_uom.factor_inv)
		for l in self.picking_rt_ids:
			for d in l.move_lines:
				m=m+(d.product_uom_qty*d.product_uom.factor_inv)
				tprt=tprt+(d.product_uom_qty*d.product_uom.factor_inv)

		for l in self.picking_drt_ids:
			for d in l.move_lines:
				j=j+(d.product_uom_qty*d.product_uom.factor_inv)				
				tpdrt=tpdrt+(d.product_uom_qty*d.product_uom.factor_inv)

		self.write({
			'required_area':n,
			'required_mp':m-j,
			'merma':(m-j)-n,
			'total_picking_mp':tpmp,
			'total_picking_rt':tprt,
			'total_picking_drt':tpdrt,
		})

	@api.one
	def get_picking(self,type_pick,motive):
		picking = self.env['stock.picking'].create({
				'picking_type_id': type_pick.id,
				'partner_id': None,
				'date': datetime.now().date(),
				'fecha_kardex':datetime.now().date(),
				'origin': self.name,
				'location_dest_id': type_pick.default_location_dest_id.id,
				'location_id': type_pick.default_location_src_id.id,
				'company_id': self.env.user.company_id.id,
				'einvoice_12': motive.id,
				})
		return picking

	@api.one
	def process(self):
		used_lots = self.lot_ids.mapped('lot_id').filtered(lambda x: x.requisition_id)
		if len(used_lots) > 0:
			msg = ''
			for item in used_lots:
				msg += '-> Lote: ' + item.name + ' con Requisicion: '+ item.requisition_id.name+'.\n'
			raise exceptions.Warning('Los siguientes lotes ya tienen orden de requisicion:\n'+msg)
		
		if len(self.raw_materials) == 0 and len(self.scraps) == 0:
			raise exceptions.Warning('Error:\nLa Orden de requisicion debe tener por lo menos una linea de Materias primas o de Retazos')
		
		conf = self.env['glass.order.config'].search([])[0]
		
		# MATERIAS PRIMAS:
		type_mp = conf.picking_type_mp
		raw_materials_picking = self.get_picking(type_mp,conf.traslate_motive_mp)[0]
		for item in self.raw_materials:
			self.create_move(raw_materials_picking,type_mp,item.product_id,item.quantity)
		self.transfer_picking(raw_materials_picking)
		self.picking_mp_ids |= raw_materials_picking

		# RETAZOS:
		if len(self.scraps) > 0:
			type_rt     = conf.picking_type_rt
			scraps_picking = self.get_picking(type_rt,conf.traslate_motive_rt)[0]
			for item in self.scraps:
				self.create_move(scraps_picking,type_rt,item.product_id,item.quantity)
			self.transfer_picking(scraps_picking)
			self.picking_rt_ids |= scraps_picking

		# DEVOLUCION DE RETAZOS:
		if len(self.return_scraps) > 0:
			type_drt    = conf.picking_type_drt
			scraps_return_picking = self.get_picking(type_drt,conf.traslate_motive_drt)[0]
			for item in self.return_scraps:
				products = self.env['product.product'].search([('name','=',item.product_id.name),('retazo','=',True)])
				product = products.filtered(lambda x: x.uom_id.ancho == item.width and x.uom_id.alto == item.height)
				new_prod = None
				if len(product) == 0:
					new_uom = self.env['product.uom'].create({
						'name':str(item.width)+"x"+str(item.height)+"mm - R",
						'uom_type':'reference',
						'is_retazo':True,
						'ancho':item.width,
						'alto':item.height,
						'category_id':conf.categ_uom_retazo.id,
						'rounding':0.00001,
					})

					attrs = []
					for attr in item.product_id.product_tmpl_id.atributo_ids:
						new = attr.copy()
						new.product_id = False
						attrs.append(new.id)

					new_tmpl = self.env['product.template'].create({
						'codigo_inicial':item.product_id.codigo_inicial.id,
						'categ_id':item.product_id.categ_id.id,
						'name':'',
						'sale_ok':False,
						'purchase_ok':False,
						'type':'product',
						'uom_id': new_uom.id,
						'list_price':False,
						'optima_trim': item.product_id.optima_trim,
						'retazo':True,
						'uom_po_id':new_uom.id,
						'atributo_ids':[(6,0,attrs)]
					})

					new_prod = self.env['product.product'].search([('product_tmpl_id','=',new_tmpl.id)])
				
				product = new_prod[0] if new_prod else product[0]
				self.create_move(scraps_return_picking,type_drt,product,item.quantity)
			self.transfer_picking(scraps_return_picking)
			self.picking_drt_ids |= scraps_return_picking

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
			stage_obj = self.env['glass.stage.record'].create({
				'user_id':self.env.uid,
				'date':datetime.now().date(),
				'time':datetime.now().time(),
				'stage':'requisicion',
				'lot_line_id':line.id,
			})
			line.requisicion=True
		self.state='process'			

	@api.multi
	def transfer_picking(self,picking):
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

	# Metodo para crear los move_lines
	@api.multi
	def create_move(self,picking,pick_type,product,quantity):
		move = self.env['stock.move'].create({
			'name': product.name or '',
			'product_id': product.id,
			'product_uom': product.uom_id.id,
			'date': datetime.now().date(),
			'date_expected': datetime.now().date(),
			'location_dest_id':picking.location_dest_id.id,
			'location_id': picking.location_id.id,
			'picking_id': picking.id,
			'move_dest_id': False,
			'state': 'draft',
			'company_id': self.env.user.company_id.id,
			'picking_type_id': pick_type.id,
			'procurement_id': False,
			'origin': self.name,
			'route_ids': pick_type.warehouse_id and [(6, 0, [x.id for x in pick_type.warehouse_id.route_ids])] or [],
			'warehouse_id': pick_type.warehouse_id.id,
			'product_uom_qty': quantity,
		})

	@api.multi
	def add_material(self):
		# materiales permitidos		
		allowed = self.get_allowed_materials(self.product_id,'raw_materials')
		lines = []
		for item in allowed:
			line = self.env['requisition.worker.wizard.line'].create({
				'product_id':item.id,
			})
			lines.append(line.id)

		wizard = self.env['requisition.worker.material.wizard'].create({
			'requisition_id':self.id,
			'lines_ids':[(6,0,lines)]
		})
		return {
			'res_id':wizard.id,
			'name':'Agregar Material',
			'type': 'ir.actions.act_window',
			'res_model': 'requisition.worker.material.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	@api.multi
	def add_scraps(self):
		# buscar si los materiales permitidos tienen un equivalente en retazo	
		names = self.get_allowed_materials(self.product_id,'raw_materials').mapped('name')
		products = self.env['product.product'].search([('name','in',names),('retazo','=',True)])

		if len(products) == 0:
			raise UserError('No se han encontrado Productos de retazo para las Materias Primas Disponibles')
		lines = []
		for item in products:
			line = self.env['requisition.worker.wizard.line'].create({
				'product_id':item.id,
				'width':item.uom_id.ancho,
				'height':item.uom_id.alto,
			})
			lines.append(line.id)

		wizard = self.env['requisition.worker.scraps.wizard'].create({
			'requisition_id':self.id,
			'lines_ids':[(6,0,lines)]
		})
		return {
			'res_id':wizard.id,
			'name':'Agregar Retazos',
			'type': 'ir.actions.act_window',
			'res_model': 'requisition.worker.scraps.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

	# devolucion de retazos
	@api.multi
	def add_return_scraps(self):		
		lines = []
		products = self.raw_materials.mapped('product_id') # mat primas
		if len(products) == 0:
			raise UserError('No ha solicitado materias primas de las cuales devolver retazos')
		for item in products:
			line = self.env['requisition.worker.wizard.line'].create({
				'product_id':item.id
			})
			lines.append(line.id)

		wizard = self.env['requisition.worker.scraps.return.wizard'].create({
			'requisition_id':self.id,
			'lines_ids':[(6,0,lines)]
		})
		return {
			'res_id':wizard.id,
			'name':'Devolver Retazos',
			'type': 'ir.actions.act_window',
			'res_model': 'requisition.worker.scraps.return.wizard',
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}

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
		self.m2 = self.lot_id.total_area
		self.date=self.lot_id.date
		self.user_id=self.lot_id.create_uid.id
		self.crystal_count=len(self.lot_id.line_ids)