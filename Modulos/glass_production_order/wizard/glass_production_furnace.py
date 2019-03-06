# -*- coding: utf-8 -*-

""" Funcionalidad antigua que ya no se usa 14/02/2019 """

# from odoo import fields, models,api, _
# from odoo.exceptions import UserError
# from datetime import datetime

# class GlassProductionFurnaceWizard(models.TransientModel):
# 	_name='glass.productionfurnace.wizard'

# 	name = fields.Char('Lote de Horno')
# 	search_code = fields.Char('Producto')
# 	line_ids=fields.One2many('glass.productionfurnace.line.wizard','mainwizard_id','Detalle')
# 	cad3 = fields.Char('cad3',default='')
# 	used_area = fields.Float('Area M2',digits=(20,4))
# 	used_rest = fields.Float('Area por Utilizar',digits=(20,4))
# 	percent_use = fields.Float('% de eficiencia',digits=(20,4))
# 	user_ingreso = fields.Many2one('res.users','Usuario')
# 	date_ingreso=fields.Datetime('Fecha')
# 	message_erro = fields.Char('*',default='')

# 	@api.multi
# 	def get_wizard(self):

# 		view = self.env.ref("glass_production_order.view_glass_productionfurnace_wizard_form",False)
# 		wizard = self.env['glass.productionfurnace.wizard'].create({})
# 		retornable = {
# 			'res_id':wizard.id,
# 			'name':'Ingreso a Horno',
# 			'type': 'ir.actions.act_window',
# 			'res_model': 'glass.productionfurnace.wizard',
# 			'view_mode': 'form',
# 			'view_type': 'form',
# 			'views': [(view.id, 'form')],
# 			'target': 'new',
# 		}

# 		return retornable

# 	@api.model
# 	def default_get(self, fields_Act):
# 		res = super(GlassProductionFurnaceWizard,self).default_get(fields_Act)
# 		config_data = self.env['glass.order.config'].search([])
# 		if len(config_data)==0:
# 			raise UserError(u'No se encontraron los valores de configuración de producción')		
# 		config_data = self.env['glass.order.config'].search([])[0]

# 		res.update( {
# 			'name':config_data.seq_furnace.number_next_actual,
# 			'user_ingreso':self.env.uid,
# 			'date_ingreso':fields.Datetime.now(),
# 		})
# 		return res

# 	@api.onchange('search_code')
# 	def onchangecode(self):
# 		idsact = []
# 		config_data = self.env['glass.order.config'].search([])
# 		if len(config_data)==0:
# 			raise UserError(u'No se encontraron los valores de configuración de producción')		
# 		config_data = self.env['glass.order.config'].search([])[0]
# 		if self.search_code:
# 			existe = self.env['glass.lot.line'].search([('search_code','=',self.search_code)])
# 			self.message_erro=""
# 			for line in self.line_ids:
# 				idsact.append(line.id)

# 			if len(existe)>0:
# 				stage_obj = self.env['glass.stage.record']
# 				ext = stage_obj.search([('stage','=','templado'),('lot_line_id','=',existe.id)])
# 				if len(ext)>0:
# 					self.message_erro="El cristal seleccionado ya fue registrado en la etapa Templado"
# 					self.search_code=""
# 					return


# 				existe_act = existe[0]
# 				pasoentalle = stage_obj.search([('stage','=','lavado'),('lot_line_id','=',existe_act.id)])
# 				cuenta =0
# 				for line in self.line_ids:
# 					if line.lot_line_id.id==existe_act.id:
# 						#print line.lot_line_id.id,existe_act.id
# 						cuenta = cuenta +1
# 				if cuenta>0:
# 					self.message_erro="El cristal seleccionado ya fue registrado en este ingreso a horno"
# 					self.search_code=""
# 					return						
# 				if len(pasoentalle)>0:
# 					ordern = len(self.line_ids)+1
# 					data = {
# 						'mainwizard_id':self.id,
# 						'order_number':ordern,
# 						'lot_id':existe_act.lot_id.id,
# 						'lot_line_id':existe_act.id,
# 						'crystal_number':existe_act.nro_cristal,
# 						'base1':existe_act.base1,
# 						'base2':existe_act.base2,
# 						'altura1':existe_act.altura1,
# 						'altura2':existe_act.altura2,
# 						'area':existe_act.area,
# 						'partner_id':existe_act.order_prod_id.partner_id.id,
# 						'obra':existe_act.order_prod_id.obra,
# 					}
# 					t=self.env['glass.productionfurnace.line.wizard'].create(data)
# 					idsact.append(t.id)
# 					if self.cad3:
# 						self.cad3=self.cad3+str(t.id)+','
# 					else:
# 						self.cad3=str(t.id)+','
					
					
# 				else:
# 					self.message_erro="No se puede agregar un elemento que no tenga registrada la etapa LAVADO"
# 					self.search_code=""
# 					return
# 		self.write({'line_ids':[(6,0,idsact)]})
# 		self.search_code=''
# 		mylines=[]
# 		if self.cad3:
# 			mylines = self.cad3[:-1].split(',')
# 		llines=[]
# 		for l in mylines:
# 			llines.append(int(l))
# 		used_area=0
# 		used_rest=0
# 		for line in self.env['glass.productionfurnace.line.wizard'].browse(llines):
# 			used_area=used_area+line.area
		
