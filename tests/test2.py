from pydeb import Pack
from os import remove

for i in ['xz', 'bzip2', 'gzip', 'zstd']:
    print('Packing using ' + i + ' algorithm.')
    Pack('./org.coolstar.sileo_2.3_iphoneos-arm', i)
    print('Done.\n------------------\n\n')
    remove('./org.coolstar.sileo_2.3_iphoneos-arm.deb')
