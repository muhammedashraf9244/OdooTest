# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning
# Ahmed Salama Code Start ---->


class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    def action_print(self):
        return self.env.ref('account.account_invoices').report_action(self)

    def action_print_without_payment(self):
        return self.env.ref('account.account_invoices_without_payment').report_action(self)

# Ahmed Salama Code End.
