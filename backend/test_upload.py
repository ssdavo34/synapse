import asyncio
from services.document_manager import DocumentManager
from services.database_service import DatabaseService
from models.database_models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

async def test_upload():
    # 1. User
    db = DatabaseService()
    with db.get_session() as session:
        user = session.query(User).first()
        if not user:
            user = User(email='test@test.com', name='Test')
            session.add(user)
            session.commit()
        user_id = user.id
    
    print(f'User ID: {user_id}')
    
    # 2. PDF
    pdf_path = 'test_doc.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, 'SynapseSimple Test Document')
    c.drawString(100, 730, 'AI is computer learning technology.')
    c.drawString(100, 710, 'Machine learning learns from data.')
    c.showPage()
    c.save()
    
    print(f'PDF created: {pdf_path}')
    
    # 3. Upload
    manager = DocumentManager()

    result = await manager.upload_document(
        file_path=pdf_path,
        user_id=user_id,
        title='Test Document'  # filename → title로 변경 (선택적)
    )
    
    if result.get("success"):
        print(f'✅ Upload complete!')
        print(f'  Document ID: {result["document_id"]}')
        print(f'  Title: {result["title"]}')
        print(f'  Chunks: {result["chunk_count"]}')
        print(f'  Vectors: {result["vector_count"]}')
        print(f'  Pages: {result["page_count"]}')
        print(f'  Text length: {result["text_length"]} chars')
    else:
        print(f'❌ Upload failed!')
        print(f'  Error: {result.get("error")}')
        print(f'  Step: {result.get("step")}')
    
    # 4. Cleanup
    os.remove(pdf_path)

asyncio.run(test_upload())