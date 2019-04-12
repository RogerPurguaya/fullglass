# -*- coding: utf-8 -*-
#Seguimiento a la produccion en Produccion
from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from decimal import *
from functools import reduce

class GlassListMainWizard(models.Model):
	_name='glass.list.main.wizard'
	_rec_name = 'titulo'
	titulo = fields.Char(default='Seguimiento de Produccion')
	order_id = fields.Many2one('glass.order','Orden')
	lote_id = fields.Many2one('glass.lot','Lote')
	requisition_id = fields.Many2one('glass.requisition',string="Mesa")
	line_ids = fields.One2many('glass.list.wizard','main_id','Lineas')
	filter_field = fields.Selection([('all','Todos'),('pending','Pendientes'),('produced','Producidos'),('to inter','Por ingresar'),('to deliver','Por Entregar'),('expired','Vencidos')],string='Filtro',default='all')
	search_param = fields.Selection([('glass_order','Orden de Produccion'),('requisition','Mesa'),('lot','Lote')],default='glass_order',string='Busqueda por')
	show_breaks = fields.Boolean('Mostrar Rotos')
	count_total_crystals = fields.Integer('Nro cristales',compute='_get_count_crystals')
	total_area_breaks = fields.Float('Total Rotos M2',compute='_get_total_area_breaks',digits=(20,4))
	count_total_breaks = fields.Integer('Nro Rotos',compute='_get_count_breaks')
	percentage_breaks = fields.Float('Porcentage de rotos',compute='_get_percentage_breaks',digits=(20,4)) 
	total_area = fields.Float('Total M2',compute='_get_total_area', digits=(20,4))
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

	@api.depends('line_ids','total_area_breaks')
	def _get_total_area(self):
		for record in self:
			areas = record.line_ids.mapped('area')
			if len(areas) > 0:
				record.total_area = reduce(lambda x,y: x+y,areas) - record.total_area_breaks
			else:
				record.total_area = 0

	@api.depends('line_ids','count_total_breaks')
	def _get_count_crystals(self):
		for record in self:
			record.count_total_crystals = len(record.line_ids) - record.count_total_breaks

	@api.depends('line_ids')
	def _get_total_area_breaks(self):
		for record in self:
			line_ids = record.line_ids.mapped('lot_line_id').filtered(lambda x: x.is_break)
			if len(line_ids) > 0:
				record.total_area_breaks=reduce(lambda x,y: x+y,line_ids.mapped('area'))
			else:
				record.total_area_breaks = 0

	@api.depends('line_ids')
	def _get_count_breaks(self):
		for record in self:
			record.count_total_breaks = len(record.line_ids.filtered(lambda x: x.glass_break))

	@api.depends('total_area','total_area_breaks')
	def _get_percentage_breaks(self):
		for record in self:
			if record.total_area > 0:
				record.percentage_breaks=(record.total_area_breaks/record.total_area)*100
			else:
				record.percentage_breaks=0
					
	@api.multi
	def makelist(self):
		self.ensure_one()
		lin = self.env['glass.list.wizard'].search([])
		for l in lin:
			l.unlink()

		orders=[]
		lines_without_lot=[] # lineas sin lote de produccion

		if self.requisition_id and self.search_param == 'requisition':
						
			lot_lines = self.requisition_id.mapped('lot_ids').mapped('lot_id').mapped('line_ids')
			orders = self._get_data(lot_lines)

		elif self.order_id and self.search_param == 'glass_order':
			lineas = self.order_id.mapped('line_ids')
			lot_lines=(lineas.filtered(lambda x: x.lot_line_id)).mapped('lot_line_id')
			orders = self._get_data(lot_lines)
			lines_without_lot=lineas.filtered(lambda x: not x.lot_line_id)
			# en este caso sacamos los cristales rotos manualmente:
			if self.show_breaks:
				glass_breaks = self.env['glass.lot.line'].search([('order_line_id','in',lineas.ids),('is_break','=',True)])
				orders += glass_breaks

		elif self.lote_id and self.search_param == 'lot':
			orders = self._get_data(self.lote_id.mapped('line_ids')) 
		
		if len(orders)==0 and len(lines_without_lot)==0:
			raise exceptions.Warning('No se ha encontrado informacion.')

		if len(lines_without_lot) > 0 and self.filter_field in ('all','pending'):
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
					'repos':line.glass_repo,
					'main_id':self.id,
					'croquis':line.image_page,
					'order_line':line.id,
					'decorator': 'without_lot',
					})						
		for line in orders:			
			self.env['glass.list.wizard'].create({
				'order_id':line.order_prod_id.id,
				'crysta_number':line.nro_cristal,
				'base1':line.base1,
				'base2':line.base2,
				'altura1':line.altura1,
				'altura2':line.altura2,
				'descudre':line.descuadre,
				'nro_pagina':line.page_number,
				'optimizado':line.optimizado,
				'corte':line.corte,
				'pulido':line.pulido,
				'entalle':line.entalle,
				'lavado':line.lavado,
				'horno':line.horno,
				'templado':line.templado,
				'insulado':line.insulado,
				'comprado':line.comprado,
				'ingresado':line.ingresado,
				'entregado':line.entregado,
				'requisicion':line.requisicion,
				'partner_id':line.order_prod_id.partner_id.id,
				'estado':line.order_prod_id.state,
				'glass_break':line.is_break,
				'decorator': 'break' if line.is_break else 'default',
				'repos':line.order_line_id.glass_repo,
				'order_line':line.order_line_id.id,
				'main_id':self.id,
				'lot_line_id':line.id,
				'lot_id': line.lot_id.id,
				'croquis':line.order_line_id.image_page_number,
				})

		vals={
		'tot_optimizado':len(list(filter(lambda x:x.templado and not x.is_break,orders))),
		'tot_corte':len(list(filter(lambda x:x.corte and not x.is_break,orders))),
		'tot_pulido':len(list(filter(lambda x:x.pulido and not x.is_break,orders))),
		'tot_entalle':len(list(filter(lambda x:x.entalle and not x.is_break,orders))),
		'tot_lavado':len(list(filter(lambda x:x.lavado and not x.is_break,orders))),
		'tot_horno':len(list(filter(lambda x:x.horno and not x.is_break,orders))),
		'tot_templado':len(list(filter(lambda x:x.templado and not x.is_break,orders))),
		'tot_insulado':len(list(filter(lambda x:x.insulado and not x.is_break,orders))),
		'tot_comprado':len(list(filter(lambda x:x.comprado and not x.is_break,orders))),
		'tot_ingresado':len(list(filter(lambda x:x.ingresado and not x.is_break,orders))),
		'tot_entregado':len(list(filter(lambda x:x.entregado and not x.is_break,orders))),
		'tot_requisicion':len(list(filter(lambda x:x.requisicion and not x.is_break,orders))),
		} 
		self.write(vals)
		return True


	@api.multi
	def _get_data(self,lot_lines):
		if self.filter_field:
			if self.filter_field == 'all':
				pass
			elif self.filter_field == 'pending':
				lot_lines = lot_lines.filtered(lambda x:x.templado==False)
			elif self.filter_field == 'produced':
				lot_lines = lot_lines.filtered(lambda x:x.templado==True)
			elif self.filter_field == 'to inter':
				lot_lines = lot_lines.filtered(lambda x:x.templado==True and x.ingresado==False)
			elif self.filter_field == 'to deliver':
				lot_lines = lot_lines.filtered(lambda x:x.ingresado==True and x.entregado==False)
			elif self.filter_field == 'expired':
				now = datetime.now().date()
				lot_lines = lot_lines.filtered(lambda x: datetime.strptime(x.order_prod_id.date_delivery.replace('-',''),"%Y%m%d").date() < now and x.templado == False)
		if not self.show_breaks:
			lot_lines = lot_lines.filtered(lambda x: not x.is_break)
		return list(set(lot_lines))

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
	arenado = fields.Boolean('Arena') 
	glass_break=fields.Boolean("Roto")
	repos=fields.Boolean(u"Reposición")
	partner_id = fields.Many2one('res.partner','Cliente')
	estado = fields.Selection([('draft','Generada'),('confirmed','Emitida'),('process','En Proceso'),('ended','Producido'),('instock','Ingresado'),('send2partner','Entregada')], 'Estado')
	order_line = fields.Many2one('glass.order.line','Lineapedido')
	lot_line_id = fields.Many2one('glass.lot.line','Linealote')
	lot_id = fields.Many2one('glass.lot','Lote')
	croquis=fields.Char('Croquis')
	area = fields.Float('Area',related='order_line.area',digits=(20,4))
	
	# nombre corto:
	display_name_lot = fields.Char(string='Lote', related='lot_id.name')
	display_name_partner=fields.Char(string='Cliente',compute='_get_display_name_partner')
	product_name = fields.Char('Producto',related='order_line.product_id.name')
	# Campo auxiliar para mostrar las lineas que no tienen lote de produccion:
	decorator = fields.Selection([('default','default'),('break','break'),('without_lot','without_lot')],default='default')
	
	@api.depends('partner_id')
	def _get_display_name_partner(self):
		for record in self:
			record.display_name_partner = record.partner_id.name[:14] if record.partner_id.name else ''

	@api.multi
	def show_detail_tracing_line(self):
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.show_detail_tracing_line_wizard_form' % module, False)
		wizard = self.env['show.detail.tracing.line.wizard'].create({'lot_line_id':self.lot_line_id.id})
		return{
			'name': 'Detalle de Seguimiento',
			'res_id': wizard.id,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'show.detail.tracing.line.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 

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
		path = self.env['main.parameter'].search([])[0].download_directory
		
		file = None
		if self.croquis:
			file = open(self.croquis,'rb')
			cont_t = file.read()
			file.close()
			file_new = open(path + 'croquis.pdf','wb')
			file_new.write(cont_t)
			file_new.close()
		else:
			import PyPDF2
			writer = PyPDF2.PdfFileWriter()
			writer.insertBlankPage(width=500, height=500, index=0)
			with open(path+'croquis.pdf', "wb") as outputStream: 
				writer.write(outputStream) #write pages to new PDF

		return {
			'name': _('Croquis'),
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.list.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
			'res_id':self.id,
		} 

class GlassReposWizard(models.TransientModel):
	_name='glass.respos.wizard'
	motive = fields.Selection([
		('Error entalle','Error entalle'), 
		('Error medidas','Error medidas'), 
		('Vidrio rayado','Vidrio rayado'), 
		('Vidrio roto','Vidrio roto'), 
		('Planimetria','Planimetria'), 
		('Error ventas','Error ventas'), 
		('Materia prima','Materia prima')])
	stage = fields.Selection([
		('corte','Corte'), 
		('pulido','Pulido'), 
		('entalle','Entalle'), 
		('lavado','Lavado'), 
		('templado','Templado'),
		('horno','Horno'),
		('insulado','Insulado')],'Etapa') 
	
	@api.one
	def makerepo(self):
		active_ids = self._context['active_ids']
		line = self.env['glass.list.wizard'].browse(active_ids)
		
		stage = line.lot_line_id.stages_ids.filtered(lambda x: x.stage == self.stage)
		if len(stage) == 0:
			raise UserError(u'El cristal a no ha pasado por la etapa seleccionada!\nSeleccione la ultima etapa exitosa del cristal')	
						
		stage_obj = self.env['glass.stage.record'].create({
			'user_id':self.env.uid,
			'date':stage[0].date, #registrar rotura con la fecha y hora de la etapa sel.
			'time':stage[0].time,
			'stage':'roto',
			'lot_line_id':line.lot_line_id.id,
			'break_motive':self.motive
		})
		line.order_line.last_lot_line=line.lot_line_id.id
		line.order_line.glass_break=True
		line.order_line.lot_line_id=False
		line.order_line.is_used=False
		line.lot_line_id.is_break=True