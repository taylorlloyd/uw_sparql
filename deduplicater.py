from SPARQLWrapper import SPARQLWrapper, JSON
from math import sqrt

sparql = SPARQLWrapper('http://husky-big.cs.uwaterloo.ca:8890/sparql')
dataset = '<http://data.nytimes.com>'
months = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]

#-------------PAIRWISE COMPARISON---------------

def edit_distance(s1, s2):
  m=len(s1)+1
  n=len(s2)+1

  tbl = {}
  for i in range(m): tbl[i,0]=i
  for j in range(n): tbl[0,j]=j
  for i in range(1, m):
   for j in range(1, n):
     cost = 0 if s1[i-1] == s2[j-1] else 1
     tbl[i,j] = min(tbl[i, j-1]+1, tbl[i-1, j]+1, tbl[i-1, j-1]+cost)

  return tbl[i,j]

def string_compare(s1, s2):
  return pow(edit_distance(s1,s2)/(len(s1) + len(s2)), 2)

def percent_difference(i1, i2):
  return abs(2*(i1 - i2)/(i1 + i2))

def int_compare(i1, i2):
  return min(percent_difference(i1,i2), string_compare(str(i1),str(i2)))

def parse_date(d):
  map(lambda n: int(n), d.split('-'))

# PRECONDITION: d1, d2 given as strings in format 'yyyy-mm-dd'
def date_difference(d1, d2):
  y1, m1, d1 = parse_date(d1)
  y2, m2, d2 = parse_date(d1)
 
  if(abs(y1-y2) > 1):
    return 1

  if(y1 == y2):
    return (abs(months[m1 - 1] + d1 - months[m2 - 1] - d2))/366.0
  elif(y1 > y2):
    return ((366 - months[m2 - 1] - d2) + months[m1 - 1] + d1)/366.0
  elif(y2 > y1):
    return ((366 - months[m1 - 1] - d1) + months[m2 - 1] + d2)/366.0
  

def date_compare(d1, d2):
  return min(string_compare(d1,d2), date_difference(d1,d2))



#--------------QUERY CODE------------------------
def all_data(dataset):
  sparql.setQuery("""
    select *
    from %s
    where {
      ?s ?p ?o
    }""" % dataset)
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()

def all_data_for_subjects(dataset, subjects):
  joined = '<' + '>,<'.join(subjects) + '>';
  query = """
    select ?s ?p ?o
    from %s
    where {
      ?s ?p ?o
      filter(?s in (%s))
    }""" % (dataset, joined)
  sparql.setQuery(query)
  sparql.setReturnFormat(JSON)
  response = sparql.query().convert()

  subjects = {}
  for e in response['results']['bindings']:
    s = e['s']['value']
    p = e['p']['value']
    o = e['o']['value']
    if s not in subjects:
      subjects[s] = {}

    if p in subjects[s]:
      if type(subjects[s][p]) is not list:
        subjects[s][p] = [subjects[s][p]]
      subjects[s][p].append(o)
    else:
      subjects[s][p] = o
  return subjects


def all_data_for_pred(dataset, predicate):
  sparql.setQuery("""
    select ?s ?o
    from %s
    where {
      ?s <%s> ?o
    }""" % (dataset, predicate))
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()['results']['bindings']

def all_predicates(dataset):
  sparql.setQuery("""
    select distinct ?p
    from %s
    where {
      ?s ?p ?o
    }""" % dataset)
  sparql.setReturnFormat(JSON)
  data = sparql.query().convert()
  return map((lambda r: r['p']['value']), data['results']['bindings'])

def pairwise_cmp(subjects):
  for s1 in subjects:
    for s2 in subjects:
      if compare(subjects[s1], subjects[s2]):
        print("Duplicate: %s and %s" % (s1, s2))

def compare(a, b):
  return False

# Begin by retrieving all available predicates
preds = all_predicates(dataset)
print('%d predicates found.' % len(preds))

for p in preds:
    pdata = all_data_for_pred(dataset, p)
    print('Predicate %s: %d entries' % (p, len(pdata)))
    max_bucket_size = sqrt(len(pdata))
    buckets = {}

    # Sort entries into hashed buckets
    for d in pdata:
        subject = d['s']['value']
        obj = d['o']['value']
        h = hash(obj)
        if(h not in buckets):
            buckets[h] = []
        buckets[h].append(subject)

    # Print out bucket metrics
    print("%d buckets generated" % len(buckets.keys()))
    usable = 0
    for i, val in enumerate(buckets):
        size = len(buckets[val])
        if(size > 1 and size < max_bucket_size):
          print("  bucket %d: %d entries" % (i, size))
          bucket = all_data_for_subjects(dataset, buckets[val])
          pairwise_cmp(bucket)

