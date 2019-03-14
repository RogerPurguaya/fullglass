# -*- encoding: utf-8 -*-

from openerp.osv import osv
import base64
from openerp import models, fields, api
import codecs
import pprint


class datos_stock_minimos(models.Model):
	_name='datos.stock.minimos'
	_auto=False


	cod_producto = fields.Char( string='cod producto')
	producto = fields.Many2one('product.product', string='producto')
	u_med_compra = fields.Many2one('product.uom', string='unidad medida compra')
	cat_producto = fields.Many2one('product.category', string='cat producto')
	almacen_prod = fields.Many2one('stock.location', string='almacen producto')
	saldo_fisico = fields.Float( string='saldo fisico')
	stock_min = fields.Float( string='stock minimo')
	stock_max = fields.Float( string='stock maximo')
	
	ultimo_prov = fields.Many2one('res.partner', string='ultimo proveedor')
	ultimo_precio = fields.Float( string='ultimo precio')
	moneda = fields.Many2one('res.currency', string='moneda')
	




class report_stock_minimos_wizard(osv.TransientModel):
	_name='report.stock.minimos.wizard'

	
	
	filtro_por = fields.Many2one('product.category', string='Filtrar por:',required=True)
	almacen = fields.Many2one('stock.location', string='Almacen:',required=True)
	fecha = fields.Date(string='Fecha:',required=True)

	@api.multi
	def do_rebuild(self):
		
		
	
		
		import io
		from xlsxwriter.workbook import Workbook
		output = io.BytesIO()
		########### PRIMERA HOJA DE LA DATA EN TABLA
		#workbook = Workbook(output, {'in_memory': True})

		direccion = self.env['main.parameter'].search([])[0].dir_create_file

		workbook = Workbook(direccion +'reportstockminimos.xlsx')
		worksheet = workbook.add_worksheet("Reporte Stock Minimos")
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


		boldborda = workbook.add_format({'bold': True})
		boldborda.set_border(style=2)
		boldborda.set_align('center')
		boldborda.set_align('vcenter')
		boldborda.set_text_wrap()
		boldborda.set_font_size(9)
		boldborda.set_bg_color('#ffff40')

		bordazul = workbook.add_format()
		bordazul.set_border(style=1)
		bordazul.set_bg_color('#4040ff')
		bordazul.set_font_color('#ffffff')


		title = workbook.add_format({'bold': True})
		title.set_align('center')
		title.set_align('vcenter')
		title.set_text_wrap()
		title.set_font_size(20)
		worksheet.set_row(0, 30)

		x= 5				
		tam_col = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
		tam_letra = 1.2
		import sys
		reload(sys)
		sys.setdefaultencoding('iso-8859-1')

		worksheet.merge_range(1,0,0,11, u"Reporte de Reglas de Reabastecimiento", title)

			
		worksheet.write(3,0, u"Filtrado Por:",bold)
		worksheet.write(3,1, self.filtro_por.name , normal)

		worksheet.write(4,0, u"Almacen:",bold)
		worksheet.write(4,1, self.almacen.name ,normal)
		worksheet.write(5,0, u"Al:",bold)
		worksheet.write(5,1, self.fecha,normal)



		worksheet.write(7,0, u"Codigo Producto",boldbord)
		worksheet.write(7,1, u"Producto",boldbord)
		worksheet.write(7,2, u"Unidad Medida compra",boldbord)
		worksheet.write(7,3, u"Categoria Producto",boldbord)
		worksheet.write(7,4, u"Almacen",boldbord)
		worksheet.write(7,5, u"Saldo Fisico",boldbord)
		worksheet.write(7,6, u"Stock Minimo",boldbord)
		worksheet.write(7,7, u"Stock Maximo",boldbord)
		worksheet.write(7,8, u"Situacion Stock Actual",boldbord)
		worksheet.write(7,9, u"Ultimo Proveedor Compra",boldbord)
		worksheet.write(7,10, u"Ultimo Precio Unitario Compra",boldbord)
		worksheet.write(7,11, u"Moneda",boldbord)


		filtro =[]
	
		filtro.append( ('cat_producto','=',self.filtro_por.id))		
		filtro.append( ('cat_producto.parent_id','=',self.filtro_por.id))
		filtro.append( ('almacen_prod','=',self.almacen.id))





		self.env.cr.execute(""" drop view if exists datos_stock_minimos;
            create view datos_stock_minimos as (



                select row_number() OVER () AS id,* from (

				select 
				pp.default_code as cod_producto,
				pp.id as producto,
				pt.uom_id as u_med_compra,
				pc.id as cat_producto,
				sl.id as almacen_prod,
				saldos.saldo_fisico as saldo_fisico,
				swo.product_min_qty as stock_min,
				swo.product_max_qty as stock_max,
				rp.id as ultimo_prov,
				pol.price_unit as ultimo_precio,
				po.currency_id as moneda
				from product_product pp
				inner join product_template pt on pt.id = pp.product_tmpl_id
				inner join product_category pc on pc.id = pt.categ_id
				inner join stock_warehouse_orderpoint swo on swo.product_id = pp.id
				inner join stock_location sl on sl.id = swo.location_id
				left join (
						
							select ubicacion as almacen, product_id as producto, pt.categ_id as categoria,
							sum(stock_disponible) as saldo,
							sum(saldo_fisico) as saldo_fisico,
							sum(por_ingresar) as por_ingresar,
							sum(transito) as transito,
							sum(salida_espera) as salida_espera,
							sum(reservas) as reservas,
							sum(previsto) as saldo_virtual

							from vst_kardex_onlyfisico_total
							inner join product_template pt on pt.id = product_tmpl_id
							where vst_kardex_onlyfisico_total.date >= '""" +str(self.fecha).split('-')[0]+ """-01-01'
							and vst_kardex_onlyfisico_total.date <= '""" +str(self.fecha)+ """'
							group by ubicacion, product_id, pt.categ_id
							order by ubicacion,product_id, pt.categ_id
						


				) saldos on pp.id = saldos.producto and saldos.almacen = sl.id
				left join (
				            select pol.product_id, max(po.date_order) as fecha from
				            purchase_order po
				inner join purchase_order_line pol on pol.order_id = po.id
				where po.state = 'purchase' and po.date_order <= '""" +str(self.fecha)+ """'
				group by pol.product_id

				)  last_p on last_p.product_id = pp.id
				left join purchase_order po on po.date_order = last_p.fecha
				left join purchase_order_line pol on pol.product_id = pp.id and order_id = po.id
				left join res_partner rp on rp.id = po.partner_id) t)
		""")
		

		for line in self.env['datos.stock.minimos'].search(filtro):

			worksheet.write(x,0,line.cod_producto if line.cod_producto else '' ,bord )
			worksheet.write(x,1,line.producto.name_get()[0][1] if line.producto.id else '' ,bord )
			worksheet.write(x,2,line.u_med_compra.name if line.u_med_compra.name else '' ,bord )
			worksheet.write(x,3,line.cat_producto.name if line.cat_producto.name else '' ,bord )
			worksheet.write(x,4,line.almacen_prod.name_get()[0][1] if line.almacen_prod.id else '' ,bord )
			worksheet.write(x,5,line.saldo_fisico if line.saldo_fisico else 0 ,numberdos )
			worksheet.write(x,6,line.stock_min if line.stock_min else 0 ,numberdos)
			worksheet.write(x,7,line.stock_max if line.stock_max else 0 ,numberdos)
			
			worksheet.write(x,8,(line.saldo_fisico-line.stock_min) if (line.saldo_fisico-line.stock_min) else 0 ,numberdos)
			
			worksheet.write(x,9,line.ultimo_prov.name if line.ultimo_prov.name else '' ,bord )
			worksheet.write(x,10,line.ultimo_precio if line.ultimo_precio else 0 ,numberdos )	
			worksheet.write(x,11,line.moneda.name if line.moneda.name else '' ,bord )	

			x = x +1

		

		tam_col = [15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15,15]


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
		
		f = open(direccion + 'reportstockminimos.xlsx', 'rb')
		
		
		sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
		vals = {
			'output_name': 'reportstockminimos.xlsx',
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


	