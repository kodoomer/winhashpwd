from Cryptodome.Hash import MD4
print('hash:', MD4.new(input('password: ').encode('utf-16-le')).hexdigest())
