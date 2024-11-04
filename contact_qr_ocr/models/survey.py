from reportlab.graphics.barcode.qrencoder import QR

from odoo import api, fields, models


class SurveySurvey(models.Model):
    _inherit = 'survey.survey'

    x_is_qr = fields.Boolean(string='QR')

    def _create_survey_questions(self):
        self.env['survey.question'].create({'survey_id': self.id, 'title': 'Scan QR-code', 'question_type': 'qr_code'})
        for item in {
            'Title',
            'Name',
            'Surname',
            'Position',
            'Phone',
            'Mobile',
            'Email',
            'Company',
            'Street',
            'ZIP-Code',
            'City',
            'Country',
            'Website',
        }:
            self.env['survey.question'].create({'survey_id': self.id, 'question_type': 'char_box', 'title': item})
        self.env['survey.question'].create({'survey_id': self.id, 'title': 'OCR', 'question_type': 'file'})

    @api.model
    def create(self, vals):
        record = super(SurveySurvey, self).create(vals)
        if vals.get('x_is_qr'):
            record._create_survey_questions()
        return record

    def write(self, vals):
        result = super(SurveySurvey, self).write(vals)
        if 'x_is_qr' in vals and self.x_is_qr:
            self._create_survey_questions()
        return result


class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    question_type = fields.Selection(
        selection_add=[('qr_code', 'QR-code'), ('x_ocr', 'OCR')]
    )


class SurveyUserInputLine(models.Model):
    _inherit = 'survey.user_input.line'

    answer_type = fields.Selection(selection_add=[('qr_code', 'Scan QR'), ('x_ocr', 'OCR')])


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    def _save_lines(self, question, answer, comment=None, overwrite_existing=False):
        if question.question_type in {'qr_code', 'x_ocr'}:
            return
        super(SurveyUserInput, self)._save_lines(question, answer, comment=comment, overwrite_existing=overwrite_existing)
