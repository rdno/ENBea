# -*- coding: utf-8 -*-
import gettext
import os
fallback = True
if os.name == 'nt':
    from enbea import gettext_windows
    lang = gettext_windows.get_language()
    __trans = gettext.translation('enbea', localedir='locale', languages=lang, fallback=fallback)
else:
    __trans = gettext.translation('enbea', fallback=fallback)
i18n = __trans.ugettext
