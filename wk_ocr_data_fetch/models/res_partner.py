# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from odoo import models
from odoo.addons.wk_ocr_data_fetch.models.models import OCRAbstractModel


class Partner(models.Model, OCRAbstractModel):
    _inherit = 'res.partner'
    # Set the description same to the inherited model
    _description = models.Model._description
