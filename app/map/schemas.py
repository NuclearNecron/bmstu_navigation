from marshmallow import Schema, fields


class NewTypeSchema(Schema):
    parent_id = fields.Int(required=False)
    name = fields.Str(required=True)
    shortname = fields.Str(required=True)
    description = fields.Str(required=False)


class UpdTypeSchema(Schema):
    name = fields.Str(required=False)
    shortname = fields.Str(required=False)
    description = fields.Str(required=False)


class NewNodeSchema(Schema):
    parent_id = fields.Int(required=False)
    name = fields.Str(required=True)
    shortname = fields.Str(required=True)
    description = fields.Str(required=False)
    type_id = fields.Int(required=True)
    x = fields.Float(requred=True)
    y = fields.Float(requred=True)
    z = fields.Float(requred=True)


class UpdNodeSchema(Schema):
    name = fields.Str(required=False)
    shortname = fields.Str(required=False)
    description = fields.Str(required=False)
    x = fields.Float(requred=False)
    y = fields.Float(requred=False)
    z = fields.Float(requred=False)


class NewConnSchema(Schema):
    node1_id = fields.Int(required=True)
    node2_id = fields.Int(required=True)
    distance = fields.Float(requred=True)
    time = fields.Float(requred=True)
    t_weight = fields.Float(requred=True)


class UpdConnSchema(Schema):
    distance = fields.Float(requred=False)
    time = fields.Float(requred=False)
    t_weight = fields.Float(requred=False)
