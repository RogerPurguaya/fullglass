from odoo import api, fields, models,exceptions
from datetime import datetime

class RequisitionMaterial(models.Model):
	_name = 'requisition.material'

	date = fields.Date(string='Fecha', default=datetime.now().date())
	config_id = fields.Many2one('glass.order.config',string='Config')
	product_id = fields.Many2one('product.product',string='Producto')
	type_operation = fields.Selection([('raw_materials','Materias Primas'),('pieces','Retazos'),('return_pieces','Devolucion de Retazos')])
	materials_ids = fields.Many2many('product.product','req_material_product_rel','requisition_material_id','product_id')


	@api.constrains('product_id')
	def _verify_product_not_in_other_req_material(self):
		for record in self:
			exists = self.env['requisition.material'].search([('product_id','=',record.product_id.id),('type_operation','=',record.type_operation)])
			if len(exists) > 1:
				type_op = dict(self._fields['type_operation'].selection).get(record.type_operation)
				raise exceptions.Warning('Ya existe una Requisicion de Materiales para el producto: '+record.product_id.name+'\n con la operacion: '+type_op)



class ProductProduct(models.Model):
	_inherit = 'product.product'
	req_materials_ids = fields.Many2many('requisition.material','req_material_product_rel','product_id','requisition_material_id')
	uom_name = fields.Char(related='uom_id.name',string='Unidad de Medida')
