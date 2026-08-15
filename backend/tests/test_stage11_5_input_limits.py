import io
import pytest
import pypdf
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from app.core.utils import count_words
from app.schemas.project import ProjectCreate
from app.schemas.incident import IncidentCreate
from app.services.project_service import project_service
from app.services.incident_service import incident_service
from app.services.evidence_service import evidence_service
from app.services.ingestion.file_extractor import IngestionError


class UploadFileMock:
    def __init__(self, filename: str, content: bytes, content_type: str = "text/plain"):
        self.filename = filename
        self._content = content
        self.content_type = content_type
        self.file = io.BytesIO(content)

    async def read(self):
        return self._content

    async def seek(self, pos: int):
        self.file.seek(pos)


def generate_word_string(count: int) -> str:
    """Helper generating exact number of words separated by space."""
    return " ".join([f"word{i}" for i in range(1, count + 1)])


@pytest.mark.asyncio
async def test_01_zero_evidence_plus_valid_log_plus_valid_description(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P1", slug="lim-p1"))
    desc = generate_word_string(100)
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="Valid Incident", description=desc)
    )
    # Log file uploaded separately
    ev_log = await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"2026-08-15 10:00:00 INFO System started", "text/plain"),
        is_mandatory_log=True,
    )
    assert inc.id is not None
    assert ev_log.id is not None


@pytest.mark.asyncio
async def test_02_one_document_plus_valid_log(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P2", slug="lim-p2"))
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="Doc Incident", description="Single document test report")
    )
    await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"Log data", "text/plain"),
        is_mandatory_log=True,
    )
    ev_doc = await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="document",
        title="Incident Note",
        source="User Upload",
        file=UploadFileMock("note.txt", b"Technical investigation note", "text/plain"),
    )
    assert ev_doc.id is not None


@pytest.mark.asyncio
async def test_03_ten_evidence_files_plus_valid_log(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P3", slug="lim-p3"))
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="10 Evidence Items Test", description="Testing 10 documents")
    )
    await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"Log data", "text/plain"),
        is_mandatory_log=True,
    )
    for i in range(10):
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="document",
            title=f"Doc {i+1}",
            source="User Upload",
            file=UploadFileMock(f"doc_{i+1}.txt", f"Sample doc content {i+1}".encode(), "text/plain"),
        )


@pytest.mark.asyncio
async def test_04_ten_images_plus_valid_log(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P4", slug="lim-p4"))
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="10 Images Test", description="Testing 10 images")
    )
    await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"Log data", "text/plain"),
        is_mandatory_log=True,
    )
    for i in range(10):
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="image",
            title=f"Screenshot {i+1}",
            source="User Upload",
            file=UploadFileMock(f"screen_{i+1}.png", b"\x89PNG\r\n\x1a\n\x00\x00\x00", "image/png"),
        )


@pytest.mark.asyncio
async def test_05_five_documents_plus_five_images_plus_valid_log(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P5", slug="lim-p5"))
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="5 Docs + 5 Images", description="Testing mixed attachments")
    )
    await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"Log data", "text/plain"),
        is_mandatory_log=True,
    )
    for i in range(5):
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="document",
            title=f"Doc {i+1}",
            source="User Upload",
            file=UploadFileMock(f"doc_{i+1}.txt", b"Doc content", "text/plain"),
        )
    for i in range(5):
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="image",
            title=f"Image {i+1}",
            source="User Upload",
            file=UploadFileMock(f"img_{i+1}.png", b"\x89PNG", "image/png"),
        )


@pytest.mark.asyncio
async def test_06_eleven_evidence_files_rejection(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P6", slug="lim-p6"))
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="11 Evidence Files Test", description="Testing 11 attachments limit")
    )
    await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"Log data", "text/plain"),
        is_mandatory_log=True,
    )
    # Upload 10 evidence attachments
    for i in range(10):
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="document",
            title=f"Doc {i+1}",
            source="User Upload",
            file=UploadFileMock(f"doc_{i+1}.txt", b"Doc content", "text/plain"),
        )

    # 11th evidence file must be rejected with EVIDENCE_LIMIT_EXCEEDED
    with pytest.raises(IngestionError) as exc:
        await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="document",
            title="Doc 11",
            source="User Upload",
            file=UploadFileMock("doc_11.txt", b"Excess content", "text/plain"),
        )
    assert exc.value.code == "EVIDENCE_LIMIT_EXCEEDED"
    assert "Maximum 10 evidence files allowed" in exc.value.message


@pytest.mark.asyncio
async def test_07_log_file_not_counted_in_ten_evidence_limit(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P7", slug="lim-p7"))
    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="Log Exclusion Test", description="Checking log exclusion")
    )
    # Upload 1 mandatory log file
    await evidence_service.upload_evidence_file(
        db=db,
        incident_id=inc.id,
        type_str="log",
        title="Mandatory System Log",
        source="Incident Creation",
        file=UploadFileMock("system.log", b"Log data", "text/plain"),
        is_mandatory_log=True,
    )
    # Upload 10 additional evidence files
    for i in range(10):
        ev = await evidence_service.upload_evidence_file(
            db=db,
            incident_id=inc.id,
            type_str="document",
            title=f"Doc {i+1}",
            source="User Upload",
            file=UploadFileMock(f"doc_{i+1}.txt", b"Doc content", "text/plain"),
        )
        assert ev.id is not None


@pytest.mark.asyncio
async def test_08_two_thousand_word_description_pass(db: AsyncSession):
    proj = await project_service.create_project(db, ProjectCreate(name="Limit Test P8", slug="lim-p8"))
    valid_desc_2000 = generate_word_string(2000)
    assert count_words(valid_desc_2000) == 2000

    inc = await incident_service.create_incident(
        db, proj.id, IncidentCreate(title="2000 Word Test", description=valid_desc_2000)
    )
    assert inc.id is not None
    assert count_words(inc.description) == 2000


@pytest.mark.asyncio
async def test_09_two_thousand_and_one_word_description_fail():
    invalid_desc_2001 = generate_word_string(2001)
    assert count_words(invalid_desc_2001) == 2001

    with pytest.raises(ValidationError) as exc:
        IncidentCreate(title="2001 Word Test", description=invalid_desc_2001)
    assert "Incident description cannot exceed 2,000 words" in str(exc.value)


@pytest.mark.asyncio
async def test_10_empty_description_fail():
    with pytest.raises(ValidationError) as exc:
        IncidentCreate(title="Empty Description Test", description="   ")
    assert "Incident description is required" in str(exc.value)
