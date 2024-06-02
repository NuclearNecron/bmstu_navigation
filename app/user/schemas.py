from marshmallow import Schema, fields


class UserSchema(Schema):
    name = fields.Str(required=False)
    surname = fields.Str(required=False)
    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class NewUserSchema(Schema):
    name = fields.Str(required=True)
    surname = fields.Str(required=True)
    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class NewAccessSchema(Schema):
    name = fields.Str(required=True)


class NewUserAccessSchema(Schema):
    user_id = fields.Int(required=True)
    role_id = fields.Int(reqired=True)


class UpdUserSchema(Schema):
    name = fields.Str(required=False)
    surname = fields.Str(required=False)
