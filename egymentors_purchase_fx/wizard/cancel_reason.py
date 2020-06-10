# -*- coding: utf-8 -*-
# © 2013 Guewen Baconnier, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class CancelReasonWizard(models.TransientModel):
    """ Ask a reason for cancellation."""
    _name = 'cancel.reason.wizard'
    _description = __doc__

    reason_id = fields.Many2one(
        'cancel.reason',
        string='Reason',
        required=True)

    def confirm_cancel(self):
        self.ensure_one()
        picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
        picking.write({'cancel_reason_id': self.reason_id.id})
        return picking.action_cancel()
