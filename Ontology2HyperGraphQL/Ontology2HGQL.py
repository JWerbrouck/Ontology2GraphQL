import rdflib
from rdflib import Graph
import os

class Ontology2HGQL():
    # initialize
    def __init__(self, Ontology):
        # the ontology that is passed could be either an ontology file or a folder that contains multiple different ontologies (e.g. all ontologies in an ICDD 'Ontology resources' folder
        self.ontology = Ontology

        # scenario if the passed ontology is a folder
        if os.path.isdir(Ontology):
            self.fullGraph = self.parseFolder()

        #scenario if the passed ontology is a single graph
        else:
            self.fullGraph = self.parseGraph()
        self.HyperGraphQL = self.HyperSchema()

    # parses an ontology graph that is passed
    # returns the graph to the self.fullGraph
    def parseGraph(self):
        g = Graph()
        graph_format = rdflib.util.guess_format(self.ontology)
        try:
            if self.ontology[0] == '"':
                initialgraph = self.ontology[1:-1]
            else:
                initialgraph = self.ontology
            g.parse(initialgraph, format=graph_format)
            return g

        except:
            print('failed to parse this file')

    # workaround if a full folder is passed: each ontology in the folder is parsed into the same local graph g
    # ('try - except' functionality to be added)
    # returns the entire graph to self.fullGraph
    def parseFolder(self):
        g = Graph()
        for root, dirs, files in os.walk(self.ontology):
            for file in files:
                if file.endswith(".rdf"):
                    graph = os.path.join(root, file)
                    g.parse(graph)

        return g

    # configuration file that queries the self.fullGraph for terms to use in the HypergraphQL schema
    # called via the HyperSchema function
    # returns 3 dictionaries:
    #       (1) Types to be constructed
    #       (2) Properties to be mapped to the types, and the 'range' of these properties
    #       (3) Subclasses of certain types, that will inherit the properties that are mapped to their superclass

    def config(self,g):
        TypeDict = {}
        PropDict = {}
        subClassDict = {}

        # Query the ontology graph for every definition, so all can have a JSON context mapped to them, to be used in the queries.
        GQLtypes = g.query(
            """SELECT ?s ?p ?o
               WHERE {
                  ?s ?p ?o
               }""")

        # Each result in the graph that is an URIRef (so Literals are not included), is added to the TypeDict
        # (key = label, e.g. 'Building', value is {'uri': https://w3id.org/bot#Building}')
        # I admit that the mapping in the dict could be more efficient, since there is only 1 key-value pair
        for row in GQLtypes:
            for item in row:
                if type(item) == rdflib.term.URIRef:
                    if '#' in item:
                        label = item.split('#')
                        if label != 'string':
                            TypeDict[label[1]] = {'uri': str(item)}

        # search for properties, their domain and range. Additionally (but unused at the moment), the propertytypes are queried for as well.
        # each of the results is then mapped in a subdictionary
        # (key = label, e.g. 'hasBuilding', value is {'uri': https://w3id.org/bot#hasBuilding, 'type': 'owl:ObjectProperty', 'domain: 'bot:Zone', 'range': 'bot:Building'}')
        properties = g.query("""SELECT ?prop ?propType ?domain ?range
               WHERE {
                  ?prop a ?propType.
                  ?prop rdfs:domain ?domain.
                  ?prop rdfs:range ?range
               }""")

        for row in properties:
            prop = row[0]
            propType = row[1]
            domain = row[2]
            range = row[3]
            label = prop.split('#')[1]
            PropDict[label] = {'uri': str(prop), 'type': str(propType), 'domain': str(domain), 'range': str(range)}


        # search for all the subclasses and their superclass
        subclasses = g.query(
            """SELECT ?s ?parent
               WHERE {
                  ?s rdfs:subClassOf ?parent.
               }""")

        for row in subclasses:
            if type(row[1]) == rdflib.term.URIRef:
                rdfClass = row[0].split('#')[1]
                rdfSuperclass = row[1]
                subClassDict[rdfClass] = {'superClass': str(rdfSuperclass)}

        return TypeDict, PropDict, subClassDict

    # function that uses the dictionaries from config to construct a HyperGraphQL schema
    # similarly, a GraphQL-LD context can be generated from only the first step
    def HyperSchema(self):
        TypeDict, PropDict, SubclassDict = self.config(self.fullGraph)

        # basic string that will be returned
        schemaString = str('')
        added_types = []
        added_context = []

        # write context for every item in the typedict.
        schemaString+=str("type __Context {" + '\n')
        for label, info in TypeDict.items():
            if label not in added_context and len(label) > 0:
                schemaString += str('\t' + label + ':' + '\t' + '\t' + '_@href(iri: "' + info['uri'] + '")' + '\n')
                added_context.append(label)
        schemaString += str('}\n\n')

        # construct a Type for every item in the typedict, and map the properties that have it as an rdfs:domain as fields
        # rdfs:range is used for the range of the fields
        # a local service is created here. Could be a user-input as well
        for label, info in TypeDict.items():
            schemaString += str('type ' + label + ' @service(id:"icdd-local") {\n')
            added_types.append(label)
            for propLabel, propInfo in PropDict.items():
                if propInfo['domain'] == info['uri']:
                    rangeLabel = propInfo['range'].split('#')[1]
                    if rangeLabel == 'string':
                        rangeLabel = 'String'
                    if len(rangeLabel) > 0:
                        schemaString += str('\t' + propLabel + ': [' + rangeLabel + '] @service(id:"icdd-local")\n')

            # If an property domain is equal to an item that has subclasses, this property is also added as a field to the subclasses of this field
            for item, superItem in SubclassDict.items():
                if item == label:
                    for propLabel, propInfo in PropDict.items():
                        if propInfo['domain'] == superItem['superClass']:
                            rangeLabel = propInfo['range'].split('#')[1]
                            if rangeLabel == 'string':
                                rangeLabel = 'String'
                            schemaString += str('\t' + propLabel + ': [' + rangeLabel + '] @service(id:"icdd-local")\n')
            schemaString += str('}\n\n')

        # return the entire schema as a string
        return str(schemaString)

if __name__ == "__main__":
    main()