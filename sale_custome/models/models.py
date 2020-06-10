# -*- coding: utf-8 -*-

from odoo import models, fields, api
from itertools import groupby


class sales_custome(models.Model):
     _inherit = 'sale.order'
     customer_order=fields.Char(string="Customer’s order")


class delivery_custome (models.Model):
     _inherit = 'stock.picking'
     customer_order_delivery = fields.Char(string="Customer’s order")
    
class delivery_fun(models.Model):
     _inherit = "stock.move"

     def _assign_picking(self):
          """
          Linking customer_order_delivery field from  Order with customer_order in sales 
          :return:
          """  
          Picking = self.env['stock.picking']
          grouped_moves = groupby(sorted (self, key=lambda m: [f.id for f in m._key_assign_picking ()]),
                                   key=lambda m: [m._key_assign_picking ()])

          for group, moves in grouped_moves:
               moves = self.env['stock.move'].concat(*list (moves))
               new_picking = False
               # Could pass the arguments contained in group but they are the same
               # for each move that why moves[0] is acceptable
               picking = moves[0]._search_picking_for_assignation ()
               if picking:
                    if any (picking.partner_id.id != m.partner_id.id or picking.origin != m.origin for m in moves):
                         # If a picking is found, we'll append `move` to its move list and thus its
                         # `partner_id` and `ref` field will refer to multiple records. In this
                         # case, we chose to  wipe them.
                         picking.write ({
                              'partner_id': False,
                              'origin': False,
                         })
               else:
                    new_picking = True
                    picking = Picking.create (moves._get_new_picking_values ())
                    # Passing the value from Size of Pieces in Manufacturing Order to Size of Pieces field in Transfer
                    picking.customer_order_delivery = self.env['sale.order'].search ([('name', '=', self.origin)], limit=1).customer_order
               moves.write ({'picking_id': picking.id})
               moves._assign_picking_post_process (new=new_picking)
          return True
    
    

class invoice_custome(models.Model):
     _inherit = 'account.move'
     customer_order_invoice = fields.Char(string="Customer’s order")
    
class invoice_fun(models.Model):
     _inherit = "sale.order"
     '''
     This function to Prepare the dict of values to create the new invoice for a sales order and 
     add new field customer_order_invoice=customer_order
     '''   
     def _prepare_invoice(self):
        """
        Prepare the dict of values to create the new invoice for a sales order. This method may be
        overridden to implement custom invoice generation (making sure to call super() to establish
        a clean extension chain).
        """
        self.ensure_one()
        journal = self.env['account.move'].with_context(force_company=self.company_id.id, default_type='out_invoice')._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting sales journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        invoice_vals = {
            'ref': self.client_order_ref or '',
            'type': 'out_invoice',
            'narration': self.note,
            'currency_id': self.pricelist_id.currency_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.payment_term_id.id,
            'invoice_payment_ref': self.reference,
            'transaction_ids': [(6, 0, self.transaction_ids.ids)],
            'invoice_line_ids': [],
            'customer_order_invoice':self.customer_order
        }

        return invoice_vals