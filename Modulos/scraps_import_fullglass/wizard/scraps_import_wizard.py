try:
	import cStringIO as StringIO
except ImportError:
	import StringIO
import base64
import csv
from datetime import datetime
from sys import exc_info
from traceback import format_exception

from odoo import models, fields, api, _
from odoo.exceptions import Warning

import logging
_logger = logging.getLogger(__name__)

class ScrapsItemImport(models.TransientModel):
	_name = 'sii.import'
	traslate_motive = fields.Many2one('einvoice.catalog.12', string='Motivo de Traslado')
	picking_type = fields.Many2one('stock.picking.type', string='Tipo de Picking')
	
	sii_data = fields.Binary(string='File', required=True)
	sii_fname = fields.Char(string='Filename')
	lines = fields.Binary(
		compute='_compute_lines', string='Input Lines', required=True)
	dialect = fields.Binary(
		compute='_compute_dialect', string='Dialect', required=True)
	csv_separator = fields.Selection(
		[(',', 'Coma (,)'), (';', 'Punto y coma (;)')],
		string='CSV Separator', required=True)
	decimal_separator = fields.Selection(
		[('.', 'Punto (.)'), (',', 'Coma (,)')],
		string='Decimal Separator',
		default='.', required=True)
	codepage = fields.Char(
		string='Code Page',
		default=lambda self: self._default_codepage(),
		help="Code Page of the system that has generated the csv file."
			 "\nE.g. Windows-1252, utf-8")
	note = fields.Text('Log')

	@api.multi
	def get_element(self):
		module = __name__.split('addons.')[1].split('.')[0]
		view = self.env.ref('%s.sii_import_view_form' % module)
		return {
			'name':'Importacion de Retazos',
			'type': 'ir.actions.act_window',
			'res_model': 'sii.import',
			'view_id': view.id,
			'view_mode': 'form',
			'view_type': 'form',
			'target': 'new',
		}
		
	def _input_fields(self):
		"""
		Extend this dictionary if you want to add support for
		fields requiring pre-processing before being added to
		the pricelist line values dict.
		"""
		return {}

	@api.multi
	def sii_import(self):
		self._err_log = '' # no usado 
		self._get_orm_fields() # no usado
		lines, header = self._remove_leading_lines(self.lines)
		header_fields = csv.reader(
			StringIO.StringIO(header), dialect=self.dialect).next()
		
		header_fields = self.traslate_header_fields(header_fields)
		self._header_fields = self._process_header(header_fields)
		reader = csv.DictReader(
			StringIO.StringIO(lines), fieldnames=self._header_fields,
			dialect=self.dialect)

		item_lines = []
		error_line = False
		for line in reader:
			line = self._process_line_vals(line)
			exist = list(filter(lambda x: x['product_id'] == line['product_id'] and x['width'] == line['width'] and x['height'] == line['height'],item_lines))
			if len(exist) == 1:
				raise Warning('Existen lineas con productos y medidas duplicadas:\n'+exist[0]['product_id']+' | '+str(exist[0]['width'])+' | '+str(exist[0]['height']))
			item_lines.append(line)


		picking = self.env['stock.picking'].create({
				'picking_type_id': self.picking_type.id,
				'partner_id': None,
				'date': datetime.now().date(),
				'fecha_kardex':datetime.now().date(),
				'location_dest_id': self.picking_type.default_location_dest_id.id,
				'location_id': self.picking_type.default_location_src_id.id,
				'company_id': self.env.user.company_id.id,
				'einvoice_12': self.traslate_motive.id,
			})

		for item in item_lines:
			products = self.env['product.product'].search([('name', '=', item['product_id'])])
			if len(products) == 0:
				raise Warning('Producto '+ item['product_id'] + ' no encontrado!')
			product = products.filtered(lambda x: x.uom_id.ancho == float(item['width']) and x.uom_id.alto == float(item['height']))
			new_prod = None
			if len(product) == 0:
				conf = self.env['glass.order.config'].search([])[0]
				base = products.filtered(lambda x: not x.retazo)[0]
				new_uom = self.env['product.uom'].create({
					'name':str(item['width'])+"x"+str(item['height'])+"mm - R",
					'uom_type':'reference',
					'is_retazo':True,
					'ancho':float(item['width']),
					'alto':float(item['height']),
					'category_id':conf.categ_uom_retazo.id,
					'rounding':0.00001,
				})
				attrs = []
				for attr in base.product_tmpl_id.atributo_ids:
					new = attr.copy()
					new.product_id = False
					attrs.append(new.id)

				new_tmpl = self.env['product.template'].create({
					'codigo_inicial':base.codigo_inicial.id,
					'categ_id':base.categ_id.id,
					'name':'',
					'sale_ok':False,
					'purchase_ok':False,
					'type':'product',
					'uom_id': new_uom.id,
					'list_price':False,
					'optima_trim': base.optima_trim,
					'retazo':True,
					'uom_po_id':new_uom.id,
					'atributo_ids':[(6,0,attrs)]
				})

				new_prod = self.env['product.product'].search([('product_tmpl_id','=',new_tmpl.id)])
			
			product = new_prod[0] if new_prod else product[0]

			move = self.env['stock.move'].create({
				'name': product.name or '',
				'product_id': product.id,
				'product_uom': product.uom_id.id,
				'date': datetime.now().date(),
				'date_expected': datetime.now().date(),
				'location_dest_id':picking.location_dest_id.id,
				'location_id': picking.location_id.id,
				'picking_id': picking.id,
				'move_dest_id': False,
				'state': 'draft',
				'company_id': self.env.user.company_id.id,
				'picking_type_id': self.picking_type.id,
				'procurement_id': False,
				'route_ids': self.picking_type.warehouse_id and [(6, 0, [x.id for x in self.picking_type.warehouse_id.route_ids])] or [],
				'warehouse_id': self.picking_type.warehouse_id.id,
				'product_uom_qty': item['quantity'],
			})

		action = picking.do_new_transfer()
		context,bad_execution,motive = None,None,None
		if type(action) == type({}):
			if action['res_model'] == 'stock.immediate.transfer' or action['res_model'] == 'stock.backorder.confirmation':
				context = action['context']
				sit = self.env['stock.immediate.transfer'].with_context(context).create({'pick_id': picking.id})	
				try:
					sit.process()
				except UserError as e:
					bad_execution = picking.name
					motive = str(e)
		if bad_execution:
			raise UserError('No fue posible procesar los siguiente Picking: '+bad_execution+'\nPosible causa: '+motive)

		return {
			'name':picking.name,
			'res_id':picking.id,
			'type': 'ir.actions.act_window',
			'res_model': 'stock.picking',
			'view_mode': 'form',
			'view_type': 'form',
		}
		#return {'type': 'ir.actions.act_window_close'}


