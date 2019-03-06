# -*- encoding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint
import datetime



class reporte_seguimiento_produccion_wizard(osv.TransientModel):
	_name='reporte.seguimiento.produccion.wizard'

	de_inicio = fields.Date(string='Fecha Inicio',required=True)
	de_final = fields.Date(string='Fecha Fin',required=True)
	productos = fields.Many2one('product.product',string = 'Productos')
	clientes = fields.Many2one('res.partner',string = 'Clientes')
	op = fields.Many2one('glass.order',string = 'OP')
	vendedor = fields.Many2one('res.users',string = 'Vendedor')
	
	
	

	@api.multi
	def do_rebuild(self):

		
			
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		workbook = Workbook(direccion +'reporteseguimientoproduccion.xlsx')
		worksheet = workbook.add_worksheet("Seguimiento de Produccion")
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

		worksheet.merge_range(1,1,0,12, u"Reporte Seguimiento de Produccion", title)

		
	

		#worksheet.write(2,0, u"Fecha Actual", bold)
		#worksheet.write(2,1, str(fields.Date.today())[:10], normal) 
		#casteo y saco 10 caracteres


		

		worksheet.write(3,1, u"Orden Prod.",boldbord)
		worksheet.write(3,2, u"Lote prod.",boldbord)
		worksheet.write(3,3, u"Fecha Prod.",boldbord)
		worksheet.write(3,4, u"Fecha entrega",boldbord)
		worksheet.write(3,5, u"Cliente",boldbord)
		worksheet.write(3,6, u"Obra",boldbord)
		worksheet.write(3,7, u"Presentacion",boldbord)
		worksheet.write(3,8, u"Producto",boldbord)
		worksheet.write(3,9, u"M2 Cristal",boldbord)
		worksheet.write(3,10, u"Cant. Cristales",boldbord)		
		worksheet.write(3,11, u"Cant. Entregada",boldbord)
		worksheet.write(3,12, u"M2 Entregado",boldbord)
		worksheet.write(3,13, u"Observaciones",boldbord)
		

		condicionales = ""

		if self.de_inicio:
			condicionales +=  " and  gor.date_production >= '" + str(self.de_inicio) + "' "

		if self.de_final:
			condicionales +=  " and  gor.date_production <= '" + str(self.de_final) + "' "

		if self.vendedor.id:
			condicionales +=  " and  so.user_id = '" + str(self.vendedor.id) + "' "			

		if self.productos.id:
			condicionales +=  " and  pp.id = '" + str(self.productos.id) + "' "		

		if self.clientes.id:
			condicionales +=  " and  rp.id = '" + str(self.clientes.id) + "' "			

		if self.op.id:
			condicionales +=  " and  gor.id = '" + str(self.op.id) + "' "			


		self.env.cr.execute("""  select gor.name as ordenprod,glo.name as lote,gor.date_production as produccion,gor.date_delivery as entrega,
				rp.display_name as cliente,gor.obra,
				patv.name as present,pt.name as producto,
				count(gol.id) as numcri,
				sum(scpl.area) as m2cri,
				sum(case when gln.id is not null then 
						case when gln.templado then 1 else 0 end
					else 0 end) as crient,
				sum(case when gln.id is not null then 
						case when gln.templado then gln.area else 0 end
					else 0 end::numeric) as m2ent
			from glass_order gor
			join sale_order so on gor.sale_order_id = so.id
			join res_partner rp on so.partner_id = rp.id
			join sale_order_line sol on so.id = sol.order_id
			join product_product pp on sol.product_id = pp.id
			join product_template pt on pp.product_tmpl_id = pt.id
			join product_selecionable psel on psel.product_id = pt.id and psel.atributo_id = 4 -- Atributo Espesor
			join product_atributo_valores patv on psel.valor_id = patv.id and psel.atributo_id = patv.atributo_id
			join glass_order_line gol on gor.id = gol.order_id and pp.id = gol.product_id
			join sale_calculadora_proforma_line scpl on gol.calc_line_id = scpl.id
			left join glass_lot_line gln on gol.lot_line_id = gln.id
			left join glass_lot glo on gol.lot_id = glo.id
			where true 	
			""" + condicionales + """

			group by 1,2,3,4,5,6,7,8
			order by 2,1,3,6,7
			"""
		)

		valores_dia= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
		valores_total= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]


		fecha_actual = None
		for line in self.env.cr.fetchall():
			
			if fecha_actual != line[2] and fecha_actual != None:
				worksheet.merge_range(x,1,x,8, "Total "+ fecha_actual, bold)
				worksheet.write(x,9,valores_dia[0] if valores_dia[0]  else 0,numberdos)
				worksheet.write(x,10,valores_dia[1] if valores_dia[1]  else 0,numberdos)
				worksheet.write(x,11,valores_dia[2] if valores_dia[2]  else 0,numberdos)
				worksheet.write(x,12,valores_dia[3] if valores_dia[3]  else 0,numberdos)
				valores_dia= [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,]
				x=x+1
			fecha_actual = line[2]
			
			worksheet.write(x,1,line[0] if line[0] else '' ,bord )
			worksheet.write(x,2,line[1] if line[1]  else '',bord )
			worksheet.write(x,3,line[2] if line[2]  else '',bord)
			worksheet.write(x,4,line[3] if line[3]  else '',bord)
			worksheet.write(x,5,line[4] if line[4]  else '',bord)
			worksheet.write(x,6,line[5] if line[5]  else '',bord)
			worksheet.write(x,7,line[6] if line[6]  else '',bord)
			worksheet.write(x,8,line[7] if line[7]  else '',bord)

			worksheet.write(x,9,line[8] if line[8]  else 0,numberdos)
			valores_dia[0]+=line[8] if line[8]  else 0
			valores_total[0]+=line[8] if line[8]  else 0
			
			worksheet.write(x,10,line[9] if line[9]  else 0,numberdos)
			valores_dia[1]+=line[9] if line[9]  else 0
			valores_total[1]+=line[9] if line[9]  else 0
			
			worksheet.write(x,11,line[10] if line[10]  else 0,numberdos)
			valores_dia[2]+=line[10] if line[10]  else 0
			valores_total[2]+=line[10] if line[10]  else 0
			
			worksheet.write(x,12,line[11] if line[11]  else 0,numberdos)
			valores_dia[3]+=line[11] if line[11]  else 0
			valores_total[3]+=line[11] if line[11]  else 0
			x = x +1

		if fecha_actual != None:
			worksheet.merge_range(x,1,x,8, "Total "+ fecha_actual, bold)
			worksheet.write(x,9,valores_dia[0] if valores_dia[0]  else 0,numberdos)
			worksheet.write(x,10,valores_dia[1] if valores_dia[1]  else 0,numberdos)
			worksheet.write(x,11,valores_dia[2] if valores_dia[2]  else 0,numberdos)
			worksheet.write(x,12,valores_dia[3] if valores_dia[3]  else 0,numberdos)
			x=x+1


		worksheet.merge_range(x,1,x,8, "Total General", bold)
		worksheet.write(x,9,valores_total[0] if valores_total[0]  else 0,numberdos)
		worksheet.write(x,10,valores_total[1] if valores_total[1]  else 0,numberdos)
		worksheet.write(x,11,valores_total[2] if valores_total[2]  else 0,numberdos)
		worksheet.write(x,12,valores_total[3] if valores_total[3]  else 0,numberdos)

		
		tam_col = [13,10,12,12,12,20,12,12,20,12,12,12,12,12,12,12,12,12,12,12,12,12,12,12]


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
		
		f = open(direccion + 'reporteseguimientoproduccion.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'reporteseguimientoproduccion.xlsx',
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


	