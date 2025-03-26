#!/usr/bin/env python
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Kevin B. Hendricks, Stratford Ontario Canada
# All rights reserved.
#
# This diffstat code was extracted and heavily modified from:
#
#  https://github.com/techtonik/python-patch
#      Under the following license:
#
#  Patch utility to apply unified diffs
#  Brute-force line-by-line non-recursive parsing
#
# Copyright (c) 2008-2016 anatoly techtonik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
import sys
from typing import Optional

# only needs to detect git style diffs as this is for
# use with dulwich

_git_header_name = re.compile(rb"diff --git a/(.*) b/(.*)")

_GIT_HEADER_START = b"diff --git a/"
_GIT_BINARY_START = b"Binary file"
_GIT_RENAMEFROM_START = b"rename from"
_GIT_RENAMETO_START = b"rename to"
_GIT_CHUNK_START = b"@@"
_GIT_ADDED_START = b"+"
_GIT_DELETED_START = b"-"
_GIT_UNCHANGED_START = b" "

# emulate original full Patch class by just extracting
# filename and minimal chunk added/deleted information to
# properly interface with diffstat routine


def _parse_patch(
    lines: list[bytes],
) -> tuple[list[bytes], list[bool], list[tuple[int, int]]]:
    """Parse a git style diff or patch to generate diff stats.

    Args:
      lines: list of byte string lines from the diff to be parsed
    Returns: A tuple (names, is_binary, counts) of three lists
    """
    names = []
    nametypes = []
    counts = []
    in_patch_chunk = in_git_header = binaryfile = False
    currentfile: Optional[bytes] = None
    added = deleted = 0
    for line in lines:
        if line.startswith(_GIT_HEADER_START):
            if currentfile is not None:
                names.append(currentfile)
                nametypes.append(binaryfile)
                counts.append((added, deleted))
            m = _git_header_name.search(line)
            assert m
            currentfile = m.group(2)
            binaryfile = False
            added = deleted = 0
            in_git_header = True
            in_patch_chunk = False
        elif line.startswith(_GIT_BINARY_START) and in_git_header:
            binaryfile = True
            in_git_header = False
        elif line.startswith(_GIT_RENAMEFROM_START) and in_git_header:
            currentfile = line[12:]
        elif line.startswith(_GIT_RENAMETO_START) and in_git_header:
            assert currentfile
            currentfile += b" => %s" % line[10:]
        elif line.startswith(_GIT_CHUNK_START) and (in_patch_chunk or in_git_header):
            in_patch_chunk = True
            in_git_header = False
        elif line.startswith(_GIT_ADDED_START) and in_patch_chunk:
            added += 1
        elif line.startswith(_GIT_DELETED_START) and in_patch_chunk:
            deleted += 1
        elif not line.startswith(_GIT_UNCHANGED_START) and in_patch_chunk:
            in_patch_chunk = False
    # handle end of input
    if currentfile is not None:
        names.append(currentfile)
        nametypes.append(binaryfile)
        counts.append((added, deleted))
    return names, nametypes, counts


# note must all done using bytes not string because on linux filenames
# may not be encodable even to utf-8
def diffstat(lines, max_width=80):
    """Generate summary statistics from a git style diff ala
       (git diff tag1 tag2 --stat).

    Args:
      lines: list of byte string "lines" from the diff to be parsed
      max_width: maximum line length for generating the summary
                 statistics (default 80)
    Returns: A byte string that lists the changed files with change
             counts and histogram.
    """
    names, nametypes, counts = _parse_patch(lines)
    insert = []
    delete = []
    namelen = 0
    maxdiff = 0  # max changes for any file used for histogram width calc
    for i, filename in enumerate(names):
        i, d = counts[i]
        insert.append(i)
        delete.append(d)
        namelen = max(namelen, len(filename))
        maxdiff = max(maxdiff, i + d)
    output = b""
    statlen = len(str(maxdiff))  # stats column width
    for i, n in enumerate(names):
        binaryfile = nametypes[i]
        # %-19s | %-4d %s
        # note b'%d' % namelen is not supported until Python 3.5
        # To convert an int to a format width specifier for byte
        # strings use str(namelen).encode('ascii')
        format = (
            b" %-"
            + str(namelen).encode("ascii")
            + b"s | %"
            + str(statlen).encode("ascii")
            + b"s %s\n"
        )
        binformat = b" %-" + str(namelen).encode("ascii") + b"s | %s\n"
        if not binaryfile:
            hist = b""
            # -- calculating histogram --
            width = len(format % (b"", b"", b""))
            histwidth = max(2, max_width - width)
            if maxdiff < histwidth:
                hist = b"+" * insert[i] + b"-" * delete[i]
            else:
                iratio = (float(insert[i]) / maxdiff) * histwidth
                dratio = (float(delete[i]) / maxdiff) * histwidth
                iwidth = dwidth = 0
                # make sure every entry that had actual insertions gets
                # at least one +
                if insert[i] > 0:
                    iwidth = int(iratio)
                    if iwidth == 0 and 0 < iratio < 1:
                        iwidth = 1
                # make sure every entry that had actual deletions gets
                # at least one -
                if delete[i] > 0:
                    dwidth = int(dratio)
                    if dwidth == 0 and 0 < dratio < 1:
                        dwidth = 1
                hist = b"+" * int(iwidth) + b"-" * int(dwidth)
            output += format % (
                bytes(names[i]),
                str(insert[i] + delete[i]).encode("ascii"),
                hist,
            )
        else:
            output += binformat % (bytes(names[i]), b"Bin")

    output += b" %d files changed, %d insertions(+), %d deletions(-)" % (
        len(names),
        sum(insert),
        sum(delete),
    )
    return output


