

from odoo import api, fields, models, _

class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"
    product_qty = fields.Float('To Do', default=0.0, digits=(12,6), required=True)
    qty_done = fields.Float('Done', default=0.0, digits=(12,6))


class StockPackOperation(models.Model):
    _inherit = 'stock.move'
    
    product_uom_qty = fields.Float(
        'Quantity',
        digits=(12,6),
        default=1.0, required=True, states={'done': [('readonly', True)]},
        help="This is the quantity of products from an inventory "
             "point of view. For moves in the state 'done', this is the "
             "quantity of products that were actually moved. For other "
             "moves, this is the quantity of product that is planned to "
             "be moved. Lowering this quantity does not generate a "
             "backorder. Changing this quantity on assigned moves affects "
             "the product reservation, and should be done with care.")
    
    product_qty = fields.Float(
        'Real Quantity', compute='_compute_product_qty', inverse='_set_product_qty',
        digits=(12,6), store=True,
        help='Quantity in the default UoM of the product')

    @api.one
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_product_qty(self):
        if self.product_uom:
            rounding_method = self._context.get('rounding_method', 'UP')
            self.product_qty = self.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id, rounding_method=rounding_method)
