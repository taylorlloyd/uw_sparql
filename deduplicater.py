from SPARQLWrapper import SPARQLWrapper, JSON

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
    print('Predicate: ' + p)