def main() -> int:
    argv = sys.argv
    # allow diffstat.py to also be used from the command line
    if len(sys.argv) > 1:
        diffpath = argv[1]
        data = b""
        with open(diffpath, "rb") as f:
            data = f.read()
        lines = data.split(b"\n")
        result = diffstat(lines)
        print(result.decode("utf-8"))
        return 0

    # if no path argument to a diff file is passed in, run
    # a self test. The test case includes tricky things like
    # a diff of diff, binary files, renames with further changes
    # added files and removed files.
    # All extracted from Sigil-Ebook/Sigil's github repo with
    # full permission to use under this license.
    selftest = b"""
diff --git a/docs/qt512.7_remove_bad_workaround.patch b/docs/qt512.7_remove_bad_workaround.patch
new file mode 100644
index 00000000..64e34192
--- /dev/null
+++ b/docs/qt512.7_remove_bad_workaround.patch
@@ -0,0 +1,15 @@
+--- qtbase/src/gui/kernel/qwindow.cpp.orig     2019-12-12 09:15:59.000000000 -0500
++++ qtbase/src/gui/kernel/qwindow.cpp  2020-01-10 10:36:53.000000000 -0500
+@@ -218,12 +218,6 @@
+     QGuiApplicationPrivate::window_list.removeAll(this);
+     if (!QGuiApplicationPrivate::is_app_closing)
+         QGuiApplicationPrivate::instance()->modalWindowList.removeOne(this);
+-
+-    // focus_window is normally cleared in destroy(), but the window may in
+-    // some cases end up becoming the focus window again. Clear it again
+-    // here as a workaround. See QTBUG-75326.
+-    if (QGuiApplicationPrivate::focus_window == this)
+-        QGuiApplicationPrivate::focus_window = 0;
+ }
+
+ void QWindowPrivate::init(QScreen *targetScreen)
diff --git a/docs/testplugin_v017.zip b/docs/testplugin_v017.zip
new file mode 100644
index 00000000..a4cf4c4c
Binary files /dev/null and b/docs/testplugin_v017.zip differ
diff --git a/ci_scripts/macgddeploy.py b/ci_scripts/gddeploy.py
similarity index 73%
rename from ci_scripts/macgddeploy.py
rename to ci_scripts/gddeploy.py
index a512d075..f9dacd33 100644
--- a/ci_scripts/macgddeploy.py
+++ b/ci_scripts/gddeploy.py
@@ -1,19 +1,32 @@
 #!/usr/bin/env python3

 import os
+import sys
 import subprocess
 import datetime
 import shutil
+import glob

 gparent = os.path.expandvars('$GDRIVE_DIR')
 grefresh_token = os.path.expandvars('$GDRIVE_REFRESH_TOKEN')

-travis_branch = os.path.expandvars('$TRAVIS_BRANCH')
-travis_commit = os.path.expandvars('$TRAVIS_COMMIT')
-travis_build_number = os.path.expandvars('$TRAVIS_BUILD_NUMBER')
+if sys.platform.lower().startswith('darwin'):
+    travis_branch = os.path.expandvars('$TRAVIS_BRANCH')
+    travis_commit = os.path.expandvars('$TRAVIS_COMMIT')
+    travis_build_number = os.path.expandvars('$TRAVIS_BUILD_NUMBER')
+
+    origfilename = './bin/Sigil.tar.xz'
+    newfilename = './bin/Sigil-{}-{}-build_num-{}.tar.xz'.format(travis_branch, travis_commit[:7],travis_build_numbe\
r)
+else:
+    appveyor_branch = os.path.expandvars('$APPVEYOR_REPO_BRANCH')
+    appveyor_commit = os.path.expandvars('$APPVEYOR_REPO_COMMIT')
+    appveyor_build_number = os.path.expandvars('$APPVEYOR_BUILD_NUMBER')
+    names = glob.glob('.\\installer\\Sigil-*-Setup.exe')
+    if not names:
+        exit(1)
+    origfilename = names[0]
+    newfilename = '.\\installer\\Sigil-{}-{}-build_num-{}-Setup.exe'.format(appveyor_branch, appveyor_commit[:7], ap\
pveyor_build_number)

-origfilename = './bin/Sigil.tar.xz'
-newfilename = './bin/Sigil-{}-{}-build_num-{}.tar.xz'.format(travis_branch, travis_commit[:7],travis_build_number)
 shutil.copy2(origfilename, newfilename)

 folder_name = datetime.date.today()
diff --git a/docs/qt512.6_backport_009abcd_fix.patch b/docs/qt512.6_backport_009abcd_fix.patch
deleted file mode 100644
index f4724347..00000000
--- a/docs/qt512.6_backport_009abcd_fix.patch
+++ /dev/null
@@ -1,26 +0,0 @@
---- qtbase/src/widgets/kernel/qwidget.cpp.orig 2019-11-08 10:57:07.000000000 -0500
-+++ qtbase/src/widgets/kernel/qwidget.cpp      2019-12-11 12:32:24.000000000 -0500
-@@ -8934,6 +8934,23 @@
-         }
-     }
-     switch (event->type()) {
-+    case QEvent::PlatformSurface: {
-+        // Sync up QWidget's view of whether or not the widget has been created
-+        switch (static_cast<QPlatformSurfaceEvent*>(event)->surfaceEventType()) {
-+        case QPlatformSurfaceEvent::SurfaceCreated:
-+            if (!testAttribute(Qt::WA_WState_Created))
-+                create();
-+            break;
-+        case QPlatformSurfaceEvent::SurfaceAboutToBeDestroyed:
-+            if (testAttribute(Qt::WA_WState_Created)) {
-+                // Child windows have already been destroyed by QWindow,
-+                // so we skip them here.
-+                destroy(false, false);
-+            }
-+            break;
-+        }
-+        break;
-+    }
-     case QEvent::MouseMove:
-         mouseMoveEvent((QMouseEvent*)event);
-         break;
diff --git a/docs/Building_Sigil_On_MacOSX.txt b/docs/Building_Sigil_On_MacOSX.txt
index 3b41fd80..64914c78 100644
--- a/docs/Building_Sigil_On_MacOSX.txt
+++ b/docs/Building_Sigil_On_MacOSX.txt
@@ -113,7 +113,7 @@ install_name_tool -add_rpath @loader_path/../../Frameworks ./bin/Sigil.app/Content
 
 # To test if the newly bundled python 3 version of Sigil is working properly ypou can do the following:
 
-1. download testplugin_v014.zip from https://github.com/Sigil-Ebook/Sigil/tree/master/docs
+1. download testplugin_v017.zip from https://github.com/Sigil-Ebook/Sigil/tree/master/docs
 2. open Sigil.app to the normal nearly blank template epub it generates when opened
 3. use Plugins->Manage Plugins menu and make sure the "Use Bundled Python" checkbox is checked
 4. use the "Add Plugin" button to navigate to and add testplugin.zip and then hit "Okay" to exit the Manage Plugins Dialog
"""

    testoutput = b""" docs/qt512.7_remove_bad_workaround.patch            | 15 ++++++++++++
 docs/testplugin_v017.zip                            | Bin
 ci_scripts/macgddeploy.py => ci_scripts/gddeploy.py |  0 
 docs/qt512.6_backport_009abcd_fix.patch             | 26 ---------------------
 docs/Building_Sigil_On_MacOSX.txt                   |  2 +-
 5 files changed, 16 insertions(+), 27 deletions(-)"""

    # return 0 on success otherwise return -1
    result = diffstat(selftest.split(b"\n"))
    if result == testoutput:
        print("self test passed")
        return 0
    print("self test failed")
    print("Received:")
    print(result.decode("utf-8"))
    print("Expected:")
    print(testoutput.decode("utf-8"))
    return -1


if __name__ == "__main__":
    sys.exit(main())
