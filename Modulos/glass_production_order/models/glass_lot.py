# -*- coding: utf-8 -*-

from odoo import fields, models,api, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassTable(models.Model):
	_name='glass.table'

	name = fields.Char('Lote')
	date =fields.Date('Fecha',default=datetime.now())
	lot_ids = fields.One2many('glass.lot','table_id','Lotes')

class GlassLot(models.Model):
	_name='glass.lot'
	_inherit = ['mail.thread']
	_order="id desc"

	name = fields.Char('Lote', default='/')
	state = fields.Selection([('draft','Nuevo'),('cancel','Cancelado'),('done','Emitido')],'Estado',track_visibility='always',default='draft')
	date = fields.Date('Fecha',default=datetime.now())
	product_id=fields.Many2one('product.product','Producto')
	total_pza = fields.Integer('Total Piezas',compute="_countlines")
	total_area = fields.Float('Área Total',compute="_totalarea",digits=(20,4))
	table_id = fields.Many2one('glass.table','Mesa')
	line_ids=fields.One2many('glass.lot.line','lot_id','Detalle')
	crystal_count=fields.Integer(u'Número de cristales',compute="getcrystalcount")
	user_id = fields.Many2one('res.users','Responsable')
	optimafile=fields.Binary('Archivo OPTIMA')
	file_name = fields.Char(string='File Name', compute='_get_file_name')

	@api.depends('name')
	def _get_file_name(self):
		for record in self:
			ext = False
			try:
				ext = self.env['glass.order.config'].search([])[0].optimization_ext
			except IndexError as e:
				print('Error: ',e)
			if ext:
				record.file_name = record.name.rjust(7,'0') +'.'+ext
			else:
				record.file_name = record.name.rjust(7,'0') +'.ext'

	@api.multi
	@api.depends('name', 'product_id')
	def name_get(self):
		result = []
		for lote in self:
			name = lote.name + ' ' + lote.product_id.name
			result.append((lote.id, name))
		return result


	@api.one
	def unlink(self):
		if self.state in ['cancel','done']:
			raise UserError(u'No se puede eliminar en los estados: Cancelada o Emitida')		
		return super(GlassLot,self).unlink()

	@api.one
	def optimize_lot(self):
		for line in self.line_ids:
			line.order_line_id.order_id.state="process"
		return True


	@api.one
	def getcrystalcount(self):
		crystal_count=len(self.line_ids)

	@api.one
	def cancel_lot(self):
		for line in self.line_ids:
			line.order_line_id.is_used=False
			line.unlink()
		self.state='cancel'
		return True

	@api.one
	def _totalarea(self):	
		tot=0
		for line in self.line_ids:
			tot = tot+line.area
		self.total_area = tot

	@api.one
	def _countlines(self):
		self.total_pza=len(self.line_ids)

	@api.one
	def validate_lot(self):
		config_data = self.env['glass.order.config'].search([])[0]
		if self.name=='/':
			newname = config_data.seq_lot.next_by_id()
			self.update({'name':newname})
		self.write({'state':'done'})
		for line in self.line_ids:
			line.order_line_id.is_used = True
		return True

	@api.onchange('line_ids')
	def onchange_lines(self):
		self.total_pza = len(self.line_ids)

	@api.multi
	def showpool(self):
		# search_view_ref = self.env.ref('account.view_account_invoice_filter', False)
		form_view_ref = self.env.ref('glass_production_order.view_glass_pool_wizard_form', False)
		# tree_view_ref = self.env.ref('account.invoice_tree', False)
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_pool_wizard_form' % module)
		data = {
			'name': _('Pool de pedidos'),
			'context': self._context,
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.pool.wizard',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'new',
		} 
		return data




class GlassLotLine(models.Model):
	_name='glass.lot.line'

	product_id=fields.Many2one('product.product','Producto')
	nro_cristal = fields.Char(u"Número de Cristal",size=10,readonly=False)
	base1 = fields.Integer("Base1 (L 4)")
	base2 = fields.Integer("Base2 (L 2)")
	altura1 = fields.Integer("Altura1 (L 1)")
	altura2 = fields.Integer("Altura2 (L 3)")
	area = fields.Float(u'Área M2',digits=(12,4))
	descuadre = fields.Char("Descuadre",size=7)
	page_number = fields.Char(u"Nro. Pág.")
	
	optimizado = fields.Boolean("Optimizado")
	requisicion = fields.Boolean("Requisición")
	pulido = fields.Boolean("Pulido")
	entalle = fields.Boolean("Entalle")
	lavado = fields.Boolean("Lavado")
	horno = fields.Boolean("Horno")
	templado = fields.Boolean("Templado")
	insulado = fields.Boolean("Insulado")
	laminado = fields.Boolean("Laminado")
	entregado = fields.Boolean("Entregado")
	comprado = fields.Boolean("Comprado")
	corte = fields.Boolean("Corte")
	## new code:
	ingresado = fields.Boolean("Ingresado")

	is_service = fields.Boolean('Es servicio')
	type_prod = fields.Char('tipoproducto')

	lot_id = fields.Many2one('glass.lot','Lote')
	order_line_id = fields.Many2one('glass.order.line')
	order_date_prod = fields.Date('Fecha OP')
	order_prod_id = fields.Many2one('glass.order',related='order_line_id.order_id',string="OP")
	order_date_prod = fields.Date('Fecha OP',related='order_prod_id.date_production')
	search_code = fields.Char(u'Código de búsqueda')
	calc_line_id= fields.Many2one('sale.calculadora.proforma.line')
	image_glass = fields.Binary("imagen",related="calc_line_id.image")
	page_glass = fields.Binary(u"Página")
	merma = fields.Float('Merma',digist=(12,4))
	is_break = fields.Boolean('Roto')
	_rec_name="search_code"


	@api.multi
	def retire_lot_line(self):
		self.ensure_one()
		if self.corte:
			raise UserError(u'No se puede retirar si a pasado la etapa de corte')		
		stage_obj = self.env['glass.stage.record']
		stages = stage_obj.search([('lot_line_id','=',self.id)])
		rid =self.lot_id.id
		for s in stages:
			s.unlink()
		
		self.order_line_id.last_lot_line=self.id
		self.order_line_id.glass_break=False
		self.order_line_id.lot_line_id=False
		self.order_line_id.is_used=False
		self.order_line_id.retired_user=self.env.uid
		self.order_line_id.retired_date=datetime.now()
		self.unlink()
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.view_glass_lot_form' % module)
		data = {
			'name': u'Lotes de producción',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'glass.lot',
			'view_id': view.id,
			'type': 'ir.actions.act_window',
			'target': 'current',
			'res_id':rid,
		} 
		return data
		