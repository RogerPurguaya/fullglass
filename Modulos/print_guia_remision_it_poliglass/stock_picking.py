# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions, _
import base64,decimal
import sys
from odoo.exceptions import UserError
import pprint
from odoo.exceptions import ValidationError

class stock_picking(models.Model):
    _inherit = 'stock.picking'
  
    @api.multi
    def print_guia_remision(self):
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
            raise exceptions.UserError(_(u'Ingrese el numero de guía'))

        name_file = self.numberg + '.txt'
        direccion = self.env['main.parameter'].search([])[0].dir_create_file + name_file
        file = open(direccion, "w")
        reload(sys)
        sys.setdefaultencoding('iso-8859-1')

        txt = chr(27) + chr(15) + chr(27) + chr(48)
        file.write(txt)
        file.write(5 * "\n")
        # change
        data = ['',self.fecha_kardex if self.fecha_kardex else '',self.invoice_id.reference if self.invoice_id.reference else '']
        self.print_line(file,data,[14,55,30],style='columns')

        data = ['',partner_id.name,partner_id.nro_documento]
        self.print_line(file,data,[14,55,30],style='columns')
        # end change
        phone = partner_id.phone if partner_id.phone else ''
        data = ['',partner_id.street,phone]
        self.print_line(file,data,[14,55,30],style='columns')
        file.write(2 * "\n")

        nombre = self.nombre if self.nombre else 'EL MISMO'
        ruc = self.ruc if self.ruc else ''
        
        self.print_line(file,['',nombre,ruc],[14,50,30],style='columns')
        file.write(2*"\n")
        
        partida = self.picking_type_id.warehouse_id.partner_id.street
        if self.punto_partida:
            partida = self.punto_partida
        
        self.print_line(file,['',partida],[22,60],style='columns')

        street_partner = ''
        if partner_id:
            street_partner = partner_id.street
        if self.picking_type_id.code == 'internal':
            warehouse = self.location_dest_id.location_id.get_warehouse()
            street_partner = warehouse.partner_id.street if warehouse.partner_id.street else ''
        if self.punto_llegada:
            street_partner = self.punto_llegada

        self.print_line(file,['',street_partner],[22,60],style='columns')
        file.write(5 * "\n")

        # new code 
        # si los move_lines tienen glass_order_line_ids ejecutan print_details_move
        out = 0
        for move in self.move_lines:
            if len(move.glass_order_line_ids) > 0:
                out += 1
        if out == len(self.move_lines):
            self.print_details_move(file, self.move_lines)
            return
        # end new code
        
        for move in self.move_lines:
            headers_widths = [1,5,20,10,5,80,12]
            cont = 1
            total_weight = 0
            nombre = move.product_id.name_get()[0][1]
            if move.product_id.default_code:
                if move.product_id.default_code in nombre:
                    nombre = nombre.replace(move.product_id.default_code, '').replace('[]', '')
            acum_weight = move.product_id.weight * move.product_uom_qty
            acum_weight = '{:,.2f}'.format(decimal.Decimal ("%0.2f" %  acum_weight))
            data = ['',cont,move.product_id.default_code or '',move.product_uom_qty,move.product_uom.name,nombre,{'value':acum_weight,'position':'right'}]
            self.print_line(file,data,headers_widths,style='columns')
            
            total_weight += float(acum_weight)
            cont += 1

        file.write((37-cont) * '\n')
        self.print_line(file,['','Total Peso:',{'value':total_weight,'position':'right'}],[109,12,12])
        file.write(10*'\n')
        file.close()

    # New Code:
    # Función que imprime los detalles de los cristales cuando el stock move 
    #tiene cristales de salida asociados:
    @api.multi
    def print_details_move(self,file,move_lines):
        cont = 1
        acum_weight = 0
        total_weight = 0
        aux = 0
        container = []
        headers_widths = [1,5,20,10,5,80,12] # anchos para datos de producto

        for move in move_lines:
            nombre = move.product_id.name_get()[0][1]
            if move.product_id.default_code:
                if move.product_id.default_code in nombre:
                    nombre = nombre.replace(move.product_id.default_code, '').replace('[]', '')

            #detail_lines = self.env['glass.order.line'].search([('out_move','=',move.id)])
            detail_lines = move.glass_order_line_ids

            for detail in detail_lines:
                show_data = str(detail.order_id.name)+'-'+str(detail.crystal_number)+ '(' +self.process_measures_item(detail.base1,detail.base2,detail.altura1,detail.altura2) + ')'
                acum_weight += detail.peso
                container.append(show_data)
            

            acum_weight = '{:,.2f}'.format(decimal.Decimal ("%0.2f" %  acum_weight))
            nombre += ' ('+str(len(detail_lines))+' Pzs)'
            data = ['',cont,move.product_id.default_code or '',move.product_uom_qty,move.product_uom.name,nombre,{'value':acum_weight,'position':'right'}]
            self.print_line(file,data,headers_widths)

            container = [container[i:i+5] for i in range(0, len(container), 5)]
            for sub_array in container:
                self.print_line(file,[5*' ']+sub_array,style='consecutive',space=1)
                aux += 1
            
            total_weight += float(acum_weight)
            container = []
            acum_weight = 0
            cont += 1
            aux += 1
        
        file.write((37-aux) * '\n')
        self.print_line(file,['','Total Peso:',{'value':total_weight,'position':'right'}],[109,12,12])
        file.write(10*'\n')
        file.close()

    # Funcion para imprimir lineas de datos, puede imprimir en modo columnas o
    # en modo consecutivo. 
    # file: objeto file donde se escribira la info.
    # data: array de datos a imprimir: ejemplo: ['Nro','producto','precio'...]
    # widths: array de anchos de columnas ejm [20,25,30,15]
    # style : modo de impresion, por defecto imprime en columnas, para imprimir en forma # consecutiva setear como 'consecutive'
    # space: define el espacio entre items, solo se usa en el modo consecutivo
    # para definir alineacion de informacion en el modo columnas puede enviar 
    # una matriz con diccionarios: 
    # ['value1',{'value','valor de columna','position': 'right'}] position puede ser 
    # 'right','center', por defecto es left
    # Se encuentra abierto a mejoras :)
    @api.multi
    def print_line(self,file,data,widths=None,style='columns',space=2):
        position = 'left' # por defecto en left
        line = ''
        styles = ['consecutive','columns']
        if style not in styles:
            print('Invalid style value: set style as column or consecutive')
            return
        for i,item in enumerate(data):
            if type(item) is dict:
                value = str(item.get('value','undefined'))
                position = item.get('position','left')
            else:
               value = str(item)

            if style == 'consecutive':
                line += value + space * ' '
                continue
            # Quitamos espacios en blanco y si si el item es mayor al ancho se recorta a la longitud del ancho dejando 2 espacios:
            value = value.strip()[:widths[i]-1] 
            count = widths[i] - len(value)
            if position == 'right':
                line += count * ' ' + value
                continue
            if position == 'center':
                count = int(count / 2)
                line += count * ' ' + value + count * ' '
                continue
            line += value + count * ' '

        file.write(line+'\n')

    # obtener las medidas a mostrar
    @api.multi
    def process_measures_item(self,base1,base2,height1,height2):
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
