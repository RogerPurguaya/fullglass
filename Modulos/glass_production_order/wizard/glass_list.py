# -*- coding: utf-8 -*-

# from odoo import fields, models,api, _
# from odoo.exceptions import UserError
# from datetime import datetime

# class GlassListMainWizard(models.TransientModel):
# 	_name='glass.list.main.wizard'

# 	order_id = fields.Many2one('glass.order','Orden')
# 	lote_id = fields.Many2one('glass.lot','Lote')
# 	date_ini = fields.Date('Fecha Incio')
# 	date_end = fields.Date('Fecha Fin')

# 	@api.multi
# 	def makelist(self):
# 		self.ensure_one()
# 		lin = self.env['glass.list.wizard'].search([])
# 		for l in lin:
# 			l.unlink()

# 		orders1=[]
# 		if self.order_id:
# 			orders1 = [self.order_id.id]
# 		else:
# 			if self.lote_id:
# 				orders1=[]
# 				for line in self.lote_id.line_ids:
# 					if line.order_prod_id.id not in orders1:
# 						orders1.append(line.order_prod_id.id)
# 		if len(orders1)>0:
# 			orders = self.env['glass.order'].browse(orders1)
# 		else:
# 			orders = self.env['glass.order'].search([('date_order','>=',self.date_ini),('date_order','<=',self.date_end)])
# 		for order in orders:
# 			for line in order.line_ids:
# 				corte=False
# 				pulido=False
# 				entalle=False
# 				lavado=False
# 				templado=False
# 				insulado=False
# 				comprado=False
# 				entregado=False
# 				if line.lot_line_id:
# 					estados = self.env['glass.stage.record'].search([('lot_line_id','=',line.lot_line_id.id)])

# 					for estado in estados:
# 						if estado.stage== 'corte':
# 							corte = True
# 						if estado.stage== 'pulido':
# 							pulido= True
# 						if estado.stage== 'entalle':
# 							entalle= True
# 						if estado.stage== 'lavado':
# 							lavado= True
# 						if estado.stage== 'templado':
# 							templado= True
# 						if estado.stage== 'insulado':
# 							insulado= True
# 						if estado.stage== 'compra':
# 							comprado= True
# 						if estado.stage== 'entregado':
# 							entregado= True
# 				self.env['glass.list.wizard'].create({
# 					'order_id':order.id,
# 					'crysta_number':line.crystal_number,
# 					'base1':line.base1,
# 					'base2':line.base2,
# 					'altura1':line.altura1,
# 					'altura2':line.altura2,
# 					'descudre':line.descuadre,
# 					'nro_pagina':line.page_number,
# 					'optimizado':line.lot_line_id.optimizado if line.lot_line_id else False,
# 					'corte':corte,
# 					'pulido':pulido,
# 					'entalle':entalle,
# 					'lavado':lavado,
# 					'templado':templado,
# 					'insulado':insulado,
# 					'comprado':comprado,
# 					'entregado':entregado,
# 					'partner_id':order.partner_id.id,
# 					'estado':order.state,
# 					'glass_break':line.glass_break,
# 					'repos':line.glass_repo,
# 					'order_line':line.id,
# 					})
# 		view = self.env.ref('glass_production_order.view_glass_list_wizard_form')
# 		data = {
# 			'name': 'Seguimiento de Producción',
# 			'view_type': 'form',
# 			'view_mode': 'tree',
# 			'res_model': 'glass.list.wizard',
# 			'view_id': view.id,
# 			'type': 'ir.actions.act_window',
# 			'target': 'current',
# 		} 
# 		return data


# class GlassListWizard(models.TransientModel):
# 	_name='glass.list.wizard'


# 	order_id = fields.Many2one('glass.order','Orden producción')
# 	crysta_number = fields.Integer('Nro. cristal')
# 	base1=fields.Float('Base1',digist=(12,2))
# 	base2=fields.Float('Base2',digist=(12,2))
# 	altura1=fields.Float('Altura1',digist=(12,2))
# 	altura2=fields.Float('Altura2',digist=(12,2))
# 	descudre=fields.Char('Descuadre')
# 	nro_pagina=fields.Char('Nro. página')
# 	optimizado=fields.Boolean('Optimizado') 
# 	corte=fields.Boolean('Corte')
# 	pulido=fields.Boolean('Pulido')
# 	entalle=fields.Boolean('Entalle')
# 	lavado=fields.Boolean('Lavado') 
# 	templado=fields.Boolean('Templado')
# 	insulado=fields.Boolean('Insulado') 
# 	comprado=fields.Boolean('Comprado') 
# 	entregado=fields.Boolean('Entregado') 
# 	glass_break=fields.Boolean("Roto")
# 	repos=fields.Boolean(u"Reposición")
# 	partner_id = fields.Many2one('res.partner','Cliente')
# 	estado = fields.Selection([('draft','Generada'),('confirmed','Emitida'),('process','En Proceso'),('ended','Finalizada'),('delivered','Despachada')], 'Estado')
# 	order_line = fields.Many2one('glass.order.line','Lineapedido')

# class GlassReposWizard(models.TransientModel):
# 	_name='glass.respos.wizard'

# 	motive = fields.Selection([
# 		('eentalle','Error entalle'), 
# 		('emedida','Error medidas'), 
# 		('vrayado','Vidrio rayado'), 
# 		('vroto','Vidrio roto'), 
# 		('planimetria','Planimetria'), 
# 		('eventas','Error ventas'), 
# 		('mprima','Materia prima')])
# 	stage = fields.Selection([
# 		('corte','Corte'), 
# 		('pulido','Pulido'), 
# 		('entalle','Entalle'), 
# 		('lavado','Lavado'), 
# 		('templado','Templado'),
# 		('insulado','Insulado'),
# 		('produccion',u'Producción')],'Etapa') 

# 	@api.one
# 	def makerepo(self):
# 		active_ids = self._context['active_ids']
# 		lines = self.env['glass.list.wizard'].browse(active_ids)
# 		for line in lines:
# 			line.order_line.glass_break=True
# 			line.order_line.lot_line_id=False
# 			line.order_line.is_used=False

