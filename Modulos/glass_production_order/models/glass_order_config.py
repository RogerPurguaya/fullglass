# -*- coding: utf-8 -*-

from odoo import fields, models,api,exceptions, _
from odoo.exceptions import UserError

class GlassOrderConfig(models.Model):
	_name = 'glass.order.config'
	name = fields.Char(u'Parámetros',default=u"Parámetros")
	seq_order=fields.Many2one('ir.sequence',u'Secuencia para las ódenes de produccion')
	seq_lot=fields.Many2one('ir.sequence',u'Secuencia para los lotes')
	
	optimization_ext = fields.Char(u'Extención')
	optimization_path = fields.Char(u'Ruta de archivo exportado')
	# horno
	seq_furnace = fields.Many2one('ir.sequence',u'Secuencia lote de horno')
	furnace_area = fields.Float(u'Área de Horno (M2)',digist=(12,4))
	seq_furnace_out = fields.Many2one('ir.sequence',u'Secuencia lote salida de horno')
	# ordenrequisicion
	seq_requisi = fields.Many2one('ir.sequence',u'Secuencia Orden de Requisición')
	picking_type_pt = fields.Many2one('stock.picking.type',u'Operación producto terminado')
	traslate_motive_pt = fields.Many2one('einvoice.catalog.12','Motivo traslado producto terminado')

	picking_type_mp = fields.Many2one('stock.picking.type',u'Operación consumo materia prima ')
	picking_type_rt = fields.Many2one('stock.picking.type',u'Operación consumo retazos')
	picking_type_drt = fields.Many2one('stock.picking.type',u'Operación devolución retazos')
	picking_type_pr = fields.Many2one('stock.picking.type',u'Operación producción')

	traslate_motive_mp = fields.Many2one('einvoice.catalog.12','Motivo traslado consumo materia prima ')
	traslate_motive_rt = fields.Many2one('einvoice.catalog.12','Motivo traslado consumo retazos')
	traslate_motive_drt = fields.Many2one('einvoice.catalog.12',u'Motivo traslado devolución retazos')
	traslate_motive_pr = fields.Many2one('einvoice.catalog.12',u'Motivo traslado  producción')
	limit_ids=fields.One2many('glass.production.limit','config_id','Plazos de Producción')

	userstage = fields.One2many('glass.production.user.stage','config_id','Usuarios - Etapas')

	dateexceptions_ids = fields.One2many('glass.date.exception','config_id','Fechas excluidas')

	uom_categ_id = fields.Many2one('product.uom.categ', string=u'Categoría de unidad por defecto')

	nro_cristales_guia = fields.Integer(string='Nro. de Cristales por guia', default=100)
	compare_attribute = fields.Many2one('product.atributo',string=u'Atributo de Comparación')

	motive_event_send_email_ids = fields.One2many('motive.event.send.email','config_id',string='Motivos de Envio de Emails')

	requisition_materials_ids = fields.One2many('requisition.material','config_id',string='Materiales de Requisicion')
	
	categ_uom_retazo = fields.Many2one('product.uom.categ')

	path_glass_order_pdf = fields.Char(string='Ruta de GlassOrder Pdf')
	path_glass_lines_pdf = fields.Char(string='Ruta de GlassOrderLine Pdf')
	 	
	@api.constrains('nro_cristales_guia')
	def _verify_nro_cristales(self):
		for record in self:
			if record.nro_cristales_guia < 1:
				raise exceptions.ValidationError('Valor Incorrecto:\nEl Numero de cristales por guia dede ser mayor a 0')

	@api.multi
	def execute_script(self):
		lines = self.env['glass.pdf.file'].search([('pdf_file','!=',False)])
		from datetime import datetime
		import base64
		sub_items = [lines[i:i+100] for i in range(0,len(lines),100)]
		for array in sub_items:
			for item in array:
				print('line in:', str(item.id))
				path = self.path_glass_order_pdf
				file, pdf = None,None
				if item.op_id:
					name = 'order_'+item.op_id.name+'_'+ str(datetime.now()).replace(':','').replace(' ','_').replace('-','_')+'.pdf'
					path += name
					file = open(path,'wb')
					pdf = item.op_id.sketch if item.op_id.sketch else item.pdf_file
					file.write(base64.b64decode(pdf))
					file.close()
					item.op_id.write({'croquis_path':path})
					item.write({'path_pdf':path})
				else:
					if not item.sale_id:
						continue
					name = 'order_'+item.sale_id.name+'_'+ str(datetime.now()).replace(':','').replace(' ','_').replace('-','_')+'.pdf'
					path += name
					file = open(path,'wb')
					file.write(base64.b64decode(item.pdf_file))
					file.close()
					item.write({'path_pdf':path})
				print('line path:', str(item.id)+item.path_pdf)
		print('enjoy!')


class GlassProductionLimit(models.Model):
	_name="glass.production.limit"

	config_id = fields.Many2one('glass.order.config','main_id')

	motive_limit = fields.Selection([
		('templado','Templado'),
		('laminado','Laminado'),
		('insulado','Insulado'),
		('cmetalica',u'C. Metálica'),
		('pac','PAC'),
		('crudo','Crudo'),
		],'Detalle')
	piezas = fields.Integer(u'Reposición Piezas')
	zero_2_50 = fields.Integer('0-50m2')
	fiftyone_2_100 = fields.Integer('51-100m2')
	onehundred1_2_200 = fields.Integer('101-200m2')
	more_2_200 = fields.Integer('+200m2')
	obras = fields.Integer('Obras')
	entalle = fields.Integer('Entalle')
	local_send = fields.Integer('Entrega AQP')
	external_send = fields.Integer('Embalaje y Transporte a Lima')
	send2partner= fields.Integer('Entrega Lima')

class GlassProductionUserStage(models.Model):
	_name="glass.production.user.stage"

	user_id = fields.Many2one('res.users','Usuario')
	stage = fields.Selection([('corte','Corte'),('pulido','Pulido'),('entalle','Entalle'),('lavado','Lavado')],'Etapa')
	config_id = fields.Many2one('glass.order.config','Mainid')
	order_prod = fields.Integer('Orden de Proceso')


class GlassDateException(models.Model):
	_name="glass.date.exception"

	date = fields.Date('Fecha Excluida')
	config_id = fields.Many2one('glass.order.config','Mainid')


