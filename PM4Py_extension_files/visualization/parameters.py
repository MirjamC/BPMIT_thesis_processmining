'''
    This file is part of PM4Py (More Info: https://pm4py.fit.fraunhofer.de).

    PM4Py is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    PM4Py is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with PM4Py.  If not, see <https://www.gnu.org/licenses/>.
'''
from enum import Enum


class Parameters(Enum):
    FORMAT = "format"   
    RULES = "rules"
    UNIQUE = "unique_list"
    MIN_PERC_RULES = "min_perc_rules"
    MIN_PERC_CONF = "min_perc_conf"
    VISUALIZATION_OPTION = "visualization_option"
    DETAILS_OPTION = "detail_option"
    GRADIENT1 = "color_min"
    GRADIENT2 = "color_max"
