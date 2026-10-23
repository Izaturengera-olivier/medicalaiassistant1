"""Tests for medical document upload and AI scanner/report analysis."""

import io
import zipfile
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from ai.models import ChatConversation, ChatMessage, MedicalDocument
from ai.services import AIService, DocumentOCRService, DocumentParserService
from core.constants import UserRole
from core.exceptions import DocumentParseError


class DocumentParserServiceTest(APITestCase):
    def setUp(self):
        self.parser = DocumentParserService()

    def test_parse_plain_text_scan_report(self):
        content = (
            "EXAMINATION: CT CHEST WITH INTRAVENOUS CONTRAST\n"
            "CLINICAL INDICATION: Cough and dyspnea\n"
            "FINDINGS: There is a 7 mm solid non-calcified nodule in the right lower lobe.\n"
            "No pleural effusion or pneumothorax.\n"
            "IMPRESSION: 7 mm right lower lobe pulmonary nodule.\n"
        )
        file_obj = io.BytesIO(content.encode("utf-8"))
        res = self.parser.parse_file(file_obj, "chest_ct_scan.txt", "text/plain")

        self.assertEqual(res["category"], "imaging_scan")
        self.assertIn("CT", res["exam_type"].upper())
        self.assertIn("7 mm solid", res["text"])
        self.assertTrue(res["has_extractable_text"])

    def test_parse_lab_report(self):
        content = (
            "LABORATORY TEST REPORT\n"
            "COMPLETE BLOOD COUNT (CBC)\n"
            "Hemoglobin: 9.8 g/dL (Normal: 12.0 - 15.5)\n"
            "Platelets: 210,000 /mcL\n"
            "ALT: 125 U/L (High)\n"
            "Creatinine: 0.9 mg/dL\n"
        )
        file_obj = io.BytesIO(content.encode("utf-8"))
        res = self.parser.parse_file(file_obj, "blood_test_results.txt", "text/plain")

        self.assertEqual(res["category"], "lab_result")
        self.assertIn("Hemoglobin", res["text"])

    def test_pdf_without_text_is_rejected(self):
        """A page with no text layer must not be analysed as if it were a report."""
        try:
            from pypdf import PdfWriter
            writer = PdfWriter()
            writer.add_blank_page(width=200, height=200)
            stream = io.BytesIO()
            writer.write(stream)
            stream.seek(0)
        except ImportError:
            stream = io.BytesIO(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n")

        with self.assertRaises(DocumentParseError):
            self.parser.parse_file(stream, "radiology_scan.pdf", "application/pdf")

    def test_unsupported_file_type_is_rejected(self):
        file_obj = io.BytesIO(b"anything at all")

        with self.assertRaises(DocumentParseError):
            self.parser.parse_file(file_obj, "report.xlsx", "application/vnd.ms-excel")

    def test_oversized_file_is_rejected(self):
        original = self.parser.MAX_FILE_SIZE_BYTES
        self.parser.MAX_FILE_SIZE_BYTES = 10
        self.addCleanup(setattr, self.parser, "MAX_FILE_SIZE_BYTES", original)

        with self.assertRaises(DocumentParseError):
            self.parser.parse_file(io.BytesIO(b"x" * 50), "report.txt", "text/plain")

    def test_docx_text_is_extracted(self):
        """Word reports are a zip of XML; paragraph text must come out readable."""
        body = (
            "<w:document><w:body>"
            "<w:p><w:r><w:t>EXAMINATION: CT CHEST</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>IMPRESSION: </w:t></w:r><w:r><w:t>7 mm nodule</w:t></w:r></w:p>"
            "</w:body></w:document>"
        )
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as written:
            written.writestr("word/document.xml", body)
        archive.seek(0)

        res = self.parser.parse_file(archive, "ct_report.docx", "")

        self.assertIn("CT CHEST", res["text"])
        self.assertIn("7 mm nodule", res["text"])
        self.assertEqual(res["category"], "imaging_scan")

    def test_image_is_read_through_ocr(self):
        """Images have no text layer, so the OCR service supplies the report content."""
        from PIL import Image

        stream = io.BytesIO()
        Image.new("RGB", (1600, 900), "white").save(stream, format="PNG")
        stream.seek(0)

        with mock.patch.object(
            DocumentOCRService, "read", return_value="LABORATORY TEST REPORT\nHemoglobin: 9.8 g/dL"
        ) as ocr:
            res = self.parser.parse_file(stream, "lab_photo.png", "image/png")

        self.assertTrue(ocr.called)
        self.assertEqual(res["category"], "lab_result")
        self.assertIn("Hemoglobin", res["text"])

    def test_ocr_reports_missing_engine_as_actionable_error(self):
        from PIL import Image

        stream = io.BytesIO()
        Image.new("RGB", (60, 40), "white").save(stream, format="PNG")

        with override_settings(TESSERACT_CMD="no-such-tesseract-binary"):
            with self.assertRaisesRegex(DocumentParseError, "(?i)tesseract"):
                DocumentOCRService().read(stream.getvalue())


class AIServiceDocumentAnalysisTest(APITestCase):
    def setUp(self):
        self.ai_service = AIService()

    def test_analyze_scanner_result_with_nodule(self):
        report = (
            "CT SCAN CHEST WITHOUT CONTRAST\n"
            "FINDINGS: 7mm solid pulmonary nodule in right lower lobe.\n"
            "IMPRESSION: Indeterminate pulmonary nodule requiring Fleischner follow-up."
        )
        analysis = self.ai_service.analyze_medical_document(
            document_text=report,
            document_category="imaging_scan",
            exam_type="CT Scan Chest",
            user_message="Is this scanner result serious?",
            user_role="PATIENT",
        )

        self.assertIn("reply", analysis)
        self.assertTrue(len(analysis["scan_findings"]) > 0)
        self.assertTrue(len(analysis["abnormalities"]) > 0)
        self.assertTrue(len(analysis["trusted_solutions"]) > 0)
        self.assertTrue(len(analysis["sources"]) > 0)
        # Should cite Fleischner Society, NIH, or WHO guidelines
        self.assertTrue(
            any("Fleischner" in s["name"] or "NIH" in s["name"] or "WHO" in s["name"] for s in analysis["sources"])
            or any("Fleischner" in sol.get("guideline_source", "") for sol in analysis["trusted_solutions"])
        )

    def test_analyze_emergency_findings(self):
        report = (
            "CT BRAIN WITHOUT CONTRAST\n"
            "FINDINGS: Acute hyperdense intracranial hemorrhage in the right basal ganglia with 4mm midline shift."
        )
        analysis = self.ai_service.analyze_medical_document(
            document_text=report,
            document_category="imaging_scan",
            exam_type="CT Brain",
            user_role="DOCTOR",
        )

        self.assertEqual(analysis["urgency_level"], "URGENT_MEDICAL_ATTENTION")
        self.assertTrue(len(analysis["warning_signs"]) > 0)


class DocumentUploadAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="patient.test@example.com",
            password="testpassword123",
            first_name="Jane",
            last_name="Doe",
            role=UserRole.PATIENT,
        )
        self.client.force_authenticate(user=self.user)

    def test_upload_and_analyze_document_success(self):
        url = reverse("upload_and_analyze_document")
        file_content = (
            b"EXAMINATION: ABDOMINAL AND PELVIC CT SCAN\n"
            b"FINDINGS: Liver shows diffuse increased echogenicity consistent with hepatic steatosis. "
            b"No focal liver mass. Gallbladder without stones.\n"
            b"IMPRESSION: Moderate hepatic steatosis.\n"
        )
        uploaded_file = SimpleUploadedFile("abdomen_ct.txt", file_content, content_type="text/plain")

        response = self.client.post(
            url,
            {"file": uploaded_file, "message": "Please explain this CT scan for me.", "kind": "patient"},
            format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertIn("document_id", data)
        self.assertEqual(data["file_name"], "abdomen_ct.txt")
        self.assertEqual(data["document_category"], "imaging_scan")
        self.assertTrue(len(data["scan_findings"]) > 0)
        self.assertTrue(len(data["trusted_solutions"]) > 0)
        self.assertTrue(len(data["sources"]) > 0)

        # Verify database record
        doc_record = MedicalDocument.objects.get(id=data["document_id"])
        self.assertEqual(doc_record.user, self.user)
        self.assertIn("hepatic steatosis", doc_record.extracted_text.lower())

        # Verify conversation and message persistence
        conversation = ChatConversation.objects.get(id=data["conversation_id"])
        self.assertEqual(conversation.user, self.user)
        messages = conversation.messages.all()
        self.assertEqual(messages.count(), 2)  # User message + Assistant reply
        user_msg = messages.filter(role="user").first()
        self.assertIsNotNone(user_msg.document)

    def test_document_list_and_detail(self):
        doc = MedicalDocument.objects.create(
            user=self.user,
            file_name="mri_scan.pdf",
            file_size=1024,
            document_category="imaging_scan",
            extracted_text="MRI Brain unremarkable",
            ai_analysis={"reply": "Normal scan"}
        )

        list_url = reverse("medical_document_list")
        res_list = self.client.get(list_url)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.json()), 1)

        detail_url = reverse("medical_document_detail", kwargs={"pk": doc.id})
        res_detail = self.client.get(detail_url)
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.json()["file_name"], "mri_scan.pdf")
