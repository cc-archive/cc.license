import RDF

def query_to_single_value(model, subject, predicate, object):
    query = RDF.Statement(subject, predicate, object)
    results = list(model.find_statements(query))
    assert len(results) == 1

    # Assume either s, p, or o is None
    # so that would be what we want back.
    is_none = [thing for thing in ('subject', 'predicate', 'object')
               if (eval(thing) is None)]
    assert len(is_none) == 1
    return uri2value(getattr(results[0], is_none[0]))

def to_bool(s):
    s = s.lower()
    assert s in ('true', 'false')
    return {'true': True, 'false': False}[s]

type2converter = {
    'http://www.w3.org/2001/XMLSchema-datatypes#boolean': to_bool,
}

def uri2value(uri):
    if uri.type == 1: # Is there a list of these somewhere?
        # a URI
        return str(uri.uri)
    if uri.type == 2:
        # It's a literal - but what kind?
        literal = uri.literal_value
        strvalue = uri.literal_value['string']
        type = literal['datatype']
        type = str(type)
        return type2converter.get(type, lambda thing: thing)(strvalue)
    raise "Your mom"

def init_model(filename):
    ''' Input: An RDF.Uri() to start from.
    Output: A model with that sucker parsed. '''
    assert ':/' not in filename # not a URI

    storage=RDF.Storage(storage_name="hashes",
                    name="test",
                    options_string="new='yes',hash-type='memory',dir='.'")
    if storage is None:
      raise "new RDF.Storage failed"

    model=RDF.Model(storage)
    if model is None:
      raise "new RDF.model failed"

    parser = RDF.Parser('raptor')
    filename_uri = RDF.Uri(string="file:" + filename)
    parser.parse_into_model(model, filename_uri)
    return model

