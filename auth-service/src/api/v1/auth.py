from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def login():
    print('yes')
    return {'status': 200, 'success': True}
