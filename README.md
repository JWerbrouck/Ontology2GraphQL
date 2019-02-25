# Ontology2GraphQL
This is a drafting directory for converting OWL ontologies to a (Hyper)GraphQL schema. It takes either an RDF graph as an input, or a folder with RDF graphs to be combined in the schema.

# ICDD querying
An implementation to automatically convert the ICDD standard (Information Container for Data Drop, ISO 21597) to a HyperGraphQL schema, for querying heterogeneous datasets present in a construction project.

If you run this script directly, you need to enter the folder where the ICDD container is located, as well as the folder where a HyperGraphQL instance (https://www.hypergraphql.org/) is installed. The script parses the ontologies in the 'Ontology Resources' subfolder into a single schema, and unifies the index.rdf file and the rdf files in the 'Payload triples' folder into a queryable file. The results (schema, context and graph) are saved in the './src/main/resources/' subdirectory of the HyperGraphQL installation folder. Then, a HyperGraphQL server is set up at http://localhost:8082/ where you can visually query the ICDD container at http://localhost:8082/graphiql. 
