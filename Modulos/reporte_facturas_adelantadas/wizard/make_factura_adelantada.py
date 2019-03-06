# -*- coding: utf-8 -*-

import base64
from openerp.osv import osv
from odoo import models, fields, api
import decimal

class make_factura_adelantada(models.TransientModel):
	_name = "make.factura.adelantada"
	fec_ini = fields.Date(string="DEL")
	fec_fin = fields.Date(string="AL")


	@api.multi
	def do_csvtoexcel(self):
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()

		if self.fec_ini == False or self.fec_fin == False:
			raise osv.except_osv('Alerta','Debe seleccionar las fechas correspondiendtes')

		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file
		workbook = Workbook(direccion +'factura_adelantada.xlsx')
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

		worksheet.merge_range(1,0,1,12, "REPORTE FACTURA ADELANTADA", especial3)

		import datetime


		worksheet.write(4,0,"Pedido",boldbord)
		worksheet.write(4,1,"Documento del Cliente",boldbord)
		worksheet.write(4,2,"Cliente",boldbord)
		worksheet.write(4,3,"Producto",boldbord)
		worksheet.write(4,4,"Unidad",boldbord)
		worksheet.write(4,5,"Cantidad",boldbord)
		worksheet.write(4,6,"Tipo de Documento",boldbord)
		worksheet.write(4,7,"Nro. de Documento",boldbord)
		worksheet.write(4,8,"Fecha de emision",boldbord)
		worksheet.write(4,9,"Moneda",boldbord)
		worksheet.write(4,10,"Valor Unitario",boldbord)
		worksheet.write(4,11,"M2 Facturado",boldbord)
		worksheet.write(4,12,"M2 Atendido",boldbord)
		worksheet.write(4,13,"M2 Entregado",boldbord)
		worksheet.write(4,14,"M2 Por Atender",boldbord)
		worksheet.write(4,15,"M2 Por Entregar",boldbord)
		worksheet.write(4,16,"Impuesto Facturado",boldbord)
		worksheet.write(4,17,"Impuesto Atendido",boldbord)
		worksheet.write(4,18,"Impuesto Entregado",boldbord)
		worksheet.write(4,19,"Impuesto por Atender",boldbord)
		worksheet.write(4,20,"Impuesto por Entregar",boldbord)
		
		x=4

		sql = """
			create or replace view vst_ventaadelantada_fac as
			select so.name as pedido,rp.nro_documento as documentocli,rp.name as cliente,
				sol.name as producto,puo.name as unidad,sol.product_uom_qty as cantidad,
				tdoc.code as tipodocumento,ai.number as nrodocumento,ai.date as fechaemision,rcu.name as moneda,round(ail.price_subtotal / ail.quantity,4) as valuninet,
				ail.quantity as m2fact,
				ail.price_subtotal as impfact,
				sol.id
			from sale_order so
			join sale_order_line sol on sol.order_id = so.id
			join sale_calculadora_proforma scp on sol.id_type = scp.id
			left join sale_order_line_invoice_rel solir on sol.id = solir.order_line_id
			left join account_invoice_line ail on solir.invoice_line_id = ail.id
			left join account_invoice ai on ail.invoice_id = ai.id
			left join res_currency rcu on ai.currency_id = rcu.id
			left join res_partner rp on so.partner_id = rp.id
			left join einvoice_catalog_01 tdoc on ai.it_type_document = tdoc.id
			left join product_uom puo on sol.product_uom = puo.id
			where so.before_invoice;
			--so.id in (495,497,494);


			create or replace view vst_ventaadelantada_ent as
			select sol.id as sale_line_id,sum(sm.product_uom_qty) as entregado
			from sale_order so
			join sale_order_line sol on sol.order_id = so.id
			join procurement_order pcord on sol.id = pcord.sale_line_id
			join stock_move sm on sm.procurement_id = pcord.id
			where sm.state = 'done'
			group by 1;

			create or replace view vst_ventaadelantada_aten as
			select sol.id as sale_line_id,sum(case when gol.id is not null then round(scpl.area / scpl.cantidad,4) else 0.0000 end) as atendido
			from sale_order_line sol
			join sale_calculadora_proforma scp on sol.id_type = scp.id
			join sale_calculadora_proforma_line scpl on scp.id = scpl.proforma_id
			left join glass_order_line gol on scpl.id = gol.calc_line_id
			group by 1;
			--where sol.order_id = 498;


			select 
				va.pedido,va.documentocli,va.cliente,va.producto,va.unidad,va.cantidad,
				va.tipodocumento,va.nrodocumento,va.fechaemision,va.moneda,va.valuninet,
				va.m2fact,
				ent.entregado as m2entregado,
				ate.atendido as m2atendido,
				va.cantidad - ate.atendido as m2poratender,
				va.cantidad - ent.entregado as m2porentregar,
				va.impfact,
				round(va.valuninet * ate.atendido,2) as impatend,
				round(va.valuninet * ent.entregado,2) as impentreg,
				round(va.valuninet * (va.cantidad - ate.atendido),2) as impxatend,
				round(va.valuninet * (va.cantidad - ent.entregado),2) as impxentreg
			from vst_ventaadelantada_fac va
			left join vst_ventaadelantada_ent ent on va.id = ent.sale_line_id
			left join vst_ventaadelantada_aten ate on va.id = ate.sale_line_id
			where va.fechaemision >= '"""+ str(self.fec_ini) +"""' and va.fechaemision < '"""+ str(self.fec_fin) + """ ' """

		self.env.cr.execute(sql)
		result = self.env.cr.fetchall()
		
		for i in result:
			worksheet.write(x,0,i[0])
			worksheet.write(x,1,i[1])
			worksheet.write(x,2,i[2])
			worksheet.write(x,3,i[3])
			worksheet.write(x,4,i[4])
			worksheet.write(x,5,i[5])
			worksheet.write(x,6,i[6])
			worksheet.write(x,7,i[7])
			worksheet.write(x,8,i[8])
			worksheet.write(x,9,i[9])
			worksheet.write(x,10,i[10])
			worksheet.write(x,11,i[11])
			worksheet.write(x,12,i[12])
			worksheet.write(x,13,i[13])
			worksheet.write(x,14,i[14])
			worksheet.write(x,15,i[15])
			worksheet.write(x,16,i[16])
			worksheet.write(x,17,i[17])
			worksheet.write(x,18,i[18])
			worksheet.write(x,19,i[19])
			worksheet.write(x,20,i[20])

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

		
		f = open(direccion + 'factura_adelantada.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'Factura_Adelantada.xlsx',
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
