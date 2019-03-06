import base64
import codecs
import pprint
import math

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import magenta, red , black , blue, gray, Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Table
from reportlab.lib.units import  cm,mm
from reportlab.lib.utils import simpleSplit
from cgi import escape
import decimal


from odoo import api, fields, models, _, tools
from datetime import datetime

class reportewizard(models.TransientModel):
    _name = 'reporte.wizard'

    start_date = fields.Date(default=datetime.today(),string="Fecha Inicio : ") 
    end_date = fields.Date(default=datetime.today(),string="Fecha Fin : ")
    stage = fields.Selection([('entalle','Entalle'),('lavado','Lavado'),('pulido','Pulido'),('corte','Corte')],'Etapa :')
    
    @api.model_cr
    def init(self):
        self.env.cr.execute(""" 
            drop view if exists report_control_excel;

            create or replace view report_control_excel as (
                select glt.area, glt.nro_cristal,glot.name as lote, gor.name as orden_prod,gor.obra,glt.base1,glt.base2,glt.altura1,glt.altura2,rp.name,1 as cant,gsr.date,gsr.stage,pt.default_code||' '||pt.name as producto
                from glass_stage_record gsr
                join glass_lot_line glt on gsr.lot_line_id = glt.id
                join glass_order_line gol on glt.order_line_id = gol.id
                join glass_order gor on gol.order_id = gor.id
                join glass_lot glot on glt.lot_id = glot.id
                join sale_order so on gor.sale_order_id = so.id
                join res_partner rp on so.partner_id = rp.id
                join product_product pp on glt.product_id = pp.id
                join product_template pt on pp.product_tmpl_id = pt.id

            );

            """)

    @api.multi
    def do_rebuild(self):
        cast_stage = str(self.stage)
        self.env.cr.execute("""
            select * from report_control_excel WHERE date >= '"""+self.start_date+"""'::date
            AND date < ('"""+self.end_date+"""'::date + '1 day'::interval) AND stage LIKE '"""+cast_stage+"""'; 
        """)

        results = self.env.cr.fetchall()
        
        import io
        from xlsxwriter.workbook import Workbook
        output = io.BytesIO()


        direccion = self.env['main.parameter'].search([])[0].dir_create_file
        workbook = Workbook(direccion +'detalleFULLGLASS.xlsx')


        ## PRIMERA HOJA
        worksheet = workbook.add_worksheet("DETALLE")
        #Print Format
        worksheet.set_landscape() #Horizontal
        worksheet.set_paper(9) #A-4
        worksheet.set_margins(left=0.75, right=0.75, top=1, bottom=1)
        worksheet.fit_to_pages(1, 0)  # Ajustar por Columna 

        bold = workbook.add_format({'bold': False})
        bold.set_align('center')
        bold.set_align('vcenter')

        normal = workbook.add_format()
        boldbord = workbook.add_format({'bold': True})
        boldbord.set_border(style=2)
        boldbord.set_align('center')
        boldbord.set_align('vcenter')
        boldbord.set_text_wrap()
        boldbord.set_font_size(9)
        boldbord.set_bg_color('#DCE6F1')


        bold2 = workbook.add_format({'bold': False})
        bold2.set_align('center')
        bold2.set_align('vcenter')
        bold2.set_bg_color('#E9EFF6')


        bold7 = workbook.add_format({'bold': False})
        bold7.set_align('right')
        bold7.set_align('vcenter')
        bold7.set_bg_color('#E9EFF6')


        bold8 = workbook.add_format({'bold': False})
        bold8.set_align('right')
        bold8.set_align('vcenter')



        bold4 = workbook.add_format({'bold': False})
        bold4.set_align('left')
        bold4.set_align('vcenter')
        bold4.set_bg_color('#E9EFF6')


        bold3 = workbook.add_format({'bold': False})
        bold3.set_align('left')
        bold3.set_align('vcenter')



        bold5 = workbook.add_format({'bold': True})
        bold5.set_border(style=2)
        bold5.set_align('center')
        bold5.set_align('vcenter')



        bold6 = workbook.add_format({'bold': True})
        bold6.set_border(style=2)
        bold6.set_align('right')
        bold6.set_align('vcenter')


        # bottom
        bold9 = workbook.add_format({'bold': True})
        bold9.set_border(style=2)
        bold9 = workbook.add_format({'bottom': 1})



        numbertres = workbook.add_format({'num_format':'0.000'})
        numberdos = workbook.add_format({'num_format':'0.00'})
        numberdosbord = workbook.add_format({'num_format':'0.00','bold': True})
        numberdosbord.set_border(style=1)
        bord = workbook.add_format()
        bord.set_border(style=1)
        bord.set_text_wrap()
        bord.set_align('center')
        bord.set_align('vcenter')
        numberdos.set_border(style=1)
        numbertres.set_border(style=1)  


        title = workbook.add_format({'bold': True})
        title.set_align('center')
        title.set_align('vcenter')
        title.set_text_wrap()
        title.set_font_size(20)
        worksheet.set_row(0, 30)
        saldo_inicial = 0
        saldo_tmp = 0 ## saldo acumulativo
                 
        tam_col = [0,0,0,0]
        tam_letra = 1.2
        import sys
        reload(sys)
        sys.setdefaultencoding('iso-8859-1')    

        worksheet.merge_range(0,0,0,12, u"REPORTE DE PROCESOS", title)


        worksheet.write(2,0, u"Producto", boldbord)
        worksheet.write(2,1, u"Nombre", boldbord)
        worksheet.write(2,2, u"Fecha", boldbord)
        
        worksheet.write(2,3, u"Numero de Cristal", boldbord)
        worksheet.write(2,4, u"Lote", boldbord)
        worksheet.write(2,5, u"Orden de Produccion", boldbord)
        worksheet.write(2,6, u"Obra", boldbord)
        worksheet.write(2,7, u"Base 1", boldbord)
        worksheet.write(2,8, u"Base 2", boldbord)
        worksheet.write(2,9, u"Altura 1", boldbord)
        worksheet.write(2,10, u"Altura 2", boldbord)
        worksheet.write(2,11, u"Cantidad", boldbord)
        worksheet.write(2,12, u"M2", boldbord)

        x=3
        len_of_results = len(results)
        sum_cantidad = 0
        sum_area = 0 

        for line in results:
            print ("Largo de resultados : " + str(len_of_results))
            print ("x : " + str(x-2))
            if (len_of_results != (x-2)):
                if (x%2 == 0): # gris
                    worksheet.write(x,0,line[13],bold4) # product
                    worksheet.write(x,1,line[9],bold4) # name
                    worksheet.write(x,2,line[11],bold2) # date

                    worksheet.write(x,3,line[1],bold2) # nro_cristal
                    worksheet.write(x,4,line[2],bold2) # lote

                    worksheet.write(x,5,line[3],bold2) # order produccion
                    worksheet.write(x,6,line[4],bold2) # obra
                    worksheet.write(x,7,line[5],bold2) # base1
                    
                    worksheet.write(x,8,line[6],bold2) # base2
                    worksheet.write(x,9,line[7],bold2) # altura1
                    worksheet.write(x,10,line[8],bold2) # altura2
                    
                    worksheet.write(x,11,line[10],bold2) # cant
                    sum_cantidad = sum_cantidad + int(line[10])

                    bold7 = workbook.add_format({'num_format':'0.0000'})
                    bold7.set_bg_color('#E9EFF6')
                    worksheet.write(x,12,line[0],bold7) # area
                    sum_area = sum_area + float(line[0])


                else: # blanco

                    worksheet.write(x,0,line[13],bold3) # product
                    worksheet.write(x,1,line[9],bold3) # name
                    worksheet.write(x,2,line[11],bold) # date

                    worksheet.write(x,3,line[1],bold) # nro_cristal
                    worksheet.write(x,4,line[2],bold) # lote

                    worksheet.write(x,5,line[3],bold) # order produccion
                    worksheet.write(x,6,line[4],bold) # obra
                    worksheet.write(x,7,line[5],bold) # base1
                    
                    worksheet.write(x,8,line[6],bold) # base2
                    worksheet.write(x,9,line[7],bold) # altura1
                    worksheet.write(x,10,line[8],bold) # altura2
                    
                    worksheet.write(x,11,line[10],bold) # cant
                    sum_cantidad = sum_cantidad + int(line[10])

                    bold8 = workbook.add_format({'num_format':'0.0000'})
                    worksheet.write(x,12,line[0],bold8) # area
                    sum_area = sum_area + float(line[0])
            else:

                # bottom
                bold9 = workbook.add_format({'bold': True})
                bold9.set_border(style=3)
                bold9 = workbook.add_format({'bottom': 1})
                bold9.set_align('left')
                bold9.set_align('vcenter')

                worksheet.write(x,0,line[13],bold9) # product
                worksheet.write(x,1,line[9],bold9) # name


                bold10 = workbook.add_format({'bold': True})
                bold10.set_border(style=3)
                bold10 = workbook.add_format({'bottom': 1})
                bold10.set_align('center')
                bold10.set_align('vcenter')
                worksheet.write(x,2,line[11],bold10) # date

                worksheet.write(x,3,line[1],bold10) # nro_cristal
                worksheet.write(x,4,line[2],bold10) # lote

                worksheet.write(x,5,line[3],bold10) # order produccion
                worksheet.write(x,6,line[4],bold10) # obra
                worksheet.write(x,7,line[5],bold10) # base1
                
                worksheet.write(x,8,line[6],bold10) # base2
                worksheet.write(x,9,line[7],bold10) # altura1
                worksheet.write(x,10,line[8],bold10) # altura2
                
                worksheet.write(x,11,line[10],bold10) # cant
                sum_cantidad = sum_cantidad + int(line[10])

                bold11 = workbook.add_format({'bold': True})
                bold11.set_border(style=3)
                bold11 = workbook.add_format({'bottom': 1})
                bold11.set_align('right')
                bold11.set_align('vcenter')

                bold11 = workbook.add_format({'num_format':'0.0000'})
                worksheet.write(x,12,line[0],bold11) # area
                sum_area = sum_area + float(line[0])



            x = x + 1








        worksheet.write(x,10,"Total",boldbord) # TOTAL
        worksheet.write(x,11,str(sum_cantidad),bold5) # sum cantidad
        worksheet.write(x,12,str(sum_area),bold6) # sum area


        tam_col = [55,40,13,10,10,10,10,10,10,10,10,10,10]

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


        ## SEGUNDA HOJA

        self.env.cr.execute("""
            select SUM(area),SUM(cant),producto from report_control_excel WHERE date >= '"""+self.start_date+"""'::date
            AND date < ('"""+self.end_date+"""'::date + '1 day'::interval) AND stage LIKE '"""+cast_stage+"""' GROUP BY producto;

        """)


        results2 = self.env.cr.fetchall()


        worksheet = workbook.add_worksheet("RESUMEN")
        #Print Format
        worksheet.set_landscape() #Horizontal
        worksheet.set_paper(9) #A-4
        worksheet.set_margins(left=0.75, right=0.75, top=1, bottom=1)
        worksheet.fit_to_pages(1, 0)  # Ajustar por Columna 

        
        tam_col = [0,0,0,0]
        tam_letra = 1.2
        import sys
        reload(sys)
        sys.setdefaultencoding('iso-8859-1')

        worksheet.merge_range(0,0,0,2, u"REPORTE DE PROCESOS", title)


        worksheet.write(2,0, u" Producto", boldbord)
        worksheet.write(2,1, u" Cantidad", boldbord)
        worksheet.write(2,2, u" Area", boldbord)
        

        x=3

        len_of_results = len(results2)
        sum_cantidad = 0
        sum_area = 0 

        for line in results2:

            if (len_of_results != (x-2)):
                if (x%2 == 0): # gris
                    worksheet.write(x,0,line[2],bold4) # producto

                    worksheet.write(x,1,line[1],bold2) # cantidad
                    sum_cantidad = sum_cantidad + int(line[1])

                    bold7 = workbook.add_format({'num_format':'0.0000'})
                    bold7.set_bg_color('#E9EFF6')
                    worksheet.write(x,2,line[0],bold7) # area
                    sum_area = sum_area + float(line[0])

                else:

                    worksheet.write(x,0,line[2],bold3) # producto

                    worksheet.write(x,1,line[1],bold) # cantidad
                    sum_cantidad = sum_cantidad + int(line[1])


                    bold7 = workbook.add_format({'num_format':'0.0000'})
                    worksheet.write(x,2,line[0],bold7) # area
                    sum_area = sum_area + float(line[0])

            else:


                # bottom
                bold9 = workbook.add_format({'bold': True})
                bold9.set_border(style=3)
                bold9 = workbook.add_format({'bottom': 1})
                bold9.set_align('left')
                bold9.set_align('vcenter')

                worksheet.write(x,0,line[2],bold9) # product
                
                worksheet.write(x,1,line[1],bold10) # cant
                sum_cantidad = sum_cantidad + int(line[1])



                bold11 = workbook.add_format({'bold': True})
                bold11.set_border(style=3)
                bold11 = workbook.add_format({'bottom': 1})
                bold11.set_align('right')
                bold11.set_align('vcenter')

                bold11 = workbook.add_format({'num_format':'0.0000'})
                worksheet.write(x,2,line[0],bold11) # area
                sum_area = sum_area + float(line[0])




            x = x + 1


        worksheet.write(x,0,"Total",boldbord) # TOTAL
        worksheet.write(x,1,str(sum_cantidad),bold5) # sum cantidad
        worksheet.write(x,2,str(sum_area),bold6) # sum area


        tam_col = [55,13,13]

        worksheet.set_column('A:A', tam_col[0])
        worksheet.set_column('B:B', tam_col[1])
        worksheet.set_column('C:C', tam_col[2])



        workbook.close()
        
        f = open(direccion + 'detalleFULLGLASS.xlsx', 'rb')
            
        sfs_obj = self.pool.get('repcontab_base.sunat_file_save')
        vals = {
            'output_name': 'detalleFULLGLASS.xlsx',
            'output_file': base64.encodestring(''.join(f.readlines())),     
        }

        sfs_id = self.env['export.file.save'].create(vals)

        return {
            "type": "ir.actions.act_window",
            "res_model": "export.file.save",
            "views": [[False, "form"]],
            "res_id": sfs_id.id,
            "target": "new",
        }