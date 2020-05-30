"""
 Copyright (C) 2020 biqqles.
 This Source Code Form is subject to the terms of the Mozilla Public
 License, v. 2.0. If a copy of the MPL was not distributed with this
 file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
from .decorator import dataclass, create_dataclass
from .dataclass import as_dict, as_tuple, fields, DataClass, Internal

# aliases for migration from dataclasses
asdict, astuple, make_dataclass = as_dict, as_tuple, create_dataclass
