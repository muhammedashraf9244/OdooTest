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
    'name': "EgyMentors Inventory Enhancement[ercac]",
    'author': 'EgyMentors, Ahmed Salama',
    'category': 'Inventory',
    'summary': """Inventory Enhancement""",
    'website': 'http://www.egymentors.com',
    'license': 'AGPL-3',
    'description': """
""",
    'version': '10.0',
    'depends': ['base', 'stock', 'purchase', 'purchase_requisition', 'report_xlsx', 'purchase_discount'],
    'data': [
        'data/inventory_adjustment_data.xml',
        'data/purchase_request_date.xml',
        'security/purchase_request_security.xml',
        'security/ir.model.access.csv',
        'reports/reports.xml',
    
        # 'views/res_config_view_changes.xml',
        'views/stock_inventory_view_changes.xml',
        'views/purchase_request_view.xml',
        'views/purchase_order_view_changes.xml',
        'views/purchase_requisition_view_changes.xml',
        'views/report_purchase_request.xml',
        'views/report_purchase_requisition_price.xml',
        'views/report_purchase_order_check.xml',
        'views/report_purchase_order_note.xml',
        # 'views/stock_picking_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
