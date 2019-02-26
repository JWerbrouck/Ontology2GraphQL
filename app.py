from Ontology2HyperGraphQL.Ontology2HGQL import Ontology2HGQL
from rdflib import Graph
import os
import webbrowser

def ICDDtripleParser(ICDDfolder, HyperGraphQLFolder):
    TripleFolder = str(ICDDfolder + "\\Payload triples")
    graphs = list_files(ICDDfolder, "rdf")
    for item in list_files(TripleFolder, "rdf"): graphs.append(item)
    print(graphs)
    g = Graph()
    for graph in graphs:
        g.parse(graph)
    try:
        schemaLocation = str(HyperGraphQLFolder+"/src/main/resources/")
        g.serialize(destination=schemaLocation+'ICDD.ttl', format='turtle')
        print('serialized')
        return schemaLocation
    except:
        print('failed to serialize this graph')

def list_files(directory, extension):
    return [str(directory+'\\'+f) for f in os.listdir(directory) if f.endswith('.' + extension)]

def createConfig(location):
    configLocation = str(location + '/src/main/resources/configICDD.json')
    config = open(configLocation, "w+")
    configstr = str('{\n\t"name": "icdd-hgql",\n\t"schema": "schemaICDD.graphql",\n\t"server": {\n\t\t"port": 8082,\n\t\t"graphql": "/graphql",\n\t\t"graphiql": "/graphiql"\n\t},\n\t"services": [\n\t\t{\n\t\t\t"id": "icdd-local",\n\t\t\t"type": "LocalModelSPARQLService",\n\t\t\t"filepath": "src/main/resources/ICDD.ttl",\n\t\t\t"filetype": "TTL"\n\t\t}\n\t]\n}')
    config.write(configstr)

    return configLocation

# primary function
def ICDDquerier():
    """ICDDfolder = str("C:/Users/[username]/Documents/ICDD/usecase_1b_delivery")"""
    # asks user where the ICDD container is located
    ICDDfolder = input("please give the location of the (unzipped) ICDD container:")
    OntoFolder = str(ICDDfolder + "\\Ontology resources")
    """HyperGraphQLFolder = str("C:/Users/[username]/hypergraphql-master")"""
    HyperGraphQLFolder = input("please give the location where HyperGraphQL is installed ('hypergraphql-master'): ")
    ICDDgraphLocation = ICDDtripleParser(ICDDfolder, HyperGraphQLFolder)
    ICDDschema = Ontology2HGQL(OntoFolder).HyperGraphQL
    schemaFile = open(ICDDgraphLocation+"schemaICDD.graphql", "w+")
    schemaFile.write(str(ICDDschema))
    configfile = createConfig(HyperGraphQLFolder)
    command = str('cd '+HyperGraphQLFolder+' && gradle execute -Pa="--classpath, --config, configICDD.json"')
    os.system(command)
    webbrowser.open_new_tab('http://localhost:8082/graphiql')

def main():
    ICDDquerier()

if __name__ == "__main__":
    main()