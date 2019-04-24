from odoo import api, fields, models, exceptions
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta
import base64

class AddSketchFile(models.TransientModel):
	_name = 'add.sketch.file'
	sketch = fields.Binary(string='Croquis')
	file_name = fields.Char('')
	message = fields.Char('Message')
		
	@api.multi
	def preview(self):
		return  {"type": "ir.actions.do_nothing",}
	
	@api.multi
	def add_file(self):
		if not self.sketch:
			raise UserError('No ha seleccionado ningun archivo')
		try:
			conf = self.env['glass.order.config'].search([])[0]
		except IndexError as e:
			raise UserError(u'No se ha encontrado la configuracion para almacenar ficheros Pdf.')
		
		path = conf.path_glass_order_pdf
		order = self.env['sale.order'].browse(self._context['active_id'])
		name = 'order_'+order.name+'_'+ str(datetime.now()).replace(':','').replace(' ','_').replace('-','_')+'.pdf' # timestamp para generar nombre unico
		path += name
		file = open(path,'wb')
		file.write(base64.b64decode(self.sketch))
		file.close()
		line = self.env['glass.pdf.file'].create({
			'file_name':self.file_name,
			'pdf_name':self.file_name,
			'path_pdf':path,
			'sale_id':order.id,
		})
		return True


	@api.multi
	def change_file(self):
		if not self.sketch:
			raise UserError('No ha seleccionado ningun archivo')
		try:
			conf = self.env['glass.order.config'].search([])[0]
		except IndexError as e:
			raise UserError(u'No se ha encontrado la configuracion para almacenar ficheros Pdf.')
		
		path = conf.path_glass_order_pdf
		order = self.env['glass.order'].browse(self._context['active_id'])
		name = 'order_'+order.name+'_'+ str(datetime.now()).replace(':','').replace(' ','_').replace('-','_')+'.pdf' # timestamp para generar nombre unico
		path += name
		file = open(path,'wb')
		file.write(base64.b64decode(self.sketch))
		file.close()

		old_path = order.croquis_path

		order.write({'croquis_path':path})
		obj_pdf = self.env['glass.pdf.file'].search([('op_id','=',order.id)])
		if len(obj_pdf) == 1:
			obj_pdf[0].write({'path_pdf':path})
		
		# limpiar el anterior:
		import os
		if old_path and os.path.exists(old_path):
			os.remove(old_path)
		else:
			print('Path file does not exist !')	
		return True