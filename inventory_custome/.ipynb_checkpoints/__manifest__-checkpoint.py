# -*- coding: utf-8 -*-
{
    'name': "inventory_custome",

    'summary': """
        this module for customization egymentors_inverntory for update purache_request field to read from
        hr department 
        """,

    'description': """
     this module for customization egymentors_inverntory for update purache_request field to read from
        hr department 
    """,

    'author': "Muhammed Ashraf",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','stock','purchase_stock','purchase', 'purchase_requisition', 'report_xlsx', 'purchase_discount'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}