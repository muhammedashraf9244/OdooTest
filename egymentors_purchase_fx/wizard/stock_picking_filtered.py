# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class StockPickingDelivery(models.TransientModel):
    _name = 'stock.picking.filter'

    product_id = fields.Many2one('product.product', "Filter Product", required=True,
                                 help=_("Filter picking with filtered product"))

    def action_filter(self):
        picking_ids = self.env['stock.picking'].search([('move_lines.product_id', '=', self.product_id.id)])
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('id', 'in', picking_ids.mapped('id'))]
        print("action['domain']: ", action['domain'])
        return action

# Ahmed Salama Code End.
