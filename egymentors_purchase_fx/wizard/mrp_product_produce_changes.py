# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
# Ahmed Salama Code Start ---->


class MrpProductProduceInherit(models.TransientModel):
    _inherit = 'mrp.product.produce'
    
    def _record_production(self):
        # Check all the product_produce line have a move id (the user can add product
        # to consume directly in the wizard)
        for line in self._workorder_line_ids():
            if not line.move_id:
                # Find move_id that would match
                if line.raw_product_produce_id:
                    moves = self.move_raw_ids
                else:
                    moves = self.move_finished_ids
                move_id = moves.filtered(lambda m: m.product_id == line.product_id and m.state not in ('done', 'cancel'))
                if not move_id:
                    # create a move to assign it to the line
                    if line.raw_product_produce_id:
                        values = {
                            'name': self.production_id.name,
                            'reference': self.production_id.name,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom_id.id,
                            'location_id': self.production_id.location_src_id.id,
                            'location_dest_id': line.product_id.property_stock_production.id,
                            'raw_material_production_id': self.production_id.id,
                            'group_id': self.production_id.procurement_group_id.id,
                            'origin': self.production_id.name,
                            'state': 'confirmed',
                            'company_id': self.production_id.company_id.id,
                            'pieces': line.pieces,
                        }
                        print("VALUES: ", values)
                    else:
                        values = self.production_id._get_finished_move_value(line.product_id.id, 0, line.product_uom_id.id)
                    move_id = self.env['stock.move'].create(values)
                    print("Move_id: ", move_id, move_id.picking_id)
                line.move_id = move_id.id

        # because of an ORM limitation (fields on transient models are not
        # recomputed by updates in non-transient models), the related fields on
        # this model are not recomputed by the creations above
        self.invalidate_cache(['move_raw_ids', 'move_finished_ids'])

        # Save product produce lines data into stock moves/move lines
        quantity = self.qty_producing
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified.") % self.product_id.display_name)
        self._update_finished_move()
        self._update_moves()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'date_start': datetime.now(),
            })

    def do_produce(self):
        """
        TODO: add pieces ref inside all related pickings
        :return: SUPER
        """
        stock_picking_ids = self.env['stock.picking']
        if self.production_id:
            if self.production_id.picking_ids:
                for p_picking_id in self.production_id.picking_ids:
                    stock_picking_ids += p_picking_id
            if self.production_id.sale_line_id:
                for o_picking_id in self.production_id.sale_line_id.order_id.picking_ids:
                    stock_picking_ids += o_picking_id
        if stock_picking_ids:
            for picking_id in stock_picking_ids:
                for line in self.raw_workorder_line_ids:
                    if line.pieces:
                        move_line = picking_id.move_lines.filtered(lambda l:  l.product_id == line.product_id)
                        if move_line:
                            move_line.pieces = line.pieces
        return super(MrpProductProduceInherit, self).do_produce()
    

class MrpProductProduceLineInherit(models.TransientModel):
    _inherit = 'mrp.product.produce.line'

    pieces = fields.Char("Pieces")
# Ahmed Salama Code End.

