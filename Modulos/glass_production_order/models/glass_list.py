# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassListMainWizard(models.Model):
	_name='glass.list.main.wizard'

	_rec_name = 'titulo'

	titulo = fields.Char(default='Seguimiento de Produccion')
	order_id = fields.Many2one('glass.order','Orden')
	lote_id = fields.Many2one('glass.lot','Lote')
	table_number = fields.Char('Mesa')
	date_ini = fields.Date('Fecha Incio')
	date_end = fields.Date('Fecha Fin')
	line_ids = fields.One2many('glass.list.wizard','main_id','Lineas')
	filter_field = fields.Selection([('pending','Pendientes'),('produced','Producidos'),('to inter','Por ingresar'),('to deliver','Por Entregar')],string='Filtro')

	tot_optimizado=fields.Integer('Optimizado')
	tot_corte=fields.Integer('Corte')
	tot_pulido=fields.Integer('Pulido')
	tot_entalle=fields.Integer('Entalle')
	tot_lavado=fields.Integer('Lavado')
	tot_horno=fields.Integer('Horno')
	tot_templado=fields.Integer('Templado')
	tot_insulado=fields.Integer('Insulado')
	tot_comprado=fields.Integer('Comprado')
	tot_ingresado=fields.Integer('Ingresado')
	tot_entregado=fields.Integer('Entregado')
	tot_requisicion=fields.Integer(u'Requisición')

	@api.multi
	def callbreakcrystal(self):
		form_view_ref = self.env.ref('glass_production_order.view_glass_respos_wizard_form', False)
		# tree_view_ref = self.env.ref('account.invoice_tree', False)
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_respos_wizard_form' % module)
		data = {
			'name': _('Registrar Rotura de Cristales'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.respos.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 
		#print data
		return data
	


	@api.multi
	def makelist(self):
		self.ensure_one()
		lin = self.env['glass.list.wizard'].search([])
		for l in lin:
			l.unlink()

		orders1=[]
		domain = []
		lines_without_lot=[] # lineas sin lote de produccion
		if self.filter_field:
			if   self.filter_field == 'pending':
				domain = [('templado','=',False)]
			elif self.filter_field == 'produced':
				domain = [('templado','=',True)]
			elif self.filter_field == 'to inter':
				domain = [('templado','=',True),('ingresado','=',False)]
			elif self.filter_field == 'to deliver':
				domain = [('ingresado','=',True),('entregado','=',False)]

		if self.table_number:
			requisitions = lineas = self.env['glass.requisition'].search([('table_number','=',self.table_number)])			
			for requisition in requisitions:
				for line_req in requisition.lot_ids:
					res_lines = []
					if self.filter_field:
						if   self.filter_field == 'pending':
							res_lines = list(filter(lambda x :x.templado==False, line_req.lot_id.line_ids))
						elif self.filter_field == 'produced':
							res_lines = list(filter(lambda x :x.templado==True, line_req.lot_id.line_ids))
						elif self.filter_field == 'to inter':
							res_lines = list(filter(lambda x:x.templado==True and ingresado==False,line_req.lot_id.line_ids))
						elif self.filter_field == 'to deliver':
							res_lines = list(filter(lambda x:x.ingresado==True and entregado==False,line_req.lot_id.line_ids))
					else:
						res_lines = line_req.lot_id.line_ids
					for lote_line in res_lines:
						if lote_line.id not in orders1:
							orders1.append(lote_line.id)

		else:
			if self.order_id:
				lineas = self.env['glass.order.line'].search([('order_id','=',self.order_id.id),('state','=','process')])
				lines_with_lot=list(filter(lambda x: x.lot_line_id,lineas))
				lot_lines = map(lambda x: x.lot_line_id, lines_with_lot)
				lines_without_lot=list(filter(lambda x: not x.lot_line_id,lineas))
				if self.filter_field:
					if   self.filter_field == 'pending':
						lot_lines = list(filter(lambda x :x.templado==False,lot_lines))
					elif self.filter_field == 'produced':
						lot_lines = list(filter(lambda x :x.templado==True,lot_lines))
					elif self.filter_field == 'to inter':
						lot_lines = list(filter(lambda x:x.templado==True and ingresado==False,lot_lines))
					elif self.filter_field == 'to deliver':
						lot_lines = list(filter(lambda x:x.ingresado==True and entregado==False,lot_lines))
				for linea in lot_lines:
					if linea.id not in orders1:
						orders1.append(linea.id)
			else:
				if self.lote_id:
					orders1=[]
					lineas = self.env['glass.lot.line'].search([('lot_id','=',self.lote_id.id)] + domain)
					for line in lineas:
						if line.id not in orders1:
							orders1.append(line.id)

		if len(orders1)>0:
			orders = self.env['glass.lot.line'].browse(orders1)
		else:
			orders = self.env['glass.order'].search([('date_order','>=',self.date_ini),('date_order','<=',self.date_end)])
			for order in orders:
				for line_order in order.line_ids:
					if line_order.lot_line_id.id not in orders1:
							orders1.append(line_order.lot_line_id.id)
			orders = self.env['glass.lot.line'].browse(orders1)
		tot_optimizado=0
		tot_corte=0
		tot_pulido=0
		tot_entalle=0
		tot_lavado=0
		tot_horno=0
		tot_templado=0
		tot_insulado=0
		tot_comprado=0
		tot_ingresado=0
		tot_entregado=0
		tot_requisicion=0

		if len(lines_without_lot) > 0:
			for line in lines_without_lot:
				self.env['glass.list.wizard'].create({
					'order_id':line.order_id.id,
					'crysta_number':line.crystal_number,
					'base1':line.base1,
					'base2':line.base2,
					'altura1':line.altura1,
					'altura2':line.altura2,
					'descudre':line.descuadre,
					'nro_pagina':line.page_number,
					'partner_id':line.order_id.partner_id.id,
					'estado':line.order_id.state,
					'glass_break':line.glass_break,
					'repos':line.glass_repo,
					'main_id':self.id,
					'lot_line_id':line.lot_line_id.id if line.lot_line_id.id else line.last_lot_line.id,
					'croquis':line.image_page,
					'order_line':line.id,
					'decorator': 'without_lot',
					})						
		for line in orders:
			corte=False
			pulido=False
			entalle=False
			lavado=False
			horno=False
			templado=False
			insulado=False
			comprado=False
			ingresado=False
			entregado=False
			optimizado=False
			requisicion= False
			estados = self.env['glass.stage.record'].search([('lot_line_id','=',line.id)])

			for estado in estados:
				if estado.stage== 'corte':
					corte = True
					tot_corte=tot_corte+1
				if estado.stage== 'pulido':
					tot_pulido=tot_pulido+1
					pulido= True
				if estado.stage== 'entalle':
					tot_entalle=tot_entalle+1
					entalle= True
				if estado.stage== 'lavado':
					tot_lavado=tot_lavado+1
					lavado= True
				if estado.stage== 'horno':
					tot_horno=tot_horno+1
					horno= True
				if estado.stage== 'templado':
					tot_templado=tot_templado+1
					templado= True
				if estado.stage== 'insulado':
					tot_insulado=tot_insulado+1
					insulado= True
				if estado.stage== 'compra':
					tot_comprado=tot_comprado+1
					comprado= True
				if estado.stage== 'ingresado':
					tot_ingresado=tot_ingresado+1
					ingresado= True
				if estado.stage== 'entregado':
					tot_entregado=tot_entregado+1
					entregado= True
				if estado.stage== 'optimizado':
					tot_optimizado=tot_optimizado+1
					optimizado= True
				if estado.stage== 'requisicion':
					tot_requisicion=tot_requisicion+1
					requisicion= True
			
			self.env['glass.list.wizard'].create({
				'order_id':line.order_prod_id.id,
				'crysta_number':line.nro_cristal,
				'base1':line.base1,
				'base2':line.base2,
				'altura1':line.altura1,
				'altura2':line.altura2,
				'descudre':line.descuadre,
				'nro_pagina':line.page_number,
				'optimizado':optimizado,
				'corte':corte,
				'pulido':pulido,
				'entalle':entalle,
				'lavado':lavado,
				'horno':horno,
				'templado':templado,
				'insulado':insulado,
				'comprado':comprado,
				'ingresado':ingresado,
				'entregado':entregado,
				'requisicion':requisicion,
				'partner_id':line.order_prod_id.partner_id.id,
				'estado':line.order_prod_id.state,
				'glass_break':line.order_line_id.glass_break,
				'decorator': 'break' if line.order_line_id.glass_break else 'default',
				'repos':line.order_line_id.glass_repo,
				'order_line':line.order_line_id.id,
				'main_id':self.id,
				'lot_line_id':line.order_line_id.lot_line_id.id if line.order_line_id.lot_line_id.id else line.order_line_id.last_lot_line.id,
				'lot_id': line.order_line_id.lot_line_id.lot_id.id if line.order_line_id.lot_line_id.id else False,
				'croquis':line.order_line_id.image_page,
				})

		vals={
			'tot_optimizado':tot_optimizado,
			'tot_corte':tot_corte,
			'tot_pulido':tot_pulido,
			'tot_entalle':tot_entalle,
			'tot_lavado':tot_lavado,
			'tot_horno':tot_horno,
			'tot_templado':tot_templado,
			'tot_insulado':tot_insulado,
			'tot_comprado':tot_comprado,
			'tot_ingresado':tot_ingresado,
			'tot_entregado':tot_entregado,
			'tot_requisicion':tot_requisicion,
		}
		self.write(vals)
		return True


class GlassListWizard(models.Model):
	_name='glass.list.wizard'

	main_id = fields.Many2one('glass.list.main.wizard','Main')
	order_id = fields.Many2one('glass.order','Orden producción')
	crysta_number = fields.Integer('Nro. cristal')
	base1=fields.Float('Base1',digist=(12,2))
	base2=fields.Float('Base2',digist=(12,2))
	altura1=fields.Float('Altura1',digist=(12,2))
	altura2=fields.Float('Altura2',digist=(12,2))
	descudre=fields.Char('Descuadre')
	nro_pagina=fields.Char('Nro. página')
	optimizado=fields.Boolean('Optimizado') 
	requisicion=fields.Boolean(u'Requisición') 
	
	corte=fields.Boolean('Corte')
	pulido=fields.Boolean('Pulido')
	entalle=fields.Boolean('Entalle')
	lavado=fields.Boolean('Lavado') 
	templado=fields.Boolean('Templado')
	horno = fields.Boolean('Horno')
	insulado=fields.Boolean('Insulado') 
	comprado=fields.Boolean('Comprado')
	ingresado=fields.Boolean('Ingresado') 
	entregado=fields.Boolean('Entregado') 
	glass_break=fields.Boolean("Roto")
	repos=fields.Boolean(u"Reposición")
	partner_id = fields.Many2one('res.partner','Cliente')
	estado = fields.Selection([('draft','Generada'),('confirmed','Emitida'),('process','En Proceso'),('ended','Producido'),('instock','Ingresado'),('send2partner','Entregada')], 'Estado')
	order_line = fields.Many2one('glass.order.line','Lineapedido')
	lot_line_id = fields.Many2one('glass.lot.line','Linealote')
	lot_id = fields.Many2one('glass.lot','Lote')
	croquis=fields.Binary('Croquis')
	# nombre corto original:
	display_name_lot = fields.Char(string='Lote', related='lot_id.name')
	display_name_partner=fields.Char(string='Cliente',compute='_get_display_name_partner')
	# campo par mostrar la info del prod:
	presentation = fields.Char(string='Presentacion', compute='_get_display_presentation')

	# Campo auxiliar para mostrar las lineas que no tienen lote de produccion:
	decorator = fields.Selection([('default','default'),('break','break'),('without_lot','without_lot')],default='default')

	@api.depends('lot_line_id')
	def _get_display_presentation(self):
		for record in self:
			if record.lot_line_id.product_id.name:
				try:
					record.presentation=record.lot_line_id.product_id.name.split(',')[1]
				except IndexError as e:
					print('Error: ', e)
					record.presentation = 'NN'
			elif record.order_line.product_id.name:
				try:
					record.presentation=record.order_line.product_id.name.split(',')[1]
				except IndexError as e:
					print('Error: ', e)
					record.presentation = 'NN'
			else:
				record.presentation = 'NN'	
				

	@api.depends('partner_id')
	def _get_display_name_partner(self):
		for record in self:
			record.display_name_partner = record.partner_id.name[:10]

	@api.multi
	def show_stages(self):
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_stage_record_tree1' % module)
		data = {
			'name': _('Seguimiento'),
			'view_type': 'tree',
			'view_mode': 'tree',
			'res_model': 'glass.stage.record',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
			'domain': [('lot_line_id','=',self.lot_line_id.id)]
		} 
		#print self.lot_line_id.id
		return data

	@api.multi
	def break_crystal(self):
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_respos_wizard_form' % module)
		data = {
			'name': _('Rotura de Cristales'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.respos.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 
		return data

	@api.multi
	def show_croquis(self):
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_list_image_form' % module)
		data = {
			'name': _('Croquis'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.list.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
			'res_id':self.id,
		} 
		return data

class GlassReposWizard(models.TransientModel):
	_name='glass.respos.wizard'

	motive = fields.Selection([
		('eentalle','Error entalle'), 
		('emedida','Error medidas'), 
		('vrayado','Vidrio rayado'), 
		('vroto','Vidrio roto'), 
		('planimetria','Planimetria'), 
		('eventas','Error ventas'), 
		('mprima','Materia prima')])
	stage = fields.Selection([
		('corte','Corte'), 
		('pulido','Pulido'), 
		('entalle','Entalle'), 
		('lavado','Lavado'), 
		('templado','Templado'),
		('insulado','Insulado'),
		('produccion',u'Producción')],'Etapa') 
	date_fisical=fields.Date('Fecha de Rotura',default=fields.Date.today())
	date_record=fields.Date('Fecha de Registro',default=fields.Date.today())
	



	@api.one
	def makerepo(self):
		active_ids = self._context['active_ids']
		line = self.env['glass.list.wizard'].browse(active_ids)
		paso = False
		if self.stage=='corte':
			if line.lot_line_id.corte:
				paso = True
		if self.stage=='pulido':
			if line.lot_line_id.pulido:
				paso = True
		if self.stage=='entalle':
			if line.lot_line_id.entalle:
				paso = True
		if self.stage=='lavado':
			if line.lot_line_id.lavado:
				paso = True
		if self.stage=='templado':
			if line.lot_line_id.templado:
				paso = True
		if not paso:		
			raise UserError(u'No se puede registrar debido a que uno de los cristales no se encuentra en la etapa seleccionada')							
		data = {
			'user_id':self.env.uid,
			'date':datetime.now(),
			'time':datetime.now().time(),
			'stage':'roto',
			'lot_line_id':line.lot_line_id.id,
			'date_fisical':self.date_fisical,
		}
		stage_obj = self.env['glass.stage.record']
		stage_obj.create(data)
		line.order_line.last_lot_line=line.lot_line_id.id
		line.order_line.glass_break=True
		line.order_line.lot_line_id=False
		line.order_line.is_used=False
		line.lot_line_id.is_break=True