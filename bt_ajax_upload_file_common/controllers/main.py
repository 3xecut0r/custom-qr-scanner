# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, Response
import json
from odoo import _
import base64
import unicodedata
import re


class AttachmentUpload(http.Controller):

    def add_attachment(self, ufile, res_model, res_id, res_field=False):
        partner = request.env.user.partner_id
        Model = request.env['ir.attachment']
        filename = ufile.filename
        if request.httprequest.user_agent.browser == 'safari':
            # Safari sends NFD UTF-8 (where é is composed by 'e' and [accent])
            # we need to send it the same stuff, otherwise it'll fail
            filename = unicodedata.normalize('NFD', ufile.filename)
        if ufile.filename:
            attachment = Model.sudo().create({
                    'name': ufile.filename,
                    'datas': base64.encodebytes(ufile.read()),
                    'store_fname': ufile.filename,
                    'res_model': res_model,
                    'res_field': res_field and res_field or '',
                    'res_id': res_id or False,
                    'ajax_uploaded_file': True,
                })

            ocr_template = request.env['ocr.template'].search([('name', '=', 'VisitCard')], limit=1)
            if not ocr_template:
                model = request.env['ir.model'].search([('model', '=', 'res.partner')], limit=1)
                ocr_template = request.env['ocr.template'].create({
                    'name': 'VisitCard',
                    'process_type': 'string',
                    'lang': 'eng',
                    'psm': '3',
                    'model_id': model.id,
                    'operation_type': 'update',
                    'restrict_im_size': False,
                })
            ocr_wizard = request.env['test.ocr.template.wizard'].with_context(active_id=ocr_template.id).create({
                'image': attachment.datas,
                'ocr_template_id': ocr_template.id
            })
            ocr_wizard.process_test_image()
            ocr_result = ocr_wizard.x_res_for_survey
            data = {}

            lines = ocr_result.split('\n')
            data['Name'] = lines[0].strip() if len(lines) > 0 else ''
            data['Position'] = lines[1].strip() if len(lines) > 1 else ''

            data['Address'] = lines[2].strip() if len(lines) > 2 else ''

            phone_match = re.search(r'Tel:\s*(.+)', ocr_result)
            fax_match = re.search(r'Fax:\s*(.+)', ocr_result)
            email_match = re.search(r'E-Mail:\s*(.+)', ocr_result)
            website_match = re.search(r'www\.(\S+)', ocr_result)

            data['Phone'] = phone_match.group(1).strip() if phone_match else ''
            data['Fax'] = fax_match.group(1).strip() if fax_match else ''
            data['Email'] = email_match.group(1).strip() if email_match else ''
            data['Website'] = f'www.{website_match.group(1).strip()}' if website_match else ''
            response_data = {'attachment': str(attachment.id), 'x_ocr': data}
            return Response(json.dumps(response_data), content_type='application/json')

        return None

    @http.route(['/upload/attachment/onchange'], type='http', auth="public", website=True, csrf=False)
    def upload_attachment_onchange(self, attachments, res_id, res_model, **kw):
        file_ids = kw.get('file_ids', [])
        survey = kw.get('survey', False)
        if survey:
            attachments = kw.get(attachments)
        if attachments:
            return self.add_attachment(attachments, res_model, res_id)

    @http.route(['/upload/attachment/onload'], type='json', auth="public", website=True, csrf=False)
    def uploaded_files(self, **kw):
        partner = request.env.user.partner_id
        files_ids = kw.get('files_ids', None)
        res_id = kw.get('res_id', '')
        res_model = kw.get('res_model', '')
        res_field = kw.get('res_field', '')
        if res_id and res_model:
            domain = [
                ('res_model', '=', res_model),
                ('res_id', '=', res_id),
                ('res_field', '=', res_field),
                ('ajax_uploaded_file', '=', True),
            ]
            attachment_ids = request.env['ir.attachment'].sudo().search(domain)
            attachments = []
            for attach in attachment_ids:
                attachments.append({'path': attach.id, 'name': attach.name, 'size': attach.file_size})
            return attachments
        elif files_ids:
            files_ids = map(int, files_ids.split(','))
            attachment_ids = request.env['ir.attachment'].sudo().browse(files_ids)
            attachments = []
            for attach in attachment_ids:
                attachments.append({'path': attach.id, 'name': attach.name, 'size': attach.file_size})
            return attachments
        return {}


    def delete_attachment(self, attachment_id, res_model):
        if attachment_id:
            Model = request.env['ir.attachment']
            if type(attachment_id) != list:
                attachment_id = [int(attachment_id)] 
            domain = [
                ('id', 'in', attachment_id),
                ('res_model', '=', res_model),
                ('res_field', '=', False),
                ('ajax_uploaded_file', '=', True),
            ]
            attachment_id = Model.sudo().search(domain)
            size = attachment_id.file_size
            attachment_id.sudo().unlink()
            return size


    @http.route(['/upload/attachment/delete'], type='json', auth="public", website=True, csrf=False)
    def uploaded_files_delete(self, attachment_id, res_model, **kw):
        res = self.delete_attachment(attachment_id, res_model)
        if type(attachment_id) == list:
            attachment_id = attachment_id[0]
        if res:
            return attachment_id, res
