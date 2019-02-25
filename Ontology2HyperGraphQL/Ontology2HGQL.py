import rdflib
from rdflib import Graph
import os

class Ontology2HGQL():

    def __init__(self, Ontology):
        self.ontology = Ontology
        if os.path.isdir(Ontology):
            self.fullGraph = self.parseFolder()
        else:
            self.fullGraph = self.parseGraph()
        self.HyperGraphQL = self.HyperSchema()

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

    def parseFolder(self):
        g = Graph()
        for root, dirs, files in os.walk(self.ontology):
            for file in files:
                if file.endswith(".rdf"):
                    graph = os.path.join(root, file)
                    g.parse(graph)

        return g

    def config(self,g):
        TypeDict = {}
        PropDict = {}
        subClassDict = {}

        classes = g.query(
            """SELECT ?s ?p ?o
               WHERE {
                  ?s ?p ?o
               }""")

        properties = g.query("""SELECT ?prop ?propType ?domain ?range
               WHERE {
                  ?prop a ?propType.
                  ?prop rdfs:domain ?domain.
                  ?prop rdfs:range ?range
               }""")

        subclasses = g.query(
            """SELECT ?s ?parent
               WHERE {
                  ?s rdfs:subClassOf ?parent.
               }""")

        for row in classes:
            for item in row:
                if type(item) == rdflib.term.URIRef:
                    if '#' in item:
                        label = item.split('#')
                        if label != 'string':
                            TypeDict[label[1]] = {'uri': str(item)}

        for row in properties:
            prop = row[0]
            propType = row[1]
            domain = row[2]
            range = row[3]
            label = prop.split('#')[1]
            PropDict[label] = {'uri': str(prop), 'type': str(propType), 'domain': str(domain), 'range': str(range)}

        for row in subclasses:
            if type(row[1]) == rdflib.term.URIRef:
                rdfClass = row[0].split('#')[1]
                rdfSuperclass = row[1]
                subClassDict[rdfClass] = {'superClass': str(rdfSuperclass)}

        return TypeDict, PropDict, subClassDict

    def HyperSchema(self):
        rdftypeDict, rdfpropDict, rdfsubclassDict = self.config(self.fullGraph)
        schemaString = str('')
        added_types = []
        added_context = []
        schemaString+=str("type __Context {" + '\n')
        for label, info in rdftypeDict.items():
            if label not in added_context and len(label) > 0:
                schemaString += str('\t' + label + ':' + '\t' + '\t' + '_@href(iri: "' + info['uri'] + '")' + '\n')
                added_context.append(label)
        schemaString += str('}\n\n')

        for label, info in rdftypeDict.items():
            schemaString += str('type ' + label + ' @service(id:"icdd-local") {\n')
            added_types.append(label)
            for propLabel, propInfo in rdfpropDict.items():
                if propInfo['domain'] == info['uri']:
                    rangeLabel = propInfo['range'].split('#')[1]
                    if rangeLabel == 'string':
                        rangeLabel = 'String'
                    if len(rangeLabel) > 0:
                        schemaString += str('\t' + propLabel + ': [' + rangeLabel + '] @service(id:"icdd-local")\n')

            for item, superItem in rdfsubclassDict.items():
                if item == label:
                    for propLabel, propInfo in rdfpropDict.items():
                        if propInfo['domain'] == superItem['superClass']:
                            rangeLabel = propInfo['range'].split('#')[1]
                            if rangeLabel == 'string':
                                rangeLabel = 'String'
                            schemaString += str('\t' + propLabel + ': [' + rangeLabel + '] @service(id:"icdd-local")\n')
            schemaString += str('}\n\n')
        return str(schemaString)

if __name__ == "__main__":
    main()