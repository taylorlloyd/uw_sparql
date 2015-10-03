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

def all_data_for_pred(dataset, predicate):
  sparql.setQuery("""
    select ?s ?o
    from %s
    where {
      ?s <%s> ?o
    }""" % (dataset, predicate))
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()

def all_predicates(dataset):
  sparql.setQuery("""
    select distinct ?p
    from %s
    where {
      ?s ?p ?o
    }""" % dataset)
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()

# Begin by retrieving all available predicates
data = all_predicates(dataset)
preds = map((lambda r: r['p']['value']), data['results']['bindings'])

print('%d predicates found.' % len(preds))

for p in preds:
    pdata = all_data_for_pred(dataset, p)
    print('Predicate %s: %d entries' % (p, len(pdata['results']['bindings'])))
    max_bucket_size = sqrt(len(pdata['results']['bindings']))
    buckets = {}

    # Sort entries into hashed buckets
    for d in pdata['results']['bindings']:
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




