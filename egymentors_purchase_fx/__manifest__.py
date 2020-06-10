# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    'name': "EgyMentors Purchase FX Number[Texmar]",
    'author': 'EgyMentors, Ahmed Salama',
    'category': 'Inventory',
    'summary': """Purchase FX Number""",
    'website': 'http://www.egymentors.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '10.0',
    'depends': ['sale', 'sale_stock', 'purchase_stock',
                'account', 'stock_picking_batch', 'mrp'],
    'data': [
        'data/inventory_adjustment_data.xml',
        'data/po_type_data.xml',
        'data/sale_order_shedual_action.xml',
        'security/ir.model.access.csv',
        'security/sale_order_security.xml',
        'wizard/cancel_reason_view.xml',
        'wizard/stock_pickings_filtered_view.xml',
        'wizard/mrp_product_produce_view_changes.xml',

        'views/res_partner_view_changes.xml',
        'views/purchase_view_changes.xml',
        'views/stock_view_changes.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view_changes.xml',
        'views/mrp_product_view_changes.xml',

        'reports/sale_report_changes.xml',
        'reports/account_report_changes.xml',
        'reports/purchase_report_changes.xml',


    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
