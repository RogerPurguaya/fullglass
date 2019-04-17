# -*- coding: utf-8 -*-
# Aegumiento a la produccion en almacen
from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime
from functools import reduce

class Glass_tracing_Production_Stock(models.Model):
	_name='glass.tracing.production.stock'
	_rec_name = 'titulo'
	titulo = fields.Char(default='Seguimiento de Produccion Almacen')
	order_id = fields.Many2one('glass.order',string='Orden')
	customer_id = fields.Many2one('res.partner',string='Cliente')
	invoice_id = fields.Many2one('account.invoice',string='Factura')
	date_ini = fields.Date('Fecha Inicio')
	date_end = fields.Date('Fecha Fin')
	line_ids = fields.One2many('tracing.production.stock.line.lot','parent_id','Lineas')
	filter_field = fields.Selection([('all','Todos'),('pending','Pendientes'),('produced','Producidos'),('to inter','Por ingresar'),('to deliver','Por Entregar'),('expired','Vencidos')],string='Filtro',default='all')
	search_param = fields.Selection([('glass_order','Orden de Produccion'),('invoice','Factura'),('customer','Cliente')],default='glass_order',string='Busqueda por')
	show_breaks = fields.Boolean('Mostrar Rotos')
	total_area = fields.Float('Total M2',compute='_get_total_area',digits=(12,4))
	count_total_crystals = fields.Integer('Nro Cristales', compute='_get_count_crystals')
	show_customer = fields.Many2one('res.partner',string='Cliente', compute='_get_show_customer')
	show_invoice = fields.Many2one('account.invoice',string='Factura', compute='_get_show_invoice')

	total_area_breaks = fields.Float('Total Rotos M2',compute='_get_total_area_breaks',digits=(12,4))
	count_total_breaks = fields.Integer('Nro Rotos',compute='_get_count_beaks')
	percentage_breaks = fields.Float('Porcentage de rotos',compute='_get_percentage_breaks') 
	tot_templado=fields.Integer('Templado')
	tot_arenado=fields.Integer('Arenado')
	tot_ingresado=fields.Integer('Ingresado')
	tot_entregado=fields.Integer('Entregado')
	for_delivery = fields.Integer('Cristales por entregar',compute='_get_for_delivery')

	@api.depends('search_param','customer_id','invoice_id','order_id')
	def _get_show_customer(self):
		for record in self:
			if record.search_param == 'glass_order' and record.order_id:
				record.show_customer = record.order_id.partner_id.id
			elif record.search_param == 'invoice' and record.invoice_id:
				record.show_customer = record.invoice_id.partner_id.id
			elif record.search_param == 'customer' and record.customer_id:
				record.show_customer = record.customer_id.id
			else:
				record.show_customer = False

	@api.depends('search_param','customer_id','invoice_id','order_id')
	def _get_show_invoice(self):
		for record in self:
			if record.search_param == 'glass_order' and record.order_id:
				record.show_invoice = record.order_id.invoice_ids[0].id
			elif record.search_param == 'invoice' and record.invoice_id:
				record.show_invoice = record.invoice_id.id
			elif record.search_param == 'customer' and record.customer_id:
				record.show_invoice = False
			else:
				record.show_invoice = False

	@api.depends('line_ids')
	def _get_total_area(self):
		for record in self:
			areas = record.line_ids.mapped('lot_line_id').filtered(lambda x:not x.is_break).mapped('area')
			if len(areas) > 0:
				record.total_area = reduce(lambda x,y: x+y,areas)
			else:
				record.total_area = 0
	
	@api.depends('line_ids')
	def _get_count_crystals(self):
		for record in self:
			record.count_total_crystals = len(record.line_ids.mapped('lot_line_id').filtered(lambda x:not x.is_break))

	@api.depends('line_ids')
	def _get_total_area_breaks(self):
		for record in self:
			line_ids = record.line_ids.mapped('lot_line_id').filtered(lambda x: x.is_break)
			if len(line_ids) > 0:
				record.total_area_breaks=reduce(lambda x,y: x+y,line_ids.mapped('area'))
			else:
				record.total_area_breaks = 0

	@api.depends('line_ids')
	def _get_count_beaks(self):
		for record in self:
			record.count_total_breaks = len(record.line_ids.mapped('lot_line_id').filtered(lambda x: x.is_break))

	@api.depends('total_area','total_area_breaks')
	def _get_percentage_breaks(self):
		for record in self:
			if record.total_area > 0:
				record.percentage_breaks=(record.total_area_breaks/record.total_area)*100
			else:
				record.percentage_breaks=0
	
	@api.depends('line_ids')
	def _get_for_delivery(self):
		for record in self:
			record.for_delivery = len(record.line_ids.mapped('lot_line_id').filtered(lambda x: not x.entregado and not x.is_break))

	@api.multi
	def makelist(self):
		self.ensure_one()
		lin = self.env['tracing.production.stock.line.lot'].search([])
		for l in lin:
			l.unlink()

		lines=[]
		if self.invoice_id and self.search_param == 'invoice':
			invoice_lines = self.invoice_id.invoice_line_ids
			sale_order_lines = invoice_lines.mapped('sale_line_ids')
			sale_order = sale_order_lines.mapped('order_id')
			if len(set(sale_order)) == 1:
				lines = sale_order.op_ids.mapped('line_ids').mapped('lot_line_id')
				aux_lines = sale_order.op_ids.mapped('line_ids')
				lines = self._get_data(lines)
			if self.show_breaks:
				glass_breaks = self.env['glass.lot.line'].search([('order_line_id','in',aux_lines.ids),('is_break','=',True)])
				lines += glass_breaks

		elif self.order_id and self.search_param == 'glass_order':
			lines=(self.order_id.line_ids.filtered(lambda x:x.lot_line_id)).mapped('lot_line_id')
			lines = self._get_data(lines)
			if self.show_breaks:
				glass_breaks = self.env['glass.lot.line'].search([('order_line_id','in',self.order_id.line_ids.ids),('is_break','=',True)])
				lines += glass_breaks

		elif self.customer_id and self.search_param == 'customer':
			sale_orders = self.env['sale.order'].search([('partner_id','=',self.customer_id.id)])
			lines = sale_orders.mapped('op_ids').mapped('line_ids').mapped('lot_line_id')
			lines = self._get_data(lines)
			if self.show_breaks:
				glass_breaks = self.env['glass.lot.line'].search([('order_line_id','in',sale_orders.mapped('op_ids').mapped('line_ids').ids),('is_break','=',True)])
				lines += glass_breaks

		if len(lines)==0:
			raise exceptions.Warning('NO SE HA ENCONTRADO INFORMACION.\nEs posible que los cristales aun no hayan iniciado el proceso de produccion')

		for line in lines:
			self.env['tracing.production.stock.line.lot'].create({
				'order_id':line.order_prod_id.id,
				'crystal_number':line.nro_cristal,
				'base1':line.base1,
				'base2':line.base2,
				'altura1':line.altura1,
				'altura2':line.altura2,
				'customer_id':line.order_prod_id.partner_id.id,
				'templado':line.templado,
				'ingresado':line.ingresado,
				'entregado':line.entregado,
				'arenado':line.arenado, # pendiente de cambio
				'embalado':False,
				'decorator':'break' if line.is_break else 'default',
				'parent_id':self.id,
				'lot_line_id':line.id,
				'is_break': line.is_break,
				})
		self.write({
		'tot_templado':len(list(filter(lambda x:x.templado and not x.is_break,lines))),
		'tot_ingresado':len(list(filter(lambda x:x.ingresado and not x.is_break,lines))),
		'tot_entregado':len(list(filter(lambda x:x.entregado and not x.is_break,lines))),
		'tot_arenado':len(list(filter(lambda x:x.arenado and not x.is_break,lines))),
		})
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
		if self.date_ini and self.date_end and self.search_param == 'customer':
			start = self._str2date(self.date_ini)
			end = self._str2date(self.date_end)
			lot_lines = lot_lines.filtered(lambda x: self._str2date(x.order_date_prod) < end and self._str2date(x.order_date_prod) > start)
		if not self.show_breaks:
			lot_lines = lot_lines.filtered(lambda x: not x.is_break)
		return list(set(lot_lines))

	def _str2date(self,string):
		return datetime.strptime(string.replace('-',''),"%Y%m%d").date()

class Tracing_Production_Stock_Line_Lot(models.Model):
	_name = 'tracing.production.stock.line.lot'

	parent_id = fields.Many2one('glass.tracing.production.stock','Main')
	order_id = fields.Many2one('glass.order','Orden produccion')
	lot_line_id = fields.Many2one('glass.lot.line','Linea de lote')
	product_name = fields.Char('Producto',related='lot_line_id.order_line_id.product_id.name')
	customer_id = fields.Many2one('res.partner','Cliente')
	crystal_number = fields.Integer('Nro. cristal')
	base1=fields.Integer('Base1')
	base2=fields.Integer('Base2')
	altura1=fields.Integer('Altura1')
	altura2=fields.Integer('Altura2')
	arenado = fields.Boolean('Arena')
	embalado = fields.Boolean('Embalado')
	templado=fields.Boolean('Templado')
	ingresado=fields.Boolean('Ingresado') 
	entregado=fields.Boolean('Entregado')  
	decorator = fields.Selection([('default','default'),('break','break'),('without_lot','without_lot')],default='default')
	is_break = fields.Boolean('Roto')

	@api.multi
	def show_detail_tracing_line(self):
		view = self.env.ref('glass_production_order.show_detail_tracing_line_wizard_form', False)
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

