# -*- mode: python -*-

import site;
for path in site.getsitepackages():
    test_path = os.path.join(path, 'pyxform/odk_validate/ODK_Validate.jar')
    if os.path.exists(test_path):
        validate_path = test_path

a = Analysis(['../src/main.py'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          [('res\\about.html', os.getcwd() + '\\src\\res\\about.html', 'DATA')],
          [('pyxform\\odk_validate\\ODK_Validate.jar', validate_path, 'DATA')],
          name='ODK XLSForm Offline.exe',
          icon='pkg\\icon.ico',
          upx=True,
          console=False
)