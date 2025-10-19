import asyncio
from services.document_manager import DocumentManager
from services.database_service import DatabaseService
from models.database_models import User
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

async def test_upload():
    # 1. User ID만 가져오기 (세션 닫기)
    db = DatabaseService()
    with db.get_session() as session:
        user = session.query(User).first()
        if not user:
            user = User(email='test@test.com', name='Test')
            session.add(user)
            session.commit()
            session.refresh(user)  # ID 확실히 가져오기
        user_id = user.id
    
    print(f'User ID: {user_id}')
    
    # 2. PDF 생성
    pdf_path = 'test_doc.pdf'
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.drawString(100, 750, 'SynapseSimple Test Document')
    c.drawString(100, 730, 'AI is computer learning technology.')
    c.drawString(100, 710, 'Machine learning learns from data.')
    c.showPage()
    c.save()
    
    print(f'PDF created: {pdf_path}')
    
    # 3. Upload - 전체 경로 사용
    manager = DocumentManager()
    
    try:
        full_path = os.path.abspath(pdf_path)
        result = await manager.upload_document(
            file_path=full_path,
            user_id=user_id
        )
        
        print('Upload complete!')
        print(f'  Document ID: {result["document_id"]}')
        print(f'  Chunks: {result["chunk_count"]}')
        print(f'  Vectors: {result["vector_count"]}')
        print(f'  Status: {result["status"]}')
        
    except Exception as e:
        print(f'Upload failed: {e}')
        import traceback
        traceback.print_exc()
    
    # 4. Cleanup
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

asyncio.run(test_upload())