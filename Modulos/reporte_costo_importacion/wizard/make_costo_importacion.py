# -*- coding: utf-8 -*-

import base64
from openerp.osv import osv
from odoo import models, fields, api
import decimal

class make_costo_importacion(models.TransientModel):
	_name = "make.costo.importacion"
	orders = fields.Many2one('purchase.order','Orden de Compra')

	@api.multi
	def do_csvtoexcel(self):
		print("Si")
		productos = []
		order_list = self.orders.id
		print("Order",order_list)
		if order_list == False:
			raise osv.except_osv('Alerta','Debe seleccionar una Orden de Produccion')

		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'kardex_producto.xlsx')
		worksheet = workbook.add_worksheet("Kardex")
		bold = workbook.add_format({'bold': True})
		bold.set_font_size(8)
		normal = workbook.add_format()
		boldbord = workbook.add_format({'bold': True})
		boldbord.set_border(style=2)
		boldbord.set_align('center')
		boldbord.set_align('vcenter')
		boldbord.set_text_wrap()
		boldbord.set_font_size(8)
		boldbord.set_bg_color('#DCE6F1')

		especial1 = workbook.add_format({'bold': True})
		especial1.set_align('center')
		especial1.set_align('vcenter')
		especial1.set_text_wrap()
		especial1.set_font_size(15)
		
		especial2 = workbook.add_format({'bold': True})
		especial2.set_align('center')
		especial2.set_align('vcenter')
		especial2.set_text_wrap()
		especial2.set_font_size(8)

		especial3 = workbook.add_format({'bold': True})
		especial3.set_align('left')
		especial3.set_align('vcenter')
		especial3.set_text_wrap()
		especial3.set_font_size(15)

		numbertres = workbook.add_format({'num_format':'0.000'})
		numberdos = workbook.add_format({'num_format':'0.00'})
		numberseis = workbook.add_format({'num_format':'0.000000'})
		numberseis.set_font_size(8)
		numberocho = workbook.add_format({'num_format':'0.00000000'})
		numberocho.set_font_size(8)
		bord = workbook.add_format()
		bord.set_border(style=1)
		bord.set_font_size(8)
		numberdos.set_border(style=1)
		numberdos.set_font_size(8)
		numbertres.set_border(style=1)			
		numberseis.set_border(style=1)			
		numberocho.set_border(style=1)		
		numberdosbold = workbook.add_format({'num_format':'0.00','bold':True})	
		numberdosbold.set_font_size(8)
		x= 10				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		worksheet.merge_range(1,0,1,12, "REPORTE DE COSTO DE IMPORTACION POR ORDEN DE COMPRA", especial3)
		worksheet.write(2,0,'Orden de compra Nro.:',especial2)
		worksheet.write(3,0,'Fecha:',especial2)
		worksheet.write(5,0,'Proveedor:',especial2)
		
		worksheet.write(2,1,self.orders.name)
		worksheet.write(3,1,self.orders.date_order)
		worksheet.write(5,1,self.orders.partner_id[0].name)

		import datetime


		worksheet.merge_range(7,0,7,4,u"ALBARANES",especial3)
		worksheet.merge_range(8,0,9,0, u"N°",boldbord)
		worksheet.merge_range(8,1,9,1, u"Referencia",boldbord)
		worksheet.merge_range(8,2,9,2, u"Destino",boldbord)
		worksheet.merge_range(8,3,9,3, u"Proveedor",boldbord)
		worksheet.merge_range(8,4,9,4, u"Fecha de Albaran",boldbord)
		worksheet.merge_range(8,5,9,5, u"Documento de origen",boldbord)
		worksheet.merge_range(8,6,9,6, u"Status",boldbord)
		x=10
		for alb in self.orders.picking_ids:
			worksheet.write(x,0,alb[0].id)
			worksheet.write(x,1,alb[0].name)
			worksheet.write(x,2,alb[0].location_dest_id[0].name)
			worksheet.write(x,3,alb[0].partner_id[0].name)
			worksheet.write(x,4,alb[0].min_date)
			worksheet.write(x,5,alb[0].origin)
			if alb[0].state == 'done':
				worksheet.write(x,6,'Realizado')
			if alb[0].state == 'assigned':
				worksheet.write(x,6,'Disponible')
			if alb[0].state == 'partially_available':
				worksheet.write(x,6,'Parcialmente Disponible')
			if alb[0].state == 'confirmed':
				worksheet.write(x,6,'Esperando Disponibilidad')
			if alb[0].state == 'waiting':
				worksheet.write(x,6,'Esperando otra Operacion')
			if alb[0].state == 'cancel':
				worksheet.write(x,6,'Cancelado')
			if alb[0].state == 'draft':
				worksheet.write(x,6,'Borrador')
			x += 1
		x += 2

		sql = """
				SELECT distinct GVI.NAME, GVI.PARTNER_ID, GVI.ID
				FROM public.gastos_vinculados_line GVL
				INNER JOIN GASTOS_VINCULADOS_IT GVI ON GVI.ID = GVL.GASTOS_ID
				INNER JOIN STOCK_MOVE SM ON SM.ID = GVL.STOCK_MOVE_ID
				INNER JOIN PRODUCT_PRODUCT PP ON PP.ID = SM.PRODUCT_ID
				INNER JOIN PRODUCT_TEMPLATE PT ON PT.ID = PP.PRODUCT_TMPL_ID
				INNER JOIN STOCK_PICKING SP ON SP.ID = SM.PICKING_ID
				INNER JOIN PURCHASE_ORDER_LINE POL ON POL.ID = SM.PURCHASE_LINE_ID
				INNER JOIN PURCHASE_ORDER PO ON PO.ID = POL.ORDER_ID
				where PO.id = """ +str(self.orders.id)+ """
				"""
		self.env.cr.execute(sql)
		gastos_list = self.env.cr.fetchall()

		worksheet.merge_range(x,0,x+1,4,u"PRODUCTOS",especial3)
		x += 2
		worksheet.merge_range(x,0,x+2,0, u"Cantidad",boldbord)
		worksheet.merge_range(x,1,x+2,1, u"Codigo y Descripcion del Producto",boldbord)
		worksheet.merge_range(x,2,x+2,2, u"Unidad de Medida",boldbord)
		worksheet.merge_range(x,3,x+2,3, u"Costo Compra",boldbord)
		cont_d = 1
		for i in gastos_list:
			proveedor = self.env['res.partner'].search([('id','=',i[1])])
			worksheet.write(x,3+ cont_d, i[0],boldbord)
			worksheet.write(x+1,3+ cont_d,proveedor[0].name,boldbord)
			worksheet.write(x+2,3+ cont_d,'USD',boldbord)
			cont_d += 1
		worksheet.merge_range(x,3+cont_d,x+2,3+cont_d, u"Total",boldbord)
		worksheet.merge_range(x,3+cont_d+1,x+2,3+cont_d+1, u"Costo Unitario",boldbord)
			
		x += 3
		sql_ini = """
				SELECT 
				POL.product_qty,
				pt.name,
				pu.name,
				pol.price_subtotal,
				"""
		sql_mid = ""
		for i in gastos_list:
			sql_mid += """
						SUM( CASE WHEN GVI.name = '""" +i[0]+ """' then gvl.flete else 0 end)  as gasto1,
						min( CASE WHEN GVI.name = '""" +i[0]+ """' then gvi.id else null end)  as gasto1,
				"""

		sql_final = """
				gvi.state as final
				FROM public.gastos_vinculados_line GVL
				INNER JOIN GASTOS_VINCULADOS_IT GVI ON GVI.ID = GVL.GASTOS_ID
				INNER JOIN STOCK_MOVE SM ON SM.ID = GVL.STOCK_MOVE_ID
				INNER JOIN product_uom pu on pu.id = sm.product_uom
				INNER JOIN PRODUCT_PRODUCT PP ON PP.ID = SM.PRODUCT_ID
				INNER JOIN PRODUCT_TEMPLATE PT ON PT.ID = PP.PRODUCT_TMPL_ID
				INNER JOIN STOCK_PICKING SP ON SP.ID = SM.PICKING_ID
				INNER JOIN PURCHASE_ORDER_LINE POL ON POL.ID = SM.PURCHASE_LINE_ID
				INNER JOIN PURCHASE_ORDER PO ON PO.ID = POL.ORDER_ID
				where PO.id = """ +str(self.orders.id)+ """
				group by pt.name,pt.id,				POL.product_qty,
				pt.name,
				pu.name,
				pol.price_subtotal,
				gvi.state
				"""
		self.env.cr.execute(sql_ini + sql_mid + sql_final)
		result = self.env.cr.fetchall()
		total = 0
		sumatorias = []
		aux_sumatorias = []
		size = 0
		sum_totales = 0
		for c,order in enumerate(result):
			worksheet.write(x,0,order[0])
			worksheet.write(x,1,order[1])
			worksheet.write(x,2,order[2])
			worksheet.write(x,3,order[3])
			total += order[3] 
			cont_y = 1
			cont_write = 1
			cont_ids = 2
			for aux in gastos_list:
				print("cont_ids",order[3+cont_ids])
				print("cont_y",order[3+cont_y])
				gasto_vinculado = self.env['gastos.vinculados.it'].browse(order[3+cont_ids])
				if gasto_vinculado.tomar_valor == 'factura':
					fecha = gasto_vinculado.date_invoice
				if gasto_vinculado.tomar_valor == 'pedido':
					fecha = gasto_vinculado.date_purchase
					fecha = fecha[:10]
				cambios = self.env['res.currency.rate'].search([('name','=',fecha)])
				dec = order[3+cont_y]/cambios[0].type_sale
				total += dec
				if c == 0:
					sumatorias.append(dec)
				else:
					size = len(sumatorias)
					aux_sumatorias.append(dec)
				worksheet.write(x,3+cont_write,dec)
				cont_y += 2
				cont_write += 1
				cont_ids += 2
			for i in range(size):
				sumatorias[i] += aux_sumatorias[i]
			aux_sumatorias = []
			sum_totales += total
			total_aux = total/order[0]
			worksheet.write(x,3+cont_write,total)
			worksheet.write(x,3+cont_write+1,total_aux)
			total = 0
			x += 1

		worksheet.write(x+1,3,'Totales',boldbord)
		j = 0
		for i in range(size):
			worksheet.write(x+1,4+i,sumatorias[i])
			j += i
		worksheet.write(x+1,3+cont_write,sum_totales)

		tam_col = [11,60,14,27,17,17,17,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11,11]

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
		worksheet.set_column('T:Z', tam_col[19])

		workbook.close()

		
		f = open(direccion + 'kardex_producto.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'Kardex.xlsx',
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
