# In-Memory DB (Python)

간단한 파이썬 기반 인메모리 데이터베이스 구현 프로젝트입니다.

## 특징

- 메모리 내에서 데이터 저장 및 조회
- Key-Value 형태의 데이터 관리
- CRUD(생성, 조회, 수정, 삭제) 지원
- 데이터 만료 시간(TTL) 지원
- 외부 의존성 없이 순수 파이썬 구현

## 설치

```bash
git clone https://github.com/your-username/py-in-mem.git
cd py-in-mem
```

## 사용 예시

```python
from MemDB import inMemoryDB

db = inMemoryDB()
db.put('user:1', {'name': 'Alice', 'age': 30})
print(db.get('user:1'))  # {'name': 'Alice', 'age': 30}

db.put('user:1', {'name': 'Alice', 'age': 31})  # 값 수정
print(db.get('user:1'))  # {'name': 'Alice', 'age': 31}

print(db.exists('user:1'))  # True
print(db.keys())            # ['user:1']
print(db.size())            # 1

db.delete('user:1')
print(db.get('user:1'))     # None
```

## API

- `put(key, value, expiration_time=None)` : 키에 값을 저장합니다. expiration_time을 지정하면 해당 시간(초) 후에 데이터가 만료됩니다. 
  - expiration_time이 None이면 기본값 7초로 설정됩니다.
- `get(key)` : 키로 값을 조회합니다.
- `delete(key)` : 키-값 쌍을 삭제합니다.
- `clear()` : 데이터베이스의 모든 데이터를 삭제합니다.
- `exists(key)` : 키의 존재 여부를 확인합니다.
- `keys()` : 모든 키 목록을 반환합니다.
- `values()` : 모든 값 목록을 반환합니다.
- `items()` : 모든 키-값 쌍을 반환합니다.
- `size()` : 데이터베이스에 저장된 항목 수를 반환합니다.
- `exit()` : 커맨드 인터페이스를 종료합니다.

## 라이선스

Apache License 2.0