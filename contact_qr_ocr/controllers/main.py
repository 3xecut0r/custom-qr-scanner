import logging

from odoo import http
from odoo.http import request
from odoo.addons.survey.controllers.main import Survey


logger = logging.getLogger(__name__)

class CustomSurvey(Survey):
    def _prepare_survey_finished_values(self, survey, answer, token=False):
        values = super(CustomSurvey, self)._prepare_survey_finished_values(survey, answer, token)
        data = {}
        for question in answer.predefined_question_ids:
            matching_answer = next(
                (user_input for user_input in answer.user_input_line_ids if user_input.question_id == question),
                None
            )

            if matching_answer:
                data[question.display_name] = matching_answer.display_name

        partner = request.env['res.partner'].search([
            ('email', '=', data.get('Email')),
            '|',
            ('phone', '=', data.get('Phone')),
            ('mobile', '=', data.get('Mobile'))
        ], limit=1)

        if not partner:
            partner = request.env['res.partner'].create({
                'name': f"{data.get('Name', '')} {data.get('Surname', '')}".strip(),
                'phone': data.get('Phone'),
                'mobile': data.get('Mobile'),
                'email': data.get('Email'),
                'company_name': data.get('Company'),
                'street': data.get('Street'),
                'zip': data.get('ZIP-Code'),
                'city': data.get('City'),
                'country_id': request.env['res.country'].search([('name', '=', data.get('Country'))], limit=1).id,
                'website': data.get('Website'),
                'is_company': bool(data.get('Company') and len(data.get('Company').strip()) > 1),
                'survey_input_ids': answer,
            })
        tag = request.env['crm.tag'].search([('name', '=', survey.display_name)], limit=1)
        if not tag:
            tag = request.env['crm.tag'].create({
                'name': survey.display_name,
            })
        lead = request.env['crm.lead'].create({
            'name': f'{data.get("Title", "Lead from Survey")} {data.get("Name", "")} {data.get("Surname", "")}',
            'contact_name': partner.name,
            'partner_id': partner.id,
            'phone': partner.phone,
            'mobile': partner.mobile,
            'email_from': partner.email,
            'street': partner.street,
            'zip': partner.zip,
            'city': partner.city,
            'country_id': partner.country_id.id,
            'website': partner.website,
            'tag_ids': [(4, tag.id)],
        })
        template = request.env.ref('contact_qr_ocr.x_mail_template_contact_qr_ocr')
        if template:
            template.send_mail(lead.id, force_send=True)

        return values


