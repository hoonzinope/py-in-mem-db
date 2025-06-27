
"""
This module defines the base class for codecs used in the resp protocol.
Simple String
+<string>\r\n
예: +OK\r\n

Error
-<error message>\r\n 예: -ERR unknown command\r\n

Integer
:<number>\r\n 예: :1000\r\n

Bulk String
$<length>\r\n<actual data>\r\n 예: $6\r\nfoobar\r\n

Array
*<number of elements>\r\n<element1>...<elementN>
예: *2\r\n$3\r\nGET\r\n$3\r\nkey\r\n

명령 예시
SET key value
*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n

GET key
*2\r\n$3\r\nGET\r\n$3\r\nkey\r\n

응답 예시
OK (Simple String)
+OK\r\n

값 (Bulk String)
$5\r\nvalue\r\n

NULL (Bulk String)
$-1\r\n

에러
-ERR unknown command\r\n
"""
import shlex

def encode(data):
    encode_data = ""
    parts = shlex.split(data)
    if not parts:
        return "*0\r\n"
    for part in parts:
        encode_data += f"${len(part)}\r\n{part}\r\n"
    return f"*{len(parts)}\r\n{encode_data}"

def decode(data):
    decode_data = []
    parts = data.split("\r\n")
    if len(parts) < 2 or not parts[0].startswith("*"):
        return None
    num_elements = int(parts[0][1:])
    if num_elements == 0:
        return decode_data
    for i in range(2, num_elements * 2 + 1, 2):
        length = int(parts[i-1][1:])
        if length == -1:
            decode_data.append(None)
        else:
            decode_data.append(parts[i][:length])
    return ' '.join(decode_data)


if __name__ == "__main__":
    encoded = encode("batch -c 'put key1 value1; put key2 value2; get key1'")
    print("Encoded:", encoded)
    decoded = decode(encoded)
    print("Decoded:", decoded)

