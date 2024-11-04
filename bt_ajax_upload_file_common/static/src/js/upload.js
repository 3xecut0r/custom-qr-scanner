/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.SurveyUploadFile = publicWidget.Widget.extend({
    selector: '.upload-files',

    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.file_loaded = false;
        this.readonly = options.readonly;
        this.options = options.readonly;
    },
    start: function () {
        var self = this;
        var $inputFile = this.$target.find(".input-file");
        var files_ids = [];
        var input_name = $inputFile.attr('data-name');
        var res_model = $inputFile.attr('res-model');
        var res_id = $inputFile.attr('data-res-id');
        var max_file_size = $inputFile.attr('max-file-size');
        var multifile = $inputFile.attr('multi-file');
        var maxFileSize;
        if (max_file_size)
            maxFileSize = max_file_size*1024000;
        else
            max_file_size = 10;
            maxFileSize = max_file_size*1024000;
        var ufiles = this.$target.find('input');
        var show_del = $inputFile.attr('show-delete');
        var show_del = show_del=="true" ?  true : false;
        var multifile = multifile=="true" ?  true : false;

        var show_download = $inputFile.attr('show-download');
        var show_download = show_download=="true" ?  true : false;
        if(this.readonly !== undefined){
            show_del = !this.readonly;
            show_download = !this.readonly;
        }
        var totalfilesize = 0;
        $inputFile.uploadFile({
            url: '/upload/attachment/onchange',
            fileName: 'attachments',
            multiple: multifile,
            maxFileCount: multifile ? 99 : 1,
            maxFileSize: maxFileSize,
            showDelete: show_del,
            showDownload: show_download,
            formData: { 'res_id': res_id, 'res_model': res_model },
            onSelect: function (files) {
                var totalfilesize_select = 0;
                for (var i = 0; i < files.length; i++) {
                    totalfilesize_select += files[i].size;
                }
                if ((totalfilesize + totalfilesize_select) > maxFileSize) {
                    alert("The maximum size for all your attachments is " + max_file_size + "MB, please compress your files if required");
                    return false;
                }
                totalfilesize += totalfilesize_select;
                return true;
            },
            deleteCallback: function (data, pd) {
                jsonrpc('/upload/attachment/delete', {
                    'attachment_id': data,
                    'res_id': res_id,
                    'res_model': res_model
                }).then(function (response) {
                    if (response && response.attachment) {
                        var index = files_ids.indexOf(response.attachment);
                        if (index > -1) {
                            files_ids.splice(index, 1);
                            totalfilesize -= response.size || 0;
                        }
                        ufiles.val(files_ids.toString());
                    } else {
                        console.warn("Unexpected response:", response);
                    }
                }).catch(function (error) {
                    console.error("Error during attachment deletion:", error);
                });
            },
            onLoad: function (obj) {
                jsonrpc('/upload/attachment/onload', {
                    'res_model': res_model,
                    'res_id': res_id,
                    'files_ids': ufiles.val()
                }).then(function (data) {
                    for (var i = 0; i < data.length; i++) {
                        obj.createProgress(data[i]["path"], data[i]["name"], data[i]["size"]);
                        files_ids.push(data[i]["path"]);
                        totalfilesize += data[i]["size"];
                    }
                    ufiles.val(files_ids.toString());
                    if (data.length <= 0) {
                        var $noattachment = $('form').find('.no-attachment');
                        if ($noattachment.length <= 0) {
                            $noattachment = $('div').find('.no-attachment');
                        }
                        if ($noattachment.length > 0) {
                            $noattachment.show();
                        }
                    }
                    self.file_loaded = true;
                });
            },
            onSuccess: function (files, response, xhr, pd) {
                if (response && response.attachment) {
                    files_ids.push(response.attachment);
                }
                if (response && response.x_ocr) {
                    _fillSurveyFields(response.x_ocr);
                }
                ufiles.val(files_ids.toString());
            },
            downloadCallback: function (filename, pd) {
                window.open("/web/content/" + filename, '_blank');
            },
            uploadButtonClass: "btn browse-btn",
            uploadStr: '<i class="fa fa-paperclip"></i>  &#160; Select Files',
            dragDropStr: "<span><b>Drag &amp; Drop Files Here</b></span>",
            sizeErrorStr: "is not allowed. Allowed Max size:",
            maxFileCountErrorStr: " is not allowed. Maximum allowed files are: ",
            statusBarWidth: 350,
            dragdropWidth: 350,
        });

        function _fillSurveyFields(data) {
            const questions = $("h3 span");
            const inputs = $("input.o_survey_question_text_box");

            const requiredFields = {
                'Title': 'Position',
                'Name': 'Name',
                'Surname': 'Surname',
                'Position': 'Position',
                'Phone': 'Phone',
                'Mobile': 'Mobile',
                'Email': 'Email',
                'Company': 'Company',
                'Street': 'Street',
                'ZIP-Code': 'ZIP-Code',
                'City': 'City',
                'Country': 'Country',
                'Website': 'Website'
            };

            let inputIndex = 0;

            questions.each(function () {
                const questionTitle = $(this).text().trim();
                const fieldName = requiredFields[questionTitle];

                if (fieldName) {
                    const valueToFill = data[fieldName] || '';

                    if (inputs[inputIndex]) {
                        $(inputs[inputIndex]).val(valueToFill);
                        inputIndex++;
                    }
                }
            });
        }


        if(show_del==false){
            $inputFile.hide('form');
        }
        $('.btn-bs-file input').on('change', function(event) {
            var file_text = $(this).parent().parent().find('span');
            if( this.files.length > 1) {
                file_text.text(this.files.length +' files selected');
            } else if( this.files.length == 1) {
                file_text.text(this.files[0].name);
            } else {
                file_text.text('No file choosen');
            }

        });
    },

})