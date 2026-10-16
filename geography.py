"""Explicit country-name resolution shared by static and interactive maps."""
import pycountry

ALIASES={'United States':'USA','United Kingdom':'GBR','South Korea':'KOR','Russia':'RUS','Taiwan':'TWN','Hong Kong':'HKG','Iran':'IRN','Vietnam':'VNM','Turkey':'TUR','Türkiye':'TUR','Palestine':'PSE','Kosovo':None,'Northern Cyprus':None}

def country_codes(names):
    result={}
    for name in names:
        try:
            country=pycountry.countries.get(alpha_3=ALIASES[name]) if name in ALIASES else pycountry.countries.lookup(name)
            result[name]={'iso':country.alpha_3,'numeric':country.numeric} if country else None
        except LookupError:result[name]=None
    return result
