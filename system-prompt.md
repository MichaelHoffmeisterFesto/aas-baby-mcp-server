# Notes on system prompt

## Original prompt

```
This server provides access to instance data of Asset Administration Shells (AAS).
AAS is the concept of interoperable digital twins. 
Each AAS is identified by an unique identifier ("id").
These AAS unique identifiers are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584. 
Each AAS has also a short identifier ("idShort"), which identifies the element only in a given namespace.
Each AAS digitally represents an specific asset in digital twin scenarios.
An asset is any object or entity, which has an perceived value for an organization or individual.
An asset is identified by an unique identifier.
These asset identifiers are Uniform Resource Identifier (URI) according RFC 3986.
An asset may have a kind, which is either role, type, instance or not applicable.
An AAS may have an administrative information, specifying e.g. version and revision information.
An AAS may have asset information, which specifies the kind and the id of the asset.
Each AAS lists a set of AAS Submodels.
The term Submodel or AAS Submodel is written with a capital S in order to distinguish from the ordinary term.
Submodels can be found by finding an AAS, which is listing the particular Submodel ids, which then could be loaded in turn.
An AAS Submodel represents an specific aspect of the specfic asset of the AAS referring to that AAS Submodel.
Each AAS Submodel is identified by an unique identifier ("id").
These AAS Submodel unique identifiers are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584.                  
Each AAS Submodel has also a short identifier ("idShort"), which identifies the element only in a given namespace.
An AAS Submodel typically has an semanticId, which identifies the aspect the Submodel represents from the asset.
These semanticId are either Uniform Resource Identifier (URI) according RFC 3986 or International Registration Data Identifier (IRDI) according to IEC 61360 or ISO 13584.
An AAS Submodel typically has value elements; these Submodel elements form a hierarchy of elements.
Such Submodel element may be Property, SubmodelElementCollection, SubmodelElementList.
An Submodel element typically has an semanticId, which identifies the meaning of the particular element.
If the Submodel element is a Property, then it has a value and possibly a unit.
If the Submodel element is a SubmodelElementCollection or SubmodelElementList, then it typically has children.
```

## Asked ChatGPT for some guide

1. Separate ontology from behavioral instructions

   Right now, your prompt is almost entirely definitional (what an AAS is, what IDs look like, etc.). That’s useful context, but it doesn’t  tell the model what to do with it.
    
   A strong system prompt needs explicit operational guidance: 
    
   What is the agent’s role? 
   What decisions should it make? 
   How should it reason over AAS/Submodels? 
    
   What to change: 
   Add a section like: 
    
   “You are an industrial reasoning agent…” 
   “When a user asks X, you should…” 
   “To retrieve information, follow this sequence…” 
    
   Example improvement (conceptually): 
    
   “When asked about an asset property, first identify the relevant AAS via asset ID, then locate the appropriate Submodel via semanticId,  then traverse Submodel elements to extract values.”
    
   Without this, the model knows the schema but doesn’t know how to use it. 

2. Encode procedural patterns and constraints, not just structure

   You mention relationships (AAS → Submodel → elements), but you don’t formalize them as stepwise reasoning patterns. LLM agents perform much better when workflows are explicit.
   
   Think in terms of algorithms, not descriptions.
   
   What to change:
   Define canonical procedures such as:
   
   Lookup flow
   Disambiguation strategy (id vs idShort)
   Traversal rules for nested elements
   Handling missing data
   
   Example pattern:
   
   Step 1: Resolve asset identifier → find AAS
   Step 2: Inspect Submodel references
   Step 3: Match Submodel via semanticId
   Step 4: Traverse hierarchy recursively
   Step 5: Extract Property values (respect units)
   
   Also include negative constraints:
   
   “Do not assume values if not present”
   “Do not confuse idShort with globally unique id”
   
   This reduces hallucination and increases determinism.

3. Reduce redundancy and increase semantic density

   Your current prompt repeats concepts (IDs, URI formats, IRDI standards) more than necessary. This dilutes signal and consumes context window without improving behavior.
   
   LLMs benefit more from:
   
   Clear distinctions
   Compact definitions
   Emphasis on what matters for reasoning
   
   What to change:
   
   Collapse repeated ID definitions into a single normalized rule
   Remove standards references unless they affect reasoning (e.g., RFC/IEC numbers are rarely operationally useful)
   Highlight differences that matter:
   id (global) vs idShort (local)
   Submodel vs SubmodelElement
   semanticId as the key for meaning
   
   Example compression:
   Instead of repeating URI/IRDI rules multiple times:
   
   “All identifiers (AAS, Submodels, semanticIds) are globally unique and may be URIs or IRDIs. Treat them as opaque identifiers and match exactly.”
   
   This frees space for actual reasoning instructions.

*  Bottom line

   Your prompt currently answers: “What is the data model?”
   It should instead answer: “How should the agent think and act using this data model?”

## Formatting

ChatGPT:

Good instinct—formatting system prompts cleanly in source code is more important than most people realize. You want something that is:

* ASCII-safe
* indentation-consistent
* easy to diff and maintain
* directly pasteable into Python

Below is a clean version using only ASCII characters and Python-friendly formatting.

Why this formatting works (important for you to reuse)

1. ASCII-only separators
   Using ===== instead of markdown (###) ensures zero rendering ambiguity across systems.

2. Flat indentation
   Avoid deep nesting—LLMs parse structure from patterns, not whitespace depth.

3. Consistent bullets (-) and arrows (->)
   These act as lightweight "syntax hints" for the model.

4. Quoted field names ('id', 'semanticId')
   Prevents the model from generalizing or renaming schema fields.