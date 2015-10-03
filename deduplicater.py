from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper('http://husky-big.cs.uwaterloo.ca:8890/sparql')
dataset = 'http://data.nytimes.com/'

def all_data(dataset):
  sparql.setQuery("""
    select *
    from %s
    where {
      ?s ?p ?o 
    }""" % dataset)
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()
  
def all_predicates(dataset):
  sparql.setQuery("""
    select count(distinct ?p)
    from %s
    where {
      ?s ?p ?o 
    }""" % dataset)
  sparql.setReturnFormat(JSON)
  return sparql.query().convert()


data = acquire_data(dataset)

