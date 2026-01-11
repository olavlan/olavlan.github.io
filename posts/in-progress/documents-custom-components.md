# Documents with custom components

Premises:
* We have a Pydantic schema for a custom component of a technical document.
* We have one or more specifications for how to define the component in various document formats.
* Given a document with a component, we can convert into pandoc AST and parse the component into its Pydantic model.

Question: How can documentation/templates/examples be dynamically created from the model, such that a change in the model would automatically be documented?
