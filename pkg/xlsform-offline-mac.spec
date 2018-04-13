# -*- mode: python -*-

import site;
for path in site.getsitepackages():
    test_path = os.path.join(path, 'pyxform/validators/odk_validate/bin/ODK_Validate.jar')
    if os.path.exists(test_path):
        validate_path = test_path

a = Analysis(['../src/main.py'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='ODK XLSForm Offline',
          console=False
)
coll = COLLECT(exe,
               a.binaries,
               [('res/about.html', os.getcwd() + '/src/res/about.html', 'DATA')],
               [('pyxform/validators/odk_validate/bin/ODK_Validate.jar', validate_path, 'DATA')],
               name='ODK XLSForm Offline',
               strip=True
)
app = BUNDLE(coll,
             name='ODK XLSForm Offline.app',
             icon='pkg/icon.icns',
             info_plist={ 'NSHighResolutionCapable': 'True' }
)