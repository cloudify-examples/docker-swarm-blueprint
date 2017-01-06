
def under_to_camel(s):
  flag=False
  first=True
  out=""
  for c in s:
    if c == '_':
      flag=True
    else:
      out = out + c if not flag and not first else out + c.upper()
      flag=False
    first=False
  return out

def camelmap(mapin):
  out={}
  for k,v in mapin.iteritems():
    out[under_to_camel(k)]=v if type(v) != type(dict()) else camelmap(v)
  return out
