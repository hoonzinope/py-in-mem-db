# In-Memory DB (Python)

간단한 파이썬 기반 인메모리 데이터베이스 구현 프로젝트입니다.

## 특징

- 메모리 내에서 데이터 저장 및 조회
- Key-Value 형태의 데이터 관리
- CRUD(생성, 조회, 수정, 삭제) 지원
- 데이터 만료 시간(TTL) 지원 (active 만료 + 백그라운드 스레드 방식)
- 외부 의존성 없이 순수 파이썬 구현

## 만료(TTL) 기능

- 각 데이터 항목은 만료 시간(TTL, Time-To-Live)을 가질 수 있습니다.
- 두 가지 만료 방식이 적용됩니다:
    - **lazy expire**: 데이터를 조회(get 등)할 때마다 만료 여부를 확인하여, 만료된 데이터는 자동으로 삭제되고 None을 반환합니다.
    - **active expire**: 별도의 백그라운드 스레드가 주기적으로 만료된 데이터를 자동으로 삭제합니다.
- 이를 통해 만료된 데이터가 즉시 또는 주기적으로 정리됩니다.

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
- `get(key)` : 키로 값을 조회합니다. 만료된 데이터는 자동으로 삭제되고 None을 반환합니다.
- `delete(key)` : 키-값 쌍을 삭제합니다.
- `clear()` : 데이터베이스의 모든 데이터를 삭제합니다.
- `exists(key)` : 키의 존재 여부를 확인합니다. 만료된 데이터는 False를 반환합니다.
- `keys()` : 모든 키 목록을 반환합니다(만료된 데이터는 제외).
- `values()` : 모든 값 목록을 반환합니다(만료된 데이터는 제외).
- `items()` : 모든 키-값 쌍을 반환합니다(만료된 데이터는 제외).
- `size()` : 데이터베이스에 저장된 항목 수를 반환합니다(만료된 데이터는 제외).
- `exit()` : 커맨드 인터페이스를 종료합니다.

## 라이선스

Apache License 2.0