# 		farea = config_data.furnace_area
# 		e_percent=0
# 		percent_use = 0
# 		if used_area>0:
# 			e_percent=farea-used_area
# 		percent_use=(used_area*100)/farea
		
# 		return {'value':{'line_ids':idsact,'used_area':used_area,'used_rest':e_percent,'percent_use':percent_use}}


# 	@api.one
# 	def save_furnace(self):
# 		stage_obj = self.env['glass.stage.record']
# 		config_data = self.env['glass.order.config'].search([])
# 		if len(config_data)==0:
# 			raise UserError(u'No se encontraron los valores de configuración de producción')		
# 		config_data = self.env['glass.order.config'].search([])[0]
# 		newname = config_data.seq_furnace.next_by_id()
# 		data = {
# 			'name':newname,
# 			'date_out':datetime.now(),
# 			'nro_crystal':0,
# 			'total_m2':0,
# 			'e_percent':0,
# 			'user_ingreso':self.env.uid,
# 			'date_ingreso':datetime.now(),
# 		}
# 		t=self.env['glass.furnace.out'].create(data)
# 		mylines = self.cad3[:-1].split(',')
# 		llines=[]
# 		for l in mylines:
# 			llines.append(int(l))
# 		area = 0
# 		qty =0
# 		for line in self.env['glass.productionfurnace.line.wizard'].browse(llines):
# 			pasoentalle = stage_obj.search([('stage','=','lavado'),('lot_line_id','=',line.lot_line_id.id)])
# 			if len(pasoentalle)==0:
# 				raise UserError(u'No se puede agregar un elemento que no tenga registrada la etapa LAVADO')		
# 			else:
# 				print 3
				
# 				data = {
# 					'main_id':t.id,
# 					'order_number':line.order_number,
# 					'lot_id':line.lot_id.id,
# 					'lot_line_id':line.lot_line_id.id,
# 					'crystal_number':line.crystal_number,
# 					'base1':line.base1,
# 					'base2':line.base2,
# 					'altura1':line.altura1,
# 					'altura2':line.altura2,
# 					'area':line.area,
# 					'partner_id':line.partner_id.id,
# 					'obra':line.obra,
# 				}
# 				newid=self.env['glass.furnace.line.out'].create(data)
# 				area = area+line.area
# 				qty = qty+1
# 				data = {
# 					'user_id':self.env.uid,
# 					'date':datetime.now(),
# 					'time':datetime.now().time(),
# 					'stage':'horno',
# 					'lot_line_id':line.lot_line_id.id,
# 					'date_fisical':datetime.now(),
# 				}
# 				stage_obj = self.env['glass.stage.record']
# 				stage_obj.create(data)
# 				line.lot_line_id.horno=True

				
				
# 		farea = config_data.furnace_area
# 		e_percent=0
# 		if area>0:
# 			e_percent=farea/area*100

# 		t.write({'area':area,'nro_crystal':qty,'e_percent':e_percent})
# 		return True


# class GlassProductionFurnaceLineWizard(models.TransientModel):
# 	_name='glass.productionfurnace.line.wizard'

# 	mainwizard_id = fields.Many2one('glass.productionfurnace.wizard')
# 	order_number = fields.Integer(u'Nro. Orden')
# 	crystal_number = fields.Char('Nro. Cristal')
# 	lot_id = fields.Many2one('glass.lot','Lote')
# 	lot_line_id = fields.Many2one('glass.lot.line',u'Línea de lote')
# 	base1 = fields.Integer("Base1 (L 4)")
# 	base2 = fields.Integer("Base2 (L 2)")
# 	altura1 = fields.Integer("Altura1 (L 1)")
# 	altura2 = fields.Integer("Altura2 (L 3)")
# 	area = fields.Float(u'Área M2',digits=(20,4))
# 	partner_id = fields.Many2one('res.partner',string='Cliente')
# 	obra = fields.Char(string='Obra')