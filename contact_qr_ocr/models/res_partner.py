# contact_qr_ocr/models/res_partner.py
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    x_photo = fields.Binary(string='Photo', attachment=True)
    survey_input_ids = fields.One2many('survey.user_input', 'partner_id', string='Answers Survey')
    survey_count = fields.Integer('Survey', compute='_compute_survey_count')

    @api.depends('survey_input_ids')
    def _compute_survey_count(self):
        for partner in self:
            partner.survey_count = len(partner.survey_input_ids)

    def action_view_survey(self):
        '''This function returns an action that displays the survey answers related to the partner.'''
        action = self.env['ir.actions.act_window']._for_xml_id('survey.action_survey_user_input')
        action['context'] = {}
        action['domain'] = [('partner_id', '=', self.id)]
        return action
