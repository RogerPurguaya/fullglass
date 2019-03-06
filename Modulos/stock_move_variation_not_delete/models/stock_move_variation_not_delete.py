# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from openerp.exceptions import ValidationError

class StockMoveVariationNotDelete(models.Model):
    _inherit = "product.attribute.line"

    @api.constrains('value_ids')
    def _isAllowtoDelete(self):
        #print self
        #print "\n**product_template",self.product_tmpl_id
        #print "**atribute", self.attribute_id
        #print "**values",self.value_ids
        sql = """
            select pp.id
            from product_product as pp
            inner join product_attribute_value_product_product_rel as pavpp
            on pp.id = pavpp.product_product_id
            inner join product_attribute_value as pav
            on pavpp.product_attribute_value_id = pav.id
            where product_tmpl_id = '%d'
            and pav.attribute_id= '%d'
            and active
            group by pp.id
        """ %( self.product_tmpl_id,self.attribute_id)
        self.env.cr.execute(sql)
        A = self.env.cr.fetchall()
        #print (A)
        sql1=""
        if len(self.value_ids)==1:
            sql1="""
            select id from
            product_product as pp
            inner join product_attribute_value_product_product_rel as pavpp
            on pp.id = pavpp.product_product_id
            where  pavpp.product_attribute_value_id = """+str(self.value_ids[0].id)
        else:
            ids=[]
            for r in self.value_ids:
                ids.append(r.id)
            sql1="""
            select id from
            product_product as pp
            inner join product_attribute_value_product_product_rel as pavpp
            on pp.id = pavpp.product_product_id
            where  pavpp.product_attribute_value_id in """+str(tuple(ids))
        self.env.cr.execute(sql1)
        B = self.env.cr.fetchall()
        #print B
        rpta= list(set(A) - (set(B)))
        #print rpta
        if rpta:
            for item in rpta:
                #print "content",item[0]
                sql="""
                select pp.id, sm.name from
                product_product as pp
                inner join stock_move as sm
                on pp.id= sm.product_id and sm.product_id = '%d' and state != 'cancel'
                """%(item[0])
                self.env.cr.execute(sql)
                sms = self.env.cr.fetchall()
                #print "sms: ", sms
                if (sms):
                    for s in sms:
                        #print "estos son elementos", s
                        raise ValidationError(u"Error no puede elimar las variación : "+ s[1]+u"\nExisten operaciones realizadas con estos productos. Porfavor vuelva a agregarlas a los Valores de Atributo")














    # @api.onchange('value_ids')
    # def _isAllowtoDelete(self):
    #     print "\n**product_template",self._origin.product_tmpl_id
    #     print "**atribute", self._origin.attribute_id
    #     print "**values",self.value_ids
    #     if len(self.value_ids) < 1:
    #         raise ValidationError("Error")
    '''
    @api.constrains('discount')
    def _check_something(self):
        sql = """
            select ppi.percent_price, pp.name as tarf, pt.name from
            sale_order as so
            inner join product_pricelist_item as ppi
            on so.pricelist_id = ppi.pricelist_id
            inner join product_pricelist as pp
            on pp.id = ppi.pricelist_id
            inner join sale_order_line as sol
            on ppi.product_tmpl_id = '%d'
            inner join product_template as pt
            on pt.id = ppi.product_tmpl_id
            where so.id = '%d'
            group by so.pricelist_id, ppi.percent_price, pp.name, pt.name
        """ %( self.product_id,self.order_id)
        self.env.cr.execute(sql)
        max_val = self.env.cr.fetchall()
        print "este es el usuario actual", self.env.user[0].id
        add_dis_user= self.env.user[0].additional_discount
        if max_val:
            des_final = max_val[0][0]+add_dis_user
            if self.discount > des_final:
                raise ValidationError("La tarifa: "+ str(max_val[0][1]) +", no puede realizar un descuento mayor al: " + str(des_final)+ "%, para el producto: " + str(max_val[0][2]))
    '''