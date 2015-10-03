from SPARQLWrapper import SPARQLWrapper, JSON
from math import sqrt

sparql = SPARQLWrapper('http://husky-big.cs.uwaterloo.ca:8890/sparql')
dataset = '<http://data.nytimes.com>'

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
      subjects[s][p] = [o]
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

