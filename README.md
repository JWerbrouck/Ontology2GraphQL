# Ontology2GraphQL
This is a drafting directory for converting OWL ontologies to a (Hyper)GraphQL schema. It takes either an RDF graph as an input, or a folder with RDF graphs to be combined in the schema.

# ICDD querying
An implementation to automatically convert the ICDD standard (Information Container for Data Drop, ISO 21597) to a HyperGraphQL schema, for querying heterogeneous datasets present in a construction project.

If you run this script directly, you need to enter the folder where the ICDD container is located, as well as the folder where a HyperGraphQL instance (https://www.hypergraphql.org/) is installed. The script parses the ontologies in the 'Ontology Resources' subfolder into a single schema, and unifies the index.rdf file and the rdf files in the 'Payload triples' folder into a queryable file. The results (schema, context and graph) are saved in the './src/main/resources/' subdirectory of the HyperGraphQL installation folder. Then, a HyperGraphQL server is set up at http://localhost:8082/ where you can visually query the ICDD container at http://localhost:8082/graphiql. 

Currently, only 'first order' triples are parsed into the schema, e.g.:

  * mapping container:containsDocument to its domain class 'container:ContainerDescription' and range 'container:Document' is supported:
  
  :containsDocument a owl:ObjectProperty ;
    rdfs:domain :ContainerDescription ;
    rdfs:range :Document ;
    
   becomes in the schema:
   
  type ContainerDescription @service(id:"icdd-local") {
	  containsLinkset: [Linkset] @service(id:"icdd-local")
	  containsDocument: [Document] @service(id:"icdd-local")
   }
  
  * mapping container:filename to its domain, which is a owl:unionOf container:Linkset and container:InternalDocument, is currently not possible.
  
  :filename a owl:DatatypeProperty,
    rdfs:domain [ a owl:Class ;
    owl:unionOf ( :Linkset :InternalDocument ) ] ;
    rdfs:range xsd:string .
    
    is not implemented in the schema.
    
Also, subclasses are currently supported at their domains (e.g. format is a field to both Document as its subclasses InternalDocument, ExternalDocument etc.), but not for their ranges (e.g. containsdocument is, in its class Containerdescription, only mapped to its range [Document]. Because inference of subclasses seems currently not present in HyperGraphQL, suggestions on how to implement this field to subclasses of 'Document', such as 'InternalDocument' etc. are welcome.
