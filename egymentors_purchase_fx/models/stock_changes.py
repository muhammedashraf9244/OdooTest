# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
# Ahmed Salama Code Start ---->


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        super(StockMoveInherit, self).write(vals)
        if vals.get('state'):
            for move in self:
                if move.purchase_line_id:
                    if vals.get('state') == 'done':
                        state = 'closed'
                    else:
                        state = 'open'
                    move.purchase_line_id.write({'line_status': state})
                elif move.sale_line_id:
                    if move.sale_line_id:
                        if vals.get('state') == 'done':
                            state = 'closed'
                        else:
                            state = 'open'
                        move.sale_line_id.write({'line_status': state})
        return True

    virtual_available = fields.Float(related='product_id.virtual_available')
    fx_num_id = fields.Many2one('fx.number', "Fx No.")
    roll_number = fields.Text("RN")
    grade_id = fields.Many2one('stock.move.grade', "Grade")
    pieces = fields.Char("Pieces")


class StockPickingGrade(models.Model):
    _name = 'stock.move.grade'
    _description = "Stock Grade"

    name = fields.Char("Grade")


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    vendor_receipt = fields.Char("Vendor Receipt")
    cancel_reason_id = fields.Many2one(
        'cancel.reason',
        string='Reason')

    def action_generate_backorder_wizard(self):
        self._process_back_order_automatic()

    def _process_back_order_automatic(self):
        for pick_id in self:
            moves_to_log = {}
            for move in pick_id.move_lines:
                if float_compare(move.product_uom_qty,
                                 move.quantity_done,
                                 precision_rounding=move.product_uom.rounding) > 0:
                    moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
            pick_id._log_less_quantities_than_expected(moves_to_log)
            pick_id.action_done()

    # fx_added = fields.Boolean("Fx Added")
    # fx_num_id = fields.Many2one('fx.number', "Fx No.")

    # def load_fx_lines(self):
    #     move_obj = self.env['stock.move']
    #     for picking in self:
    #         if picking.fx_num_id:
    #             product_list = []
    #             moves = move_obj.search([('picking_id.fx_num_id', '=', picking.fx_num_id.id)])
    #             for move in moves:
    #                 if move.product_id not in product_list \
    #                         and move.product_id.qty_available:
    #                     product_list.append(move.product_id)
    #             if product_list:
    #                 location = picking.location_id and picking.location_id or picking.location_dest_id
    #                 for product_id in product_list:
    #                     move_obj.create({
    #                         'product_id': product_id.id,
    #                         'picking_id': picking.id,
    #                         'name': product_id.display_name,
    #                         'product_uom': product_id.uom_id and product_id.uom_id.id or False,
    #                         'product_uom_qty': product_id.with_context({'location': location.id}).qty_available,
    #                         'state': 'draft',
    #                         'location_id': picking.location_id and picking.location_id.id or False,
    #                         'location_dest_id': picking.location_dest_id and picking.location_dest_id.id or False,
    #                     })
    #             picking.fx_added = True


class StockInventoryInherit(models.Model):
    _inherit = 'stock.inventory'

    ref = fields.Char("Code")

    def action_validate(self):
        self.ref = self.env['ir.sequence'].sudo().next_by_code('stock.inventory.code') or _('New')
        return super(StockInventoryInherit, self).action_validate()


class CancelReason(models.Model):
    _name = 'cancel.reason'
    _description = 'Cancel Reason'
    _rec_name = "name"

    name = fields.Char('Reason', required=True, translate=True)


class StockPickingBatchInherit(models.Model):
    _inherit = "stock.picking.batch"

    product_id = fields.Many2one('product.product', "Filtered Product",
                                 help=_("Receive only one filtered product on this patch"))

    def done(self):
        if self.product_id:
            pickings = self.mapped('picking_ids').filtered(lambda p: p.state not in ('cancel', 'done'))
            if self.product_id not in pickings.move_ids_without_package.mapped('product_id'):
                raise Warning(_("This filtered product [] not in any picking "
                                "lines of this patch" % self.product_id.display_name))
            # Receive only on product
            # print("Pickings: ", pickings)
            for picking in pickings:
                # print("picking: ", picking, picking.move_ids_without_package.mapped('product_id'))
                for ml in picking.move_ids_without_package.filtered(lambda l: l.product_id == self.product_id):
                    # print("ML: ", ml, ml.product_id.display_name,  ml.product_uom_qty, ml.quantity_done)
                    ml.write({'quantity_done': ml.product_uom_qty})
                    # print("qty: ", ml.product_uom_qty, ml.quantity_done)
            return super(StockPickingBatchInherit, self).done()


class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'
    

# Ahmed Salama Code End.
