# -*- coding: utf-8 -*-
{
    'name': "sales_custome",

    'summary': """
       this is custome module for sales to add new field
          """,

    'description': """
       this is custome module for sales to add new field
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/quotationview.xml',
        'views/invoice.xml',
        'views/delivery.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable':True,
    'auto_install':False,
    'application':True,
}