from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from db_session import Base, PrimaryModel

class Permission(Base, PrimaryModel):
    __tablename__ = 'permissions'

    permission = Column(String, nullable=False, unique=True)
    description = Column(String)

class GroupPermission(Base, PrimaryModel):
    __tablename__ = 'group_permissions'

    permission_id = Column(UUID,ForeignKey('permissions.id'),nullable=False)
    group_id = Column(UUID,ForeignKey('groups.id'),nullable=False)

    UniqueConstraint(group_id,permission_id)
    permission = relationship(Permission, primaryjoin=permission_id == Permission.id)




