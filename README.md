# In-Memory Key-Value DB with python

간단한 파이썬 기반 인메모리 key-value 데이터베이스 구현체 입니다.

## 버전
- Python 3.8 이상

## 특징

- 메모리 내에서 데이터 저장 및 조회
- Key-Value 형태의 데이터 관리
- CRUD(생성, 조회, 수정, 삭제) 지원
- 데이터 만료 시간(TTL) 지원 
  - (조회시 만료(lazy) + 주기적 만료 스레드(active) 방식)
- Lock 기반의 동시성 제어로 데이터 일관성 보장
- transaction (begin, commit, rollback) 지원
- backup 및 restore 기능
- alias 명령어 지원
- batch 명령어 지원 (한 번에 여러 명령어 실행)
- find 명령어 지원 (특정 패턴으로 key, value 검색)
- Logger 클래스를 통한 체계적인 로깅 지원
- 외부 의존성 없이 순수 파이썬 구현

#### 만료(TTL) 기능

- 각 데이터 항목은 만료 시간(TTL, Time-To-Live)을 가질 수 있습니다.
- 두 가지 만료 방식이 적용됩니다:
    - **lazy expire**: 데이터를 조회(get 등)할 때마다 만료 여부를 확인하여, 만료된 데이터는 자동으로 삭제되고 None을 반환합니다.
    - **active expire**: 별도의 백그라운드 스레드가 주기적으로 만료된 데이터를 자동으로 삭제합니다.
- 이를 통해 만료된 데이터가 즉시 또는 주기적으로 정리됩니다.

#### Lock 기반 동시성 제어

- 데이터베이스는 Lock 클래스를 사용하여 동시성 문제를 해결합니다.
- 모든 데이터 접근은 Lock을 통해 보호되며, 이를 통해 다중 스레드 환경에서도 데이터 일관성을 유지합니다.
- Lock은 `with` 문을 사용하여 자동으로 획득 및 해제됩니다.

#### Transaction 지원

- 데이터베이스는 트랜잭션을 지원합니다.
- `begin()`, `commit()`, `rollback()` 메서드를 통해 트랜잭션을 관리할 수 있습니다.
- 트랜잭션 내에서 수행된 모든 작업은 `commit()` 호출 시에만 실제로 적용됩니다.
- `rollback()`을 호출하면 트랜잭션 내의 모든 변경 사항이 취소됩니다.

#### backup 및 restore 기능
- 데이터베이스의 현재 상태는 백그라운드에서 주기적으로 백업됩니다.
  - (현재 상태는 ./meta-data/snapshot.db 파일에 저장됩니다.) 
- 데이터 변경 시마다 AOF(Append-Only File) 형식으로 로그가 기록됩니다.
  - (./meta-data/AOF.txt 파일에 저장됩니다.)
- 재 시작시 snapshot.db 파일과 AOF.txt 파일을 읽어 데이터베이스를 복원합니다.

#### alias 명령어 지원
- 사용자가 자주 사용하는 명령어에 대해 alias(별칭)를 설정할 수 있습니다.
- alias 정보는 `./meta-data/alias.json` 파일에 저장되어, 재 시작시 자동으로 로드됩니다.
- `show-alias` 명령어로 현재 설정된 alias 목록을 확인할 수 있습니다.
- 사용예시
```bash
cmd>> alias k keys
cmd>> k
['z', '2']
cmd>> alias i items
cmd>> i
[('z', '1'), ('2', '1')]
cmd>> show-alias
set: put
v: values
k: keys
i: items
cmd>> exit
Exiting...
```

#### batch 명령어 지원
- `batch` 명령어를 사용하여 여러 명령어를 한 번에 실행할 수 있습니다.
- 명령어는 `;`로 구분하며, 각 명령어는 별도의 줄에 작성할 수 있습니다.
- 자동으로 트랜잭션 모드로 실행되며, 모든 명령어가 성공적으로 실행되어야 커밋됩니다.
- cmd 모드와 file 모드 모두에서 지원됩니다.
  - 기본은 cmd 모드입니다.
  - option '-c' 또는 '--cmd'를 사용하여 커맨드 모드로 실행할 수 있습니다.
  - option '-f' 또는 '--file'을 사용하여 파일 모드로 실행할 수 있습니다.
