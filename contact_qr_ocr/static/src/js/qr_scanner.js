/** @odoo-module **/

import SurveyFormWidget from '@survey/js/survey_form';

SurveyFormWidget.include({
    start: function () {
        var self = this;
        this.fadeInOutDelay = 400;

        return this._super.apply(this, arguments).then(function () {
            self._initQrScanner();
            self._observeContentChanges();
        });
    },

    _initQrScanner: function () {
        var $scanButton = this.$(".btn-scan-qr");
        var modal = document.getElementById("qrModal");
        var closeBtn = document.querySelector(".close");

        if ($scanButton.length) {
            $scanButton.on("click", () => {
                modal.style.display = "block";

                const qrScanner = new Html5Qrcode("reader");
                const config = { fps: 10, qrbox: 250 };

                qrScanner.start(
                    { facingMode: "environment" },
                    config,
                    (decodedText) => {
                        qrScanner.stop();
                        modal.style.display = "none";

                        const data = this._parseVCard(decodedText);
                        this._fillSurveyFields(data);
                    },
                    (errorMessage) => {
                        console.warn(`Occurs error while scanning QR`);
                    }
                ).catch((err) => {
                    console.error("Error:", err);
                });
            });

            closeBtn.onclick = () => {
                modal.style.display = "none";
                qrScanner.stop();
            };

            window.onclick = (event) => {
                if (event.target === modal) {
                    modal.style.display = "none";
                    qrScanner.stop();
                }
            };
        }
    },

    _parseVCard: function (vCard) {
        const data = {};
        const lines = vCard.split("\n");

        lines.forEach(line => {
            if (line.startsWith("N:")) {
                const [lastName, firstName] = line.slice(2).split(";");
                data.Name = firstName || '';
                data.Surname = lastName || '';
            } else if (line.startsWith("TITLE:")) {
                data.Position = line.slice(6);
            } else if (line.startsWith("TEL;WORK;VOICE:")) {
                data.Phone = line.slice(14);
            } else if (line.startsWith("TEL;TYPE=CELL:")) {
                data.Mobile = line.slice(13);
            } else if (line.startsWith("EMAIL;WORK;INTERNET:")) {
                data.Email = line.slice(20);
            } else if (line.startsWith("URL:")) {
                data.Website = line.slice(4);
            } else if (line.startsWith("ADR;WORK:")) {
                const addressParts = line.slice(8).split(";");
                data.Street = addressParts[2] || '';
                data.City = addressParts[3] || '';
                data['ZIP-Code'] = addressParts[5] || '';
                data.Country = addressParts[6] || '';
            } else if (line.startsWith("ORG:")) {
                data.Company = line.slice(4);
            }
        });

        return data;
    },

    _fillSurveyFields: function (data) {
        const questions = this.$("h3 span");
        const inputs = this.$("input.o_survey_question_text_box");

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
    },

    _observeContentChanges: function () {
        var self = this;
        const targetNode = document.querySelector(".o_survey_form_container");
        if (targetNode) {
            const observer = new MutationObserver(() => {
                self._initQrScanner();
            });

            observer.observe(targetNode, { childList: true, subtree: true });
        }
    }
});
