# -*- coding: utf-8 -*-
from collections import defaultdict

from dateutil.relativedelta import relativedelta
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError


# Ahmed Salama Code Start ---->


class FxNumber(models.Model):
    _name = 'fx.number'
    _description = "FX Number"

    name = fields.Char(required=1)


class PurchaseOrderType(models.Model):
    _name = 'purchase.order.type'
    _description = "PO Type"

    name = fields.Char(required=1)


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    # fx_num_id = fields.Many2one('fx.number', "Fx No.")
    po_type_id = fields.Many2one('purchase.order.type', "PO Type")
    order_status = fields.Selection([('open', 'Open'),
                                     ('closed', 'Closed')], "Order Status", default='open')
    serial_number = fields.Char("Serial Number")

    # @api.model
    # def _prepare_picking(self):
    #     """
    #     Append fx_num_id To sent Data for picking
    #     # purchase_line_id
    #     :return:
    #     """
    #     res = super(PurchaseOrderInherit, self)._prepare_picking()
    #     if self.fx_num_id:
    #         res['fx_num_id'] = self.fx_num_id.id
    #     return res

    @api.model
    def create(self, vals):
        po_id = super(PurchaseOrderInherit, self).create(vals)
        serial_number = po_id.name
        if po_id.partner_id and po_id.partner_id.sequence_id:
            serial_number = po_id.partner_id.sequence_id.next_by_id()
        po_id.serial_number = serial_number
        return po_id

    def write(self, vals):
        """
        Change Status Of PO
        :param vals:
        :return:
        """
        super(PurchaseOrderInherit, self).write(vals)
        if vals.get('order_status') and vals.get('order_status') == 'closed' and self.origin:
            # Mark related order as Delivered
            orders_name = [self.origin]
            if ',' in self.origin:
                orders_name = self.origin.split(',')
            order_id = self.env['sale.order'].search([('name', 'in', orders_name)])
            if order_id:
                order_id.write({'purchase_delivered_id': self.id,
                                'purchase_delivered': True})
        return True

    def print_order(self):
        return self.env.ref('purchase.action_report_purchase_order').report_action(self)


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    line_status = fields.Selection([('open', 'Open'),
                                    ('closed', 'Closed')], "Status", default='open')
    fx_num_id = fields.Many2one('fx.number', "Fx No.")

    def write(self, vals):
        """
        Change Status Of PO
        :param vals:
        :return:
        """
        super(PurchaseOrderLineInherit, self).write(vals)
        if vals.get('line_status'):
            # Check Other Lines:
            for line in self:
                if line.order_id:
                    if all(line_status == 'closed' for line_status
                           in line.order_id.order_line.mapped('line_status')):
                        status = 'closed'
                    else:
                        status = 'open'
                    line.order_id.write({'order_status': status})
        return True

    def _prepare_stock_moves(self, picking):
        res = super(PurchaseOrderLineInherit, self)._prepare_stock_moves(picking)
        for line in res:
            if self.fx_num_id:
                line['fx_num_id'] = self.fx_num_id.id
        return res


class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _run_buy(self, procurements):
        procurements_by_po_domain = defaultdict(list)
        for procurement, rule in procurements:

            # Get the schedule date in order to find a valid seller
            procurement_date_planned = fields.Datetime.from_string(procurement.values['date_planned'])
            schedule_date = (procurement_date_planned - relativedelta(days=procurement.company_id.po_lead))

            supplier = procurement.product_id._select_seller(
                quantity=procurement.product_qty,
                date=schedule_date.date(),
                uom_id=procurement.product_uom)

            if not supplier:
                msg = _(
                    'There is no matching vendor price to generate the purchase order for product %s (no vendor defined, minimum quantity not reached, dates not valid, ...). Go on the product form and complete the list of vendors.') % (
                          procurement.product_id.display_name)
                raise UserError(msg)

            partner = supplier.name
            # we put `supplier_info` in values for extensibility purposes
            procurement.values['supplier'] = supplier
            procurement.values['propagate_date'] = rule.propagate_date
            procurement.values['propagate_date_minimum_delta'] = rule.propagate_date_minimum_delta
            procurement.values['propagate_cancel'] = rule.propagate_cancel

            domain = rule._make_po_get_domain(procurement.company_id, procurement.values, partner)
            procurements_by_po_domain[domain].append((procurement, rule))

        for domain, procurements_rules in procurements_by_po_domain.items():
            # Get the procurements for the current domain.
            # Get the rules for the current domain. Their only use is to create
            # the PO if it does not exist.
            procurements, rules = zip(*procurements_rules)

            # Get the set of procurement origin for the current domain.
            origins = set([p.origin for p in procurements])
            # Check if a PO exists for the current domain.
            po = self.env['purchase.order'].sudo().search([dom for dom in domain], limit=1)
            company_id = procurements[0].company_id
            if not po:
                # We need a rule to generate the PO. However the rule generated
                # the same domain for PO and the _prepare_purchase_order method
                # should only uses the common rules's fields.
                vals = rules[0]._prepare_purchase_order(company_id, origins, [p.values for p in procurements])
                # The company_id is the same for all procurements since
                # _make_po_get_domain add the company in the domain.
                po = self.env['purchase.order'].with_context(force_company=company_id.id).sudo().create(vals)
            else:
                # If a purchase order is found, adapt its `origin` field.
                if po.origin:
                    missing_origins = origins - set(po.origin.split(', '))
                    if missing_origins:
                        po.write({'origin': po.origin + ', ' + ', '.join(missing_origins)})
                else:
                    po.write({'origin': ', '.join(origins)})

            procurements_to_merge = self._get_procurements_to_merge(procurements)
            procurements = self._merge_procurements(procurements_to_merge)

            po_lines_by_product = {}
            grouped_po_lines = groupby(
                po.order_line.filtered(lambda l: not l.display_type and l.product_uom == l.product_id.uom_po_id).sorted(
                    'product_id'), key=lambda l: l.product_id.id)
            for product, po_lines in grouped_po_lines:
                po_lines_by_product[product] = self.env['purchase.order.line'].concat(*list(po_lines))
            po_line_values = []
            for procurement in procurements:
                po_lines = po_lines_by_product.get(procurement.product_id.id, self.env['purchase.order.line'])
                po_line = po_lines._find_candidate(*procurement)

                if po_line:
                    # If the procurement can be merge in an existing line. Directly
                    # write the new values on it.
                    vals = self._update_purchase_order_line(procurement.product_id,
                                                            procurement.product_qty, procurement.product_uom,
                                                            company_id,
                                                            procurement.values, po_line)
                    po_line.write(vals)
                else:
                    # If it does not exist a PO line for current procurement.
                    # Generate the create values for it and add it to a list in
                    # order to create it in batch.
                    partner = procurement.values['supplier'].name
                    po_line_values.append(self._prepare_purchase_order_line(
                        procurement.product_id, procurement.product_qty,
                        procurement.product_uom, procurement.company_id,
                        procurement.values, po))
            self.env['purchase.order.line'].sudo().create(po_line_values)
            # todo Confirm order by default
            po.button_confirm()

# Ahmed Salama Code End.
