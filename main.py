import subprocess
from Cryptodome.Cipher import AES, DES
from Cryptodome.Hash import MD4

subprocess.call(['psexec.exe', '-s', 'reg', 'export', 'HKLM\\SAM\\SAM', '%cd%\\sam.reg', '/y'], shell=True)
with open("sam.reg", 'r', encoding='utf-16-le', errors='ignore') as file:
    lines = file.read().splitlines()
    
users = []
vs = {}
# i hate this
for idx, line in enumerate(lines):
    if line == r'[HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account]':
        idx2 = idx
        while not '"F"=' in lines[idx2]:
            idx2 += 1
        fd = lines[idx2].split(":")[1]
        idx2 += 1
        while '=' not in lines[idx2]:
            fd += lines[idx2]
            idx2 += 1
        fd = fd.replace('\\', '').replace(' ', '').replace(',', '')
    if '[HKEY_LOCAL_MACHINE\\SAM\\SAM\\Domains\\Account\\Users\\Names\\' in line:
        users.append([line.split('\\')[-1][:-1], lines[idx+1].split('(')[1].split(')')[0].zfill(8)])
    if '[HKEY_LOCAL_MACHINE\\SAM\\SAM\\Domains\\Account\\Users\\0' in line:
        idx2 = idx
        while not '"V"=' in lines[idx2]:
            idx2 += 1
        v = lines[idx2].split(":")[1]
        idx2 += 1
        while '=' not in lines[idx2]:
            v += lines[idx2]
            idx2 += 1
        v = v.replace('\\', '').replace(' ', '').replace(',', '')
        vs[line.split('\\')[-1][:-1].lower()] = v

print("Please select a user:")
for idx, val in enumerate(users):
    print(f'[{idx}] {val[0]} ({val[1]})')
idx = input(': ')
user = None
try:
    user = users[int(idx)]
except IndexError:
    print("Invalid index")
    quit()
v = vs[user[1]]
rrid = user[1]

fd = bytearray.fromhex(fd)
v = bytearray.fromhex(v)
rid = int.from_bytes(bytearray.fromhex(rrid))

with open("lsa.txt", 'r', encoding='utf-8', errors='ignore') as file:
    text = file.read()

jd = ''
skew1 = ''
gbg = ''
data = ''

lines = text.splitlines()
for idx, line in enumerate(lines[:-1]):
    cls = lines[idx+1].split(':')[-1].strip()
    match line.split('\\')[-1]:
        case 'GBG':
            gbg = cls
        case 'Skew1':
            skew1 = cls
        case 'Data':
            data = cls
        case 'JD':
            jd = cls

lsa_key = bytearray(range(16))
scrambled = bytearray.fromhex(jd + skew1 + gbg + data)
for i, j in enumerate([8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7]):
    lsa_key[i] = scrambled[j]

print('LSA key (L):', lsa_key.hex())

length = int.from_bytes(fd[0x74:0x78], 'little')
cipher = AES.new(lsa_key, AES.MODE_CBC, iv=fd[0x78:0x88])
boot_key = cipher.decrypt(fd[0x88:0x88+length])[:16]

print("Boot key (B):", boot_key.hex())

offset = int.from_bytes(v[0xa8:0xac], 'little') + 0xCC
length = int.from_bytes(v[0xac:0xb0], 'little')
og_nt_hash = v[offset:offset+length]
cipher = AES.new(boot_key, AES.MODE_CBC, iv=og_nt_hash[0x08:0x18])
og_nt_hash2 = cipher.decrypt(og_nt_hash[0x18:])[:16]

rid = rid.to_bytes(32, 'little')
obf_keys = [
    [rid[i] for i in [0, 1, 2, 3, 0, 1, 2]],
    [rid[i] for i in [3, 0, 1, 2, 3, 0, 1]]
]
for i, j in enumerate(obf_keys):
    # dont look here this code is ass
    key = []
    for k, l in enumerate([0x1, 0x3, 0x7, 0xf, 0x1f, 0x3f]):
        key.append((j[k] & l) << (6 - k) | j[k + 1] >> (k + 2))
    key = [j[0] >> 1, *key, j[6] & 0x7f]
    obf_keys[i] = bytearray([(i << 1) & 0xfe for i in key])

print("Obf. keys (K):", *map(lambda i: i.hex(), obf_keys))

cipher = [DES.new(key, DES.MODE_ECB) for key in obf_keys]
og_nt_hash2 = cipher[0].decrypt(og_nt_hash2[:8]) + cipher[1].decrypt(og_nt_hash2[8:])

print("NT hash (NT):", og_nt_hash2.hex())

print("Start with \"p:\" to enter a password instead. (ex. p:mylogin)")
nt_hash = input("Enter new NT hash: ")
if nt_hash.startswith('p:'):
    nt_hash = MD4.new(nt_hash[2:].encode('utf-16-le')).hexdigest()
nt_hash = bytearray.fromhex(nt_hash)
print("new NT hash (NT):", nt_hash.hex())

cipher = [DES.new(key, DES.MODE_ECB) for key in deobf_keys]
nt_hash = cipher[0].encrypt(nt_hash[:8]) + cipher[1].encrypt(nt_hash[8:])
nt_hash += b'\x10' * 16
cipher = AES.new(boot_key, AES.MODE_CBC, iv=og_nt_hash[0x08:0x18])
nt_hash = cipher.encrypt(nt_hash)

for i, ch in enumerate(nt_hash):
    v[offset + i + 0x18] = ch

with open("hashenc.reg", 'w') as file:
    file.write(rf'''Windows Registry Editor Version 5.00
[HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users\{rrid}]

"V"=hex:{v.hex(',')}
''')

print("Saved as a .reg file \"hashenc.reg\"")

if input("Apply? (Y/N) ").lower() == 'y':
    subprocess.call(['psexec.exe', '-s', 'reg', 'import', '%cd%\\hashenc.reg'], shell=True)
