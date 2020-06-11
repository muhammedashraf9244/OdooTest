# -*- coding: utf-8 -*-

from odoo import models, fields, api
from itertools import groupby


class sales_custome(models.Model):
     _inherit = 'sale.order'
     customer_order=fields.Char(string="Customer’s order")
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
        
        

class delivery_custome (models.Model):
     _inherit = 'stock.picking'
     customer_order_delivery = fields.Char(string="Customer’s order")
    
class delivery_fun(models.Model):
     _inherit = "stock.move"

     
     
     def _get_new_picking_values(self):
        """ return create values for new picking that will be linked with group
        of moves in self.
        """
        origins = set(self.filtered(lambda m: m.origin).mapped('origin'))
        origin = len(origins) == 1 and origins.pop() or False
        partners = self.mapped('partner_id')
        partner = len(partners) == 1 and partners.id or False
        return {
            'origin': origin,
            'company_id': self.mapped('company_id').id,
            'user_id': False,
            'move_type': self.mapped('group_id').move_type or 'direct',
            'partner_id': partner,
            'picking_type_id': self.mapped('picking_type_id').id,
            'location_id': self.mapped('location_id').id,
            'location_dest_id': self.mapped('location_dest_id').id,
            'customer_order_delivery':self.env['sale.order'].search (['|',('name', '=', self.origin),('client_order_ref', '!=',False)],limit=1).customer_order
        }
    


class invoice_custome(models.Model):
     _inherit = 'account.move'
     customer_order_invoice = fields.Char(string="Customer’s order")
'''    
class invoice_fun(models.Model):
     _inherit = "sale.order"
     
     This function to Prepare the dict of values to create the new invoice for a sales order and add new fieldcustomer_order_invoice=customer_order
        
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
        '''        