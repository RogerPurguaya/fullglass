# -*- encoding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint




class datos_ordenes_requisicion(models.Model):
	_name='datos.ordenes.requisicion'
	_auto=False
			
	requisition_id= fields.Char( string='requisicion')
	codigo = fields.Char( string='codigo')
	prod = fields.Char( string='detalle')
	present = fields.Char(string='modelo')
	umed = fields.Char( string='unidad')
	mp_m2 = fields.Float( string='Mprima')
	
	corte = fields.Float( string='corte')
	dev_m2 = fields.Float(string='retazos')
	desper = fields.Float( string='desperdicio')
	consum = fields.Float( string='consumo')
	


class report_ordenes_requisicion_wizard(osv.TransientModel):
	_name='report.ordenes.requisicion.wizard'

	
	
	tipo_mp = fields.Many2one('academic.cycle',string='Tipo MP')
	orden_req = fields.Many2one('academic.cycle',string='Orden Requisicion')
	fecha_inicio = fields.Date(string='Fecha Inicio',required=True)
	fecha_fin = fields.Date(string='fecha Fin',required=True)

	
	
	

	@api.multi
	def do_rebuild(self):
		
		
	
		
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		workbook = Workbook(direccion +'reportordenesrequisicion.xlsx')
		worksheet = workbook.add_worksheet("Reporte de Ordenes de Requisicion")
		#Print Format
		worksheet.set_landscape() #Horizontal
		worksheet.set_paper(9) #A-4
		worksheet.set_margins(left=0.75, right=0.75, top=1, bottom=1)
		worksheet.fit_to_pages(1, 0)  # Ajustar por Columna	

		bold = workbook.add_format({'bold': True})
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(9)
		boldbord.set_bg_color('#DCE6F1')
		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_text_wrap()
		numberdos.set_border(style=1)
		numbertres.set_border(style=1)	


		title = workbook.add_format({'bold': True})
		title.set_align('center')
		title.set_align('vcenter')
		title.set_text_wrap()
		title.set_font_size(20)
		worksheet.set_row(0, 30)

		bordazul = workbook.add_format()
		bordazul.set_border(style=1)
		bordazul.set_bg_color('#4040ff')
		bordazul.set_font_color('#ffffff')

		boldborda = workbook.add_format({'bold': True})
		boldborda.set_border(style=2)
		boldborda.set_align('center')
		boldborda.set_align('vcenter')
		boldborda.set_text_wrap()
		boldborda.set_font_size(9)
		boldborda.set_bg_color('#ffff40')

		x= 4	
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		worksheet.merge_range(1,0,1,10, u"Reporte de Ordenes de Requisicion", title)

		worksheet.write(3,0, u"Requisicion",boldbord)
		worksheet.write(3,1, u"Codigo",boldbord)
		worksheet.write(3,2, u"Detalle",boldbord)
		worksheet.write(3,3, u"Modelo",boldbord)
		worksheet.write(3,4, u"Unidad",boldbord)
		worksheet.write(3,5, u"M. Prima",boldbord)
		worksheet.write(3,6, u"Corte",boldbord)
		worksheet.write(3,7, u"Retazo",boldbord)
		worksheet.write(3,8, u"Desperdicio",boldbord)
		worksheet.write(3,9, u"Consumo",boldbord)



		
	
		tam_col = [15,30,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]


		worksheet.set_column('A:A', tam_col[0])
		worksheet.set_column('B:B', tam_col[1])
		worksheet.set_column('C:C', tam_col[2])
		worksheet.set_column('D:D', tam_col[3])
		worksheet.set_column('E:E', tam_col[4])
		worksheet.set_column('F:F', tam_col[5])
		worksheet.set_column('G:G', tam_col[6])
		worksheet.set_column('H:H', tam_col[7])
		worksheet.set_column('I:I', tam_col[8])
		worksheet.set_column('J:J', tam_col[9])
		worksheet.set_column('K:K', tam_col[10])
		worksheet.set_column('L:L', tam_col[11])
		worksheet.set_column('M:M', tam_col[12])
		worksheet.set_column('N:N', tam_col[13])
		worksheet.set_column('O:O', tam_col[14])
		worksheet.set_column('P:P', tam_col[15])
		worksheet.set_column('Q:Q', tam_col[16])
		worksheet.set_column('R:R', tam_col[17])
		worksheet.set_column('S:S', tam_col[18])
		worksheet.set_column('T:T', tam_col[19])

		workbook.close()
		
		f = open(direccion + 'reportordenesrequisicion.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'reportordenesrequisicion.xlsx',
			'output_file': base64.encodestring(''.join(f.readlines())),		
		}

		sfs_id = self.env['export.file.save'].create(vals)

		#import os
		#os.system('c:\\eSpeak2\\command_line\\espeak.exe -ves-f1 -s 170 -p 100 "Se Realizo La exportación exitosamente Y A EDWARD NO LE GUSTA XDXDXDXDDDDDDDDDDDD" ')

		return {
		    "type": "ir.actions.act_window",
		    "res_model": "export.file.save",
		    "views": [[False, "form"]],
		    "res_id": sfs_id.id,
		    "target": "new",
		}


	