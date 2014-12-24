#!/bin/bash
#
# This script creates a patch file to perform surgery on an existing frontend.
# ./generate_patch.sh >netflix.patch
# patch --directory=/usr/local --strip=0 <netflix.patch

BASE=`git merge-base fixes/0.27 netflix`

(echo "import os" && echo "SHARE_DIR=os.path.join(os.path.dirname(os.path.realpath(__file__)), '../share/mythtv')") | git diff --exit-code --no-index --relative=- --dst-prefix=bin/lircfirefox_config.py /dev/null -
git diff --exit-code --relative=mythplugins/mythnetvision/firefox --src-prefix=bin/ --dst-prefix=bin/ "$BASE" netflix mythplugins/mythnetvision/firefox/lircfirefox.py
git diff --exit-code --relative=mythplugins/mythnetvision/firefox --src-prefix=share/mythtv/mythnetvision/ --dst-prefix=share/mythtv/mythnetvision/ "$BASE" netflix mythplugins/mythnetvision/firefox/lirc.firefox
git diff --exit-code --relative=mythplugins/mythnetvision/theme/menus --src-prefix=share/mythtv/ --dst-prefix=share/mythtv/ "$BASE" netflix mythplugins/mythnetvision/theme/menus/netvisionmenu.xml
git diff --exit-code --src-prefix=share/ --dst-prefix=share/ "$BASE" netflix mythtv/themes/Terra/menu-ui.xml mythtv/themes/defaultmenu/library.xml
git diff --exit-code --text --src-prefix=share/ --dst-prefix=share/ "$BASE" netflix mythtv/themes/default/Netflix_Web_Logo.jpg mythtv/themes/default/amazon.jpg mythtv/themes/default/dailyshow.jpg mythtv/themes/Terra/watermarks/internet.jpg
