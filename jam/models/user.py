from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from jam.extensions import db


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)
    email = db.Column(db.String(254), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(30))
    member_since = db.Column(db.DateTime, default=datetime.utcnow)

    confirmed = db.Column(db.Boolean, default=False)
    locked = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    # role_id = db.Column(db.Integer, db.ForeignKey("role.id"))
    # role = db.relationship("Role", back_populates="users")

    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def return_all(cls):
        def to_json(x):
            return {"username": x.username}

        return {
            "users": list(map(lambda x: to_json(x), UserModel.query.all()))
        }

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {"message": "{} row(s) deleted".format(num_rows_deleted)}
        except Exception:
            return {"message": "Something went wrong"}
