# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import base64,decimal
import sys
from odoo.exceptions import UserError
import pprint
from odoo.exceptions import ValidationError

class Stock_Picking(models.Model):
	_inherit = 'stock.picking'

	@api.multi
	def get_preview_remission_guide(self):
		if self.picking_type_id.code != 'internal':
			partner_id = self.partner_id
		else:
			try:
				partner_id = self.env['res.company'].search([])[0].partner_id
			except IndexError as e:
				print('Error: ', e)
				raise exceptions.UserError('No hay una compania configurada')

		if partner_id.street == False or partner_id.nro_documento == False:
			raise exceptions.UserError(_('El cliente no tiene direccion o Nro Documento'))

		if self.numberg == False:
			raise exceptions.UserError(_(u'No se ha establecido un numero de guia'))
		
		partida = self.picking_type_id.warehouse_id.partner_id.street
		if self.punto_partida:
			partida = self.punto_partida

		street_partner = ''
		if partner_id:
			street_partner = partner_id.street
		if self.picking_type_id.code == 'internal':
			warehouse = self.location_dest_id.location_id.get_warehouse()
			street_partner = warehouse.partner_id.street if warehouse.partner_id.street else ''
		if self.punto_llegada:
			street_partner = self.punto_llegada


		# new code 
		# si los move_lines tienen glass_order_line_ids ejecutan print_details_move
		data = None
		out = 0
		for move in self.move_lines:
			if len(move.glass_order_line_ids) > 0:
				out += 1
		if out == len(self.move_lines):
			data = self._get_data(self.move_lines)
		else:
			data = self._get_data_for_internal(self.move_lines)
		# end new code

		vals = {
		'date':self.fecha_kardex if self.fecha_kardex else '',
		'reference':self.invoice_id.reference if self.invoice_id.reference else '',
		'partner':partner_id.name,
		'nro_doc':partner_id.nro_documento,
		'direction':partner_id.street,
		'phone': partner_id.phone if partner_id.phone else '',
		'transporter':self.nombre if self.nombre else 'EL MISMO',
		'ruc': self.ruc if self.ruc else '',
		'start_point':partida,
		'end_point':street_partner,
		'mode':'',
		'data':data,
		}

		view = self.env.ref('show_preview_of_remission_guide.view_remission_guide_wizard_form',False)
		wizard = self.env['preview.remission.guide.wizard'].create(vals)
		return {
			'name':'Previsualizar guia de remision',
			'res_id':wizard.id,
			'res_model':'preview.remission.guide.wizard',
			'view_mode':'form',
			'view_id':view.id,
			'type': 'ir.actions.act_window',
			'target':'new',
		}

	def _get_data(self,move_lines):
		cont = 1
		acum_weight = 0
		total_weight = 0
		container = []
		datita = 'ITEM'+10*' '+'CODIGO'+14*' '+'CANTIDAD'+7*' '+'UNIT.'+15*' '+'DESCRIPCION ARTICULOS\n' 
		for move in move_lines:
			nombre = move.product_id.name
			detail_lines = move.glass_order_line_ids
			for detail in detail_lines:
				show_data = str(detail.order_id.name)+'-'+str(detail.crystal_number)+ '(' +self._process_measures_item(detail.base1,detail.base2,detail.altura1,detail.altura2) + ')'
				acum_weight += detail.peso
				container.append(show_data)

			acum_weight = '{:,.2f}'.format(decimal.Decimal ("%0.2f" %  acum_weight))
			nombre += ' ('+str(len(detail_lines))+' Pzs)'
			data = [cont,move.product_id.default_code or '',move.product_uom_qty,move.product_uom.name,nombre]
			
			datita += (12*' ').join(map(str,data))+'\n'
			container = [container[i:i+7] for i in range(0, len(container), 7)]
			for sub_array in container:
				sub_array = map(lambda x: x.ljust(25,' '),sub_array)
				datita += ''.join(sub_array) + '\n'
			total_weight += float(acum_weight)
			container = []
			acum_weight = 0
			cont += 1
			datita += 'Peso Parcial:'.ljust(14,' ')+str(acum_weight).rjust(13,' ')+ 2*'\n'
		datita+='\nPeso total:'.ljust(14,' ')+str(total_weight).rjust(13,' ')
		return datita
		

	def _get_data_for_internal(self, move_lines):
		datita = 'ITEM'+10*' '+'CODIGO'+14*' '+'CANTIDAD'+7*' '+'UNIT.'+15*' '+'DESCRIPCION ARTICULOS\n' 
		for move in move_lines:
			cont = 1
			total_weight = 0
			nombre = move.product_id.name_get()[0][1]
			if move.product_id.default_code:
				if move.product_id.default_code in nombre:
					nombre = nombre.replace(move.product_id.default_code, '').replace('[]', '')
			
			acum_weight = move.product_id.weight * move.product_uom_qty
			acum_weight = '{:,.2f}'.format(decimal.Decimal ("%0.2f" %  acum_weight))
			data = [cont,move.product_id.default_code or '',move.product_uom_qty,move.product_uom.name,nombre]
			datita += (12*' ').join(map(str,data))+'\n'
			datita += 'Peso Parcial:'.ljust(14,' ')+str(acum_weight).rjust(13,' ')+ 2*'\n'
			total_weight += float(acum_weight)
			cont += 1

		datita+='\nPeso total:'.ljust(14,' ')+str(total_weight).rjust(13,' ')
		return datita

	def _process_measures_item(self,base1,base2,height1,height2):
		label = ''
		base1,base2,height1,height2 = str(base1),str(base2),str(height1),str(height2)
		if base1 == base2:
			label += base1
		else:
			label += base1 + '/' + base2
		label += 'X'
		if height1 == height2:
			label += height1
		else:
			label += height1 + '/' + height2
		return label
