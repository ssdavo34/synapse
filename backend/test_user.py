from services.database_service import DatabaseService
from models.database_models import User

db = DatabaseService()

# context manager 방식으로 사용
with db.get_session() as session:
    # User 생성
    user = User(
        email='test@example.com',
        name='Test User'
    )
    session.add(user)
    session.commit()
    
    print(f'User created successfully!')
    print(f'   ID: {user.id}')
    print(f'   Email: {user.email}')
    print(f'   Name: {user.name}')
    
    # 조회 확인
    found = session.query(User).filter_by(email='test@example.com').first()
    print(f'User found: {found.name}')
