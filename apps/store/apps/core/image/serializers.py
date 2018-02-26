from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    email = fields.Email()


class PdfSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.String()
    path = fields.String()
    created = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M.%S")
    user = fields.Nested(UserSchema)


class PdfImageSchema(Schema):
    id = fields.Int(dump_only=True)
    pdf = fields.Nested(PdfSchema)
    image = fields.String()
