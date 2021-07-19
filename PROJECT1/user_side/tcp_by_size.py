SIZE_OF_LEN = 7


def send_by_size(sock,data,is_bytes = False):
    if is_bytes:
        data = str(len(data)).zfill(SIZE_OF_LEN).encode() + data
        sock.send(data)
    else:
        data = str(len(data)).zfill(SIZE_OF_LEN) + data
        sock.send(data.encode())


def recv_by_size(sock):
    """returns bytes. if data is string do data.decode()"""
    len_data = b''
    while len(len_data) < SIZE_OF_LEN:
        len_data += sock.recv(SIZE_OF_LEN)
        if len_data == '':
            return ''
    len_data = int(len_data.decode())
    data = b''
    while len(data) < len_data:
        new_data = sock.recv(len_data-len(data))
        data += new_data
        if data == '':
            return ''
    return data

