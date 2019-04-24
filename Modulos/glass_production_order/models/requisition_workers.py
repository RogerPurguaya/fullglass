from odoo import api, fields, models,exceptions

# Materias primas: 
class RequisicionMaterialWorker(models.Model):
	_name = 'requisition.worker.material'
	requisition_id = fields.Many2one('glass.requisition',string='Req.')
	product_id = fields.Many2one('product.product',string='Producto')
	quantity = fields.Integer('Cantidad')

	@api.constrains('quantity')
	def _verify_quantity(self):
		for record in self:
			if record.quantity <= 0:
				raise exceptions.Warning(u'La cantidad ('+str(record.quantity)+') ingresada no es valida\nIngrese una cantidad mayor a 0.')

class RequisicionMaterialWorkerWizard(models.TransientModel):
	_name = 'requisition.worker.material.wizard'
	requisition_id = fields.Many2one('glass.requisition',string='Req.')
	lines_ids = fields.One2many('requisition.worker.wizard.line','material_id')

	@api.multi
	def add_items(self):
		lines = self.lines_ids.filtered(lambda x: x.quantity > 0)
		if len(lines) == 0:
			raise exceptions.Warning('No ha establecido cantidad para ningun producto o la cantidad ingresada es invalida')
		
		exist = lines.filtered(lambda x: x.product_id.id in self.requisition_id.raw_materials.mapped('product_id').ids)
		if len(exist) > 0:
			msg=''
			for line in exist:
				msg+='-> ' + line.product_id.name+'\n'
			raise exceptions.Warning('Los siguiente productos ya se encuentran en la lista de materias primas:\n'+msg)

		for item in lines:
			worker = self.env['requisition.worker.material'].create({
				'requisition_id':self.requisition_id.id,
				'product_id':item.product_id.id,
				'quantity':item.quantity,
			})
		return True

# Retazos:
class RequisicionScrapsWorker(models.Model):
	_name = 'requisition.worker.scraps'
	requisition_id = fields.Many2one('glass.requisition',string='Req.')
	product_id = fields.Many2one('product.product',string='Producto')
	quantity = fields.Integer('Cantidad')
	width = fields.Integer('Ancho') # para retazos
	height = fields.Integer('Alto') # para retazos

	@api.constrains('quantity')
	def _verify_quantity(self):
		for record in self:
			if record.quantity <= 0:
				raise exceptions.Warning(u'La cantidad ('+str(record.quantity)+') ingresada no es valida\nIngrese una cantidad mayor a 0.')


class RequisicionScrapsWorkerWizard(models.TransientModel):
	_name = 'requisition.worker.scraps.wizard'
	requisition_id = fields.Many2one('glass.requisition',string='Req.')
	lines_ids = fields.One2many('requisition.worker.wizard.line','scraps_id')

	@api.multi
	def add_items(self):
		lines = self.lines_ids.filtered(lambda x: x.quantity > 0)
		if len(lines) == 0:
			raise exceptions.Warning('No ha establecido cantidad para ningun producto o la cantidad ingresada es invalida')
		
		exist = lines.filtered(lambda x: x.product_id.id in self.requisition_id.scraps.mapped('product_id').ids)
		if len(exist) > 0:
			msg=''
			for line in exist:
				msg+='-> ' + line.product_id.name+'\n'
			raise exceptions.Warning('Los siguiente productos ya se encuentran en la lista de Retazos:\n'+msg)

		for item in lines:
			worker = self.env['requisition.worker.scraps'].create({
				'requisition_id':self.requisition_id.id,
				'product_id':item.product_id.id,
				'quantity':item.quantity,
				'width':item.width,
				'height':item.height,
			})
		return True

# Devolucion de Retazos:
class RequisicionWorkerScrapsReturn(models.Model):
	_name = 'requisition.worker.scraps.return'
	requisition_id = fields.Many2one('glass.requisition',string='Req.')
	product_id = fields.Many2one('product.product',string='Producto')
	quantity = fields.Integer('Cantidad')
	width = fields.Integer('Ancho') # para retazos
	height = fields.Integer('Alto') # para retazos

	@api.constrains('quantity')
	def _verify_quantity(self):
		for record in self:
			if record.quantity <= 0:
				raise exceptions.Warning(u'La cantidad ('+str(record.quantity)+') ingresada no es valida\nIngrese una cantidad mayor a 0.')
	
	@api.constrains('width','height')
	def _verify_measures(self):
		for record in self:
			if record.width <= 0 or record.height <= 0:
				raise exceptions.Warning(u'Las medidas ('+str(record.width)+'X'+str(record.height)+') ingresadas no son validas\nIngrese cantidades mayores a 0.')


class RequisicionWorkerScrapsReturnWizard(models.TransientModel):
	_name = 'requisition.worker.scraps.return.wizard'
	requisition_id = fields.Many2one('glass.requisition',string='Req.')
	lines_ids = fields.One2many('requisition.worker.wizard.line','scraps_return_id')

	@api.multi
	def add_items(self):
		lines = self.lines_ids.filtered(lambda x: x.quantity > 0 and x.width > 0 and x.height > 0)
		if len(lines) == 0:
			raise exceptions.Warning('No ha establecido cantidad/ancho/alto para ningun producto o las cantidades ingresadas no son validas')
		
		exist = lines.filtered(lambda x: x.product_id.id in self.requisition_id.return_scraps.mapped('product_id').ids)
		if len(exist) > 0:
			msg=''
			for line in exist:
				msg+='-> ' + line.product_id.name+'\n'
			raise exceptions.Warning('Los siguiente productos ya se encuentran en la lista de Retazos a Devolver:\n'+msg)

		for item in lines:
			worker = self.env['requisition.worker.scraps.return'].create({
				'requisition_id':self.requisition_id.id,
				'product_id':item.product_id.id,
				'quantity':item.quantity,
				'width':item.width,
				'height':item.height,
			})
		return True

# modelo reutilizable para los 3 tipos de operacion (mat primas, retazos y dev. retazos)
class RequisicionWorkerWizardLine(models.TransientModel):
	_name = 'requisition.worker.wizard.line'
	material_id = fields.Many2one('requisition.worker.material.wizard')
	scraps_id = fields.Many2one('requisition.worker.scraps.wizard')
	scraps_return_id = fields.Many2one('requisition.worker.scraps.return.wizard')
	product_id = fields.Many2one('product.product',string='Producto')
	quantity = fields.Integer('Cantidad')
	width = fields.Integer('Ancho') # para retazos
	height = fields.Integer('Alto') # para retazos

class ProductTemplate(models.Model):
	_inherit = 'product.template'
	retazo = fields.Boolean('Es Retazo') # campoa para productos retazo 

class ProductProduct(models.Model):
	_inherit = 'product.product'
	retazo = fields.Boolean(related='product_tmpl_id.retazo') # campoa para productos retazo 

