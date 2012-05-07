include ( ../../mythconfig.mak )
include ( ../../settings.pro )

TEMPLATE = app
CONFIG -= qt moc

lircfiles.path = $${PREFIX}/share/mythtv/mythnetvision
lircfiles.files = lirc.*

pyfiles.path = $${PREFIX}/bin
pyfiles.files = *.py

INSTALLS += lircfiles pyfiles

SOURCES += dummy.c
