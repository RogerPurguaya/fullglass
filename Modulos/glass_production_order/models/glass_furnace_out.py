# -*- coding: utf-8 -*-

from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError
from datetime import datetime

class GlassFurnaceOut(models.Model):
	_name='glass.furnace.out'
	_inherit = ['mail.thread']
	_order="date_out desc"

	name = fields.Char('Lote de Horno Salida',default="/")
	
	nro_crystal=fields.Integer('Nro. Cristales')
	total_m2=fields.Float('Total M2',digits=(12,4))
	e_percent=fields.Float('% de Eficiencia',digits=(12,4))
	state = fields.Selection([('draft','Borrador'),('confirm','Confirmado'),('process','En Proceso'),('done','Finalizado')],'Estado',default='draft')
	line_ids=fields.One2many('glass.furnace.line.out','main_id','Detalle')
	user_ingreso = fields.Many2one('res.users','Usuario Ingreso')
	date_ingreso = fields.Datetime('Fecha Ingreso')
	date_out=fields.Datetime('Fecha Salida')
	user_out = fields.Many2one('res.users','Usuario Salida')
	# new field
	search_code = fields.Char('Producto', store=False)
	message_erro = fields.Char('*',default='')
	cad3 = fields.Char('cad3',default='')
	show_button = fields.Boolean('Mostrar Limpiar', compute='_get_show_button')

	@api.depends('line_ids')
	def _get_show_button(self):
		for record in self:
			bad_lines = record.line_ids.filtered(lambda x: x.lot_line_id.is_break or x.lot_line_id.horno)
			if len(bad_lines) > 0:
				record.show_button = True
			else:
				record.show_button = False

	@api.onchange('search_code')
	def onchangecode(self):
		idsact = []
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		if self.search_code:
			if not self._origin.id:
				self.search_code = ""
				self.message_erro = "Debe guardar esta salida de horno antes de agregar productos."
				return
			
			existe = self.env['glass.lot.line'].search([('search_code','=',self.search_code)])
			self.message_erro=""
			
			for line in self.line_ids:
				pass
			if len(existe)>0:
				stage_obj = self.env['glass.stage.record']
				ext = stage_obj.search([('stage','=','templado'),('lot_line_id','=',existe.id)])
				if len(ext)>0:
					self.message_erro="El cristal seleccionado ya fue registrado en la etapa Templado"
					self.search_code=""
					return
				
				existe_act = existe[0]
				pasoentalle = stage_obj.search([('stage','=','lavado'),('lot_line_id','=',existe_act.id)])
				cuenta = 0

				# cambiando esto xq no funciona
				lines = self.env['glass.furnace.line.out'].search([('main_id','=',self._origin.id)])

				for line in lines:
					idsact.append(line.id)
					if line.lot_line_id.id==existe_act.id:
						cuenta = cuenta +1
				
				if cuenta>0:
					self.message_erro="El cristal seleccionado ya fue registrado en este ingreso a horno"
					self.search_code=""
					return						
				if len(pasoentalle)>0:
					ordern = len(self.line_ids)+1

					data = {
						#'main_id': self._origin.id,
						'order_number':ordern,
						'lot_id':existe_act.lot_id.id,
						'lot_line_id':existe_act.id,
						'crystal_number':existe_act.nro_cristal,
						'base1':existe_act.base1,
						'base2':existe_act.base2,
						'altura1':existe_act.altura1,
						'altura2':existe_act.altura2,
						'area':existe_act.area,
						'partner_id':existe_act.order_prod_id.partner_id.id,
						'obra':existe_act.order_prod_id.obra,
					}
					t=self.env['glass.furnace.line.out'].create(data)
					idsact.append(t.id)
					#print('create !', t)
					if self.cad3:
						self.cad3=self.cad3+str(t.id)+','
					else:
						self.cad3=str(t.id)+','
					
				else:
					self.message_erro="No se puede agregar un elemento que no tenga registrada la etapa LAVADO"
					self.search_code=""
					return
			else:
				self.message_erro="Codigo de busqueda no encontrado!"
				self.search_code=""
				return
		else:
			return

		obj = self.env['glass.furnace.out'].search([('id','=',self._origin.id)])
		obj.write({'line_ids': [(6,0,idsact)]})
		self.search_code=''

		return {'value':{'line_ids':idsact}}
