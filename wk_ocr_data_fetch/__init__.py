# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################
from . import models
from . import wizard


def pre_init_check(cr):
    from odoo.service import common
    from odoo.exceptions import ValidationError
    version_info = common.exp_version()
    server_series = version_info.get('server_serie')
    if server_series != '17.0':
        raise ValidationError('Module support Odoo series 17.0 found {}.'.format(server_series))
    return True