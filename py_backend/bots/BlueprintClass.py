from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

# Define the basic types
StringType = str
NumberType = Union[int, float]


@dataclass
class PropertyDetailSchema:
    type: str
    description: str
    value: Optional[Union[StringType, NumberType, List[Any]]] = None

    # This method ensures that the value assigned matches the type
    def set_value(self, val: Any):
        if self.type == "string" and isinstance(val, StringType):
            self.value = val
        elif self.type == "number" and isinstance(val, (int, float)):
            self.value = val
        elif self.type == "array" and isinstance(val, list):
            # Ensure items in the list match the specified type
            if all(isinstance(item, StringType) for item in val):
                self.value = val
            else:
                raise ValueError("Invalid item type in array.")
        else:
            raise ValueError("Type mismatch.")


@dataclass
class ParameterSchema:
    type: str
    properties: Dict[str, PropertyDetailSchema] = field(default_factory=dict)
    required: Optional[List[str]] = field(default_factory=list)


@dataclass
class FunctionSchema:
    name: str
    description: Optional[str] = None
    parameters: Optional[List[ParameterSchema]] = field(default_factory=list)

    def __getitem__(self, key):
        return getattr(self, key)


@dataclass
class BlueprintClass:
    blueprint_id: str
    blueprint_name: str
    blueprint_description: str
    initial_context: list
    sub_topic_name: Optional[str] = "strategy-market_obsticle-general"
    pub_topic_name: Optional[str] = "strategy-market_obsticle-typed"
    functions: Optional[List[FunctionSchema]] = field(default_factory=list)
    ignored_roles: Optional[List[str]] = field(default_factory=lambda: ["system"])
    source_type: Optional[str] = "functional"
    ignored_source_types: Optional[List[str]] = field(
        default_factory=lambda: ["functional"]
    )


# test_data_parameters = {
#     "type": "object",
#     "properties": {
#         "name": {
#             "type": "string",
#             "description": "frieldy name of the persona",
#         },
#         "age": {
#             "type": "number",
#             "description": "age of the persona",
#         },
#         "personality_traits": {
#             "type": "array",
#             "items": {
#                 "type": "string",
#                 "description": "personality traits of the persona",
#             },
#         },
#     },
#     "required": [
#         "name",
#         "age",
#         "personality_traits",
#     ],
# }

# test_data_functions = [
#     {
#         "name": "save_persona",
#         "description": "Save information related to a given persona",
#         "parameters": test_data_parameters,
#         "required": [
#             "name",
#             "age",
#             "occupation",
#             "personality_traits",
#             "education",
#             "interests",
#             "pain_points",
#             "goals",
#         ],
#     },
# ]


def construct_function_schema(data: dict) -> FunctionSchema:
    # Convert the 'parameters' dictionary to ParameterSchema
    param_schema = ParameterSchema(
        type=data["parameters"]["type"],
        properties={
            key: PropertyDetailSchema(**value)
            for key, value in data["parameters"]["properties"].items()
        },
        required=data["parameters"].get("required", []),
    )

    return FunctionSchema(
        name=data["name"],
        description=data.get("description"),
        parameters=[
            param_schema
        ],  # Notice the list here, since 'parameters' in 'FunctionSchema' is a List[ParameterSchema]
    )


# converted_test_data_functions = [
#     construct_function_schema(data) for data in test_data_functions
# ]

# blueprint_test = BlueprintClass(
#     blueprint_id="test",
#     blueprint_name="Test Blueprint",
#     blueprint_description="This is a test blueprint",
#     initial_context=["test"],
#     sub_topic_name="test",
#     pub_topic_name="test",
#     functions=converted_test_data_functions,
# )