# End code

	@api.onchange('line_ids')
	def onchangelines(self):
		
		area = 0
		for line in self.line_ids:
			area= area+line.area
			#print('lineas en el onchange ',line)
		self.total_m2=area
		self.nro_crystal=len(self.line_ids)
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		farea = config_data.furnace_area
		if area>0:
			self.e_percent=(area*100)/farea

	@api.model
	def create(self,vals):
		area = 0
		for line in self.line_ids:
			area= area+line.area
		vals.update({'total_m2':area})
		vals.update({'nro_crystal':len(self.line_ids)})
		vals.update({'date_out':datetime.now()})
		vals.update({'user_ingreso':self.env.uid})
		vals.update({'date_ingreso':datetime.now()})
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		farea = config_data.furnace_area
		if area>0:
			vals.update({'e_percent':(area*100)/farea})
		return super(GlassFurnaceOut,self).create(vals)

	@api.one
	def write(self,vals):
		area = 0

		for line in self.line_ids:
			area= area+line.area
		vals.update({'total_m2':area})
		vals.update({'nro_crystal':len(self.line_ids)})
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		farea = config_data.furnace_area
		if area>0:
			vals.update({'e_percent':(area*100)/farea})

		return super(GlassFurnaceOut,self).write(vals)
			
	@api.one
	def print_etiqueta(self):
		for line in self.line_ids:
			line.lot_line_id.etiqueta=True
		return True
	
	@api.multi
	def remove_bad_lines(self):
		bad_lines = self.line_ids.filtered(lambda x: x.lot_line_id.is_break or x.lot_line_id.horno)
		for item in bad_lines:
			item.unlink()
		return True

	@api.multi
	def confirm(self):
		self.state = 'confirm'

	@api.one
	def send_to_process(self):
		if len(self.line_ids) == 0:
			raise exceptions.Warning('No ha ingresado Cristales.')
		bad_lines = self.line_ids.filtered(lambda x: x.lot_line_id.is_break or x.lot_line_id.horno)
		if len(bad_lines) > 0:
			msg = ''
			for item in bad_lines:
				motive = ' :Cristal Roto' if item.lot_line_id.is_break else ' :Ya tiene etapa de horno'
				msg += '-> '+item.lot_line_id.search_code+' - '+item.lot_line_id.nro_cristal+motive+'\n'
			raise exceptions.Warning('Los siguientes cristales no pueden procesarse:\n'+msg+'Haga click en el boton Limpiar para quitar estos cristales y seguir el proceso.')
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		newname = config_data.seq_furnace.next_by_id()
		
		for line in self.line_ids:
			stage_obj = self.env['glass.stage.record'].create({
				'user_id':self.env.uid,
				'date':datetime.now(),
				'time':datetime.now().time(),
				'stage':'horno',
				'lot_line_id':line.lot_line_id.id,
				})
			line.lot_line_id.horno=True
		self.write({'name':newname, 'state': 'process'})
		return True

	@api.one
	def furnace_out(self):
		config_data = self.env['glass.order.config'].search([])
		if len(config_data)==0:
			raise UserError(u'No se encontraron los valores de configuracion de produccion')		
		config_data = self.env['glass.order.config'].search([])[0]
		if self.name=='/':
			newname = config_data.seq_furnace_out.next_by_id()
			self.update({'name':newname,})
		stage_obj = self.env['glass.stage.record']
		for line in self.line_ids:
			ext = stage_obj.search([('stage','=','templado'),('lot_line_id','=',line.lot_line_id.id)])
			if len(ext)>0:
				raise UserError(u'El cristal seleccionado ya fue registrado en la etapa Templado')		
			data = {
					'user_id':self.env.uid,
					'date':datetime.now(),
					'time':datetime.now().time(),
					'stage':'templado',
					'lot_line_id':line.lot_line_id.id,
				}
			stage_obj.create(data)
			line.lot_line_id.is_used=True
			line.lot_line_id.templado=True
			#new code:
			line.lot_line_id.order_line_id.state = 'ended'

		self.state = 'done'
		self.update({'state':'done','user_out':self.env.uid,'date_out':fields.Datetime.now()})
		return True



class GlassFurnaceLineOut(models.Model):
	_name='glass.furnace.line.out'

	#_rec_name="lot_line_id"

	main_id = fields.Many2one('glass.furnace.out')
	lot_id = fields.Many2one('glass.lot','Lote')
	lot_line_id = fields.Many2one('glass.lot.line',u'Línea de lote')
	order_number = fields.Integer(u'Nro. Orden')
	crystal_number = fields.Char('Nro. Cristal')
	base1 = fields.Integer("Base1 (L 4)")
	base2 = fields.Integer("Base2 (L 2)")
	altura1 = fields.Integer("Altura1 (L 1)")
	altura2 = fields.Integer("Altura2 (L 3)")
	area = fields.Float(u'Área M2',digits=(20,4))
	partner_id = fields.Many2one('res.partner',string='Cliente',)
	obra = fields.Char(string='Obra')
	etiqueta = fields.Boolean(string='Etiqueta')
	is_used = fields.Boolean(string='Usado', default=False)
	is_break = fields.Boolean(related='lot_line_id.is_break',string='Roto')