- 예시:
```bash
cmd>> batch -c "put a 1 10000; put b 1 10000; get a; get b;"
Executing batch command not in transaction mode
[None, None, '1', '1']
cmd>> exit 
Exiting...
````

#### find 명령어 지원
- `find -[k,v] -[r,l] <search>` 명령어를 사용하여 특정 패턴으로 키를 검색할 수 있습니다.
  - option `-k` 또는 `--key`를 사용하여 키를 검색할 수 있습니다.
  - option `-v` 또는 `--value`를 사용하여 값을 검색할 수 있습니다.
  - option `-l` 또는 `--like`를 사용하여 와일드카드 패턴으로 검색할 수 있습니다.
  - option `-r` 또는 `--regex`를 사용하여 정규 표현식 패턴으로 검색할 수 있습니다.
- 예시:
```bash
cmd>> put a 1 10000
cmd>> put b 2 10000
cmd>> put c 1 10000
cmd>> items
[('a', '1'), ('b', '2'), ('c', '1')]
cmd>> find -k a
['a']
cmd>> find -k -l *
['a', 'b', 'c']
cmd>> exit
Exiting...

```

## 설치

```bash
git clone https://github.com/your-username/py-in-mem.git
cd py-in-mem
```

## 사용 예시

```bash
$ > python main.py
[2025-06-25 13:43:45]   [Command]       log:Command interface initialized
[2025-06-25 13:43:45]   [inMemoryDB]    log:Initialized in-memory database
Welcome to the in-memory database command interface!
Type 'help' for a list of commands.
cmd>> keys
['a', 'b', 'c']
cmd>> delete c
Appending to AOF: delete c
cmd>> exists c
False
cmd>> exit 
Exiting...
```

## API

- `put(key, value, expiration_time=None)` : 키에 값을 저장합니다. expiration_time을 지정하면 해당 시간(초) 후에 데이터가 만료됩니다. 
    - expiration_time이 None이면 기본값 7초로 설정됩니다.
- `get(key)` : 키로 값을 조회합니다. 만료된 데이터는 자동으로 삭제되고 None을 반환합니다.
- `delete(key)` : 키-값 쌍을 삭제합니다.
- `clear` : 데이터베이스의 모든 데이터를 삭제합니다.
- `exists(key)` : 키의 존재 여부를 확인합니다. 만료된 데이터는 False를 반환합니다.
- `keys` : 모든 키 목록을 반환합니다(만료된 데이터는 제외).
- `values` : 모든 값 목록을 반환합니다(만료된 데이터는 제외).
- `items` : 모든 키-값 쌍을 반환합니다(만료된 데이터는 제외).
- `size` : 데이터베이스에 저장된 항목 수를 반환합니다(만료된 데이터는 제외).
- `begin` : 트랜잭션을 시작합니다.
- `commit` : 트랜잭션을 커밋합니다. 트랜잭션 내의 모든 변경 사항이 적용됩니다.
- `rollback` : 트랜잭션을 롤백합니다. 트랜잭션 내의 모든 변경 사항이 취소됩니다.
- `exit` : 커맨드 인터페이스를 종료합니다.
- `show-alias` : 현재 설정된 alias 목록을 출력합니다.
- `alias <alias_name> <command>` : 명령어에 별칭을 설정합니다. 
  - 예: `alias k keys`는 `k`를 입력하면 `keys` 명령어를 실행합니다.
- `reset-alias` : 모든 alias를 초기화합니다.
- `batch <commands>` : 여러 명령어를 한 번에 실행합니다. 
  - 예: `batch put a 1; put b 2; get a; get b;`는 `put`과 `get` 명령어를 순차적으로 실행합니다.

## 라이선스

MIT License