#### other methods
	def _process_line_vals(self, line):
		a,b,c = line['quantity'],line['width'],line['height']
		if None in list(line.values()):
			raise Warning('Una  o varias lineas no tienen todos los valores requeridos:\n (Producto,Cantidad,Ancho,Alto)')
		if a <= 0 or  b <= 0 or c <= 0:
			raise Warning('Una  o varias lineas tienen valores no validos (0 o valor negativo)')
		if type(line['product_id']) != type('') or len(line['product_id']) == 0:
			raise Warning('El valor del Campo producto esta vacio o tiene un valor invalido')
		return line
	
	def traslate_header_fields(self,header_fields):
		dic_values = {
			'producto':'product_id',
			'cantidad':'quantity',
			'ancho':'width',
			'alto':'height',
		}

		for i,header in enumerate(header_fields):
			if header in dic_values:
				header_fields[i] = dic_values[header]
		return header_fields


	def _get_orm_fields(self):
		sii_mod = self.env['product.pricelist.item']
		orm_fields = sii_mod.fields_get()
		blacklist = models.MAGIC_COLUMNS + [sii_mod.CONCURRENCY_CHECK_FIELD]
		self._orm_fields = {
			f: orm_fields[f] for f in orm_fields
			if f not in blacklist
			and not orm_fields[f].get('depends')}


	def _process_header(self, header_fields):

		self._field_methods = self._input_fields()
		self._skip_fields = []

		# header fields after blank column are considered as comments
		column_cnt = 0

		for cnt in range(len(header_fields)):
			if header_fields[cnt] == '':
				column_cnt = cnt
				break
			elif cnt == len(header_fields) - 1:
				column_cnt = cnt + 1
				break
		header_fields = header_fields[:column_cnt]

		# check for duplicate header fields
		header_fields2 = []
		for hf in header_fields:
			if hf in header_fields2:
				raise Warning(_(
					"Duplicate header field '%s' found !"
					"\nPlease correct the input file.")
					% hf)
			else:
				header_fields2.append(hf)

		for i, hf in enumerate(header_fields):

			if hf in self._field_methods:
				continue

			if hf not in self._orm_fields \
					and hf not in [self._orm_fields[f]['string'].lower()
								   for f in self._orm_fields]:
				_logger.error(
					_("%s, undefined field '%s' found "
					  "while importing move lines"),
					self._name, hf)
				self._skip_fields.append(hf)
				continue

			field_def = self._orm_fields.get(hf)
			if not field_def:
				for f in self._orm_fields:
					if self._orm_fields[f]['string'].lower() == hf:
						orm_field = f
						field_def = self._orm_fields.get(f)
						break
			else:
				orm_field = hf
			field_type = field_def['type']

			if field_type in ['char', 'text']:
				self._field_methods[hf] = {
					'method': self._handle_orm_char,
					'orm_field': orm_field,
					}
			elif field_type == 'integer':
				self._field_methods[hf] = {
					'method': self._handle_orm_integer,
					'orm_field': orm_field,
					}
			elif field_type == 'float':
				self._field_methods[hf] = {
					'method': self._handle_orm_float,
					'orm_field': orm_field,
					}
			elif field_type == 'many2one':
				self._field_methods[hf] = {
					'method': self._handle_orm_many2one,
					'orm_field': orm_field,
					}
			else:
				_logger.error(
					_("%s, the import of ORM fields of type '%s' "
					  "is not supported"),
					self._name, hf, field_type)
				self._skip_fields.append(hf)

		return header_fields

	def _log_line_error(self, line, msg):
		data = self.csv_separator.join(
			[line[hf] for hf in self._header_fields])
		self._err_log += _(
			"Error when processing line '%s'") % data + ':\n' + msg + '\n\n'

	def _handle_orm_char(self, field, line, pricelist, sii_vals,
						 orm_field=False):
		orm_field = orm_field or field
		if not sii_vals.get(orm_field):
			sii_vals[orm_field] = line[field]

	def _handle_orm_integer(self, field, line, pricelist, sii_vals,
							orm_field=False):
		orm_field = orm_field or field
		if not sii_vals.get(orm_field):
			val = str2int(
				line[field], self.decimal_separator)
			if val is False:
				msg = _(
					"Incorrect value '%s' "
					"for field '%s' of type Integer !"
					) % (line[field], field)
				self._log_line_error(line, msg)
			else:
				sii_vals[orm_field] = val

	def _handle_orm_float(self, field, line, pricelist, sii_vals,
						  orm_field=False):
		orm_field = orm_field or field
		if not sii_vals.get(orm_field):
			sii_vals[orm_field] = str2float(
				line[field], self.decimal_separator)

			val = str2float(
				line[field], self.decimal_separator)
			if val is False:
				msg = _(
					"Incorrect value '%s' "
					"for field '%s' of type Numeric !"
					) % (line[field], field)
				self._log_line_error(line, msg)
			else:
				sii_vals[orm_field] = val

	def _handle_orm_many2one(self, field, line, pricelist, sii_vals,
							 orm_field=False):
		orm_field = orm_field or field
		if not sii_vals.get(orm_field):
			val = str2int(
				line[field], self.decimal_separator)
			if val is False:
				msg = _(
					"Incorrect value '%s' "
					"for field '%s' of type Many2One !"
					"\nYou should specify the database key "
					"or contact your IT department "
					"to add support for this field."
					) % (line[field], field)
				self._log_line_error(line, msg)
			else:
				sii_vals[orm_field] = val

	@api.model
	def _default_codepage(self):
		return 'Windows-1252'

	@api.one
	@api.depends('sii_data')
	def _compute_lines(self):
		if self.sii_data:
			self.lines = base64.decodestring(self.sii_data)

	@api.one
	@api.depends('lines', 'csv_separator')
	def _compute_dialect(self):
		if self.lines:
			try:
				self.dialect = csv.Sniffer().sniff(
					self.lines[:128], delimiters=';,')
			except:
				# csv.Sniffer is not always reliable
				# in the detection of the delimiter
				self.dialect = csv.Sniffer().sniff(
					'"header 1";"header 2";\r\n')
				if ',' in self.lines[128]:
					self.dialect.delimiter = ','
				elif ';' in self.lines[128]:
					self.dialect.delimiter = ';'
		if self.csv_separator:
			self.dialect.delimiter = str(self.csv_separator)

	@api.onchange('sii_data')
	def _onchange_sii_data(self):
		if self.lines:
			self.csv_separator = self.dialect.delimiter
			if self.csv_separator == ';':
				self.decimal_separator = ','

	@api.onchange('csv_separator')
	def _onchange_csv_separator(self):
		if self.csv_separator and self.sii_data:
			self.dialect.delimiter = self.csv_separator

	def _remove_leading_lines(self, lines):
		""" remove leading blank or comment lines """
		input = StringIO.StringIO(lines)
		header = False
		while not header:
			ln = input.next()
			if not ln or ln and ln[0] in [self.csv_separator, '#']:
				continue
			else:
				header = ln.lower()
		if not header:
			raise Warning(
				_("No header line found in the input file !"))
		output = input.read()
		return output, header

def str2float(amount, decimal_separator):
	if not amount:
		return 0.0
	try:
		if decimal_separator == '.':
			return float(amount.replace(',', ''))
		else:
			return float(amount.replace('.', '').replace(',', '.'))
	except:
		return False


def str2int(amount, decimal_separator):
	if not amount:
		return 0
	try:
		if decimal_separator == '.':
			return int(amount.replace(',', ''))
		else:
			return int(amount.replace('.', '').replace(',', '.'))
	except:
		return False
