# contact_qr_ocr/__manifest__.py
{
    'name': 'Contact QR OCR Integration',
    'version': '17.0.0.0.0',
    'summary': 'Scans QR codes and extracts contact data using OCR',
    'category': 'Productivity',
    'description': 'Automatically scans QR codes and extracts contact data, then adds or updates contacts in the CRM.',
    'author': 'Oleksii Panpukha',
    'license': 'Other proprietary',
    'website': 'https://github.com/3xecut0r',
    'depends': ['base', 'crm', 'survey', 'bt_survey_ajax_upload_file'],
    'data': [
        'views/survey.xml',
        'views/survey_question_templates.xml',
        'views/survey_question_views.xml',
        'views/res_partner.xml',
        'views/email_template.xml',
    ],
    'assets': {
        'survey.survey_assets': [
            'contact_qr_ocr/static/src/css/qr_modal.css',
            'contact_qr_ocr/static/lib/html5-qrcode.min.js',
            'contact_qr_ocr/static/src/js/qr_scanner.js',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}
