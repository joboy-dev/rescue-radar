from typing import Dict, Any
import sqlalchemy as sa
from uuid import uuid4

from api.db.database import Base, get_db


class BaseTableModel(Base):
    """This model creates helper methods for all models"""

    __abstract__ = True

    id = sa.Column(sa.String, primary_key=True, index=True, default=lambda: str(uuid4().hex))
    is_deleted = sa.Column(sa.Boolean, server_default='false')
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())

    def to_dict(self):
        """Returns a dictionary representation of the instance"""
        
        obj_dict = self.__dict__.copy()
        del obj_dict["_sa_instance_state"]
        obj_dict["id"] = self.id
        if self.created_at:
            obj_dict["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            obj_dict["updated_at"] = self.updated_at.isoformat()
            
        # Process relationships
        for relationship_name in self.__mapper__.relationships.keys():
            # Get the related object
            related_obj = getattr(self, relationship_name)

            if related_obj is None:
                obj_dict[relationship_name] = None
            elif isinstance(related_obj, list):  # One-to-Many or Many-to-Many
                obj_dict[relationship_name] = [item.to_dict() for item in related_obj]
            else:  # Many-to-One or One-to-One
                obj_dict[relationship_name] = related_obj.to_dict()

        return obj_dict

    @classmethod
    def create(self, **kwargs):
        """Creates a new instance of the model"""
        
        db = next(get_db())
        
        obj = self(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def all(
        self, 
        page: int = 1, 
        per_page: int = 10, 
        sort_by: str = "created_at", 
        order: str = "desc",
        show_deleted: bool = False
    ):
        """Fetches all instances with pagination and sorting"""
        
        db = next(get_db())
        query = db.query(self).filter_by(is_deleted=False) if not show_deleted else db.query(self)

        # Handle sorting
        if order == "desc":
            query = query.order_by(sa.desc(getattr(self, sort_by)))
        else:
            query = query.order_by(getattr(self, sort_by))

        # Handle pagination
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page).all()

    @classmethod
    def fetch_by_id(self, id: str):
        """Fetches a single instance by ID (ignores soft-deleted records)"""
        
        db = next(get_db())
        return db.query(self).filter_by(id=id, is_deleted=False).first()

    @classmethod
    def fetch_one_by_field(self, **kwargs):
        """Fetches one unique record that match the given field(s)"""
        
        db = next(get_db())
        kwargs["is_deleted"] = False
        return db.query(self).filter_by(**kwargs).first()
    
    @classmethod
    def fetch_by_field(self, **kwargs):
        """Fetches all records that match the given field(s)"""
        
        db = next(get_db())
        kwargs["is_deleted"] = False
        return db.query(self).filter_by(**kwargs).all()

    @classmethod
    def update(self, id: str, **kwargs):
        """Updates an instance with the given ID"""
        
        db = next(get_db())
        obj = db.query(self).filter_by(id=id, is_deleted=False).first()
        if not obj:
            return None  # Return None if the object isn't found
        for key, value in kwargs.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    @classmethod
    def soft_delete(self, id: str):
        """Performs a soft delete by setting is_deleted to the current timestamp"""
        
        db = next(get_db())
        obj = db.query(self).filter_by(id=id, is_deleted=False).first()
        if obj:
            obj.is_deleted = True
            db.commit()

    @classmethod
    def hard_delete(self, id: str):
        """Permanently deletes an instance by ID"""
        
        db = next(get_db())
        obj = db.query(self).filter_by(id=id).first()
        if obj:
            db.delete(obj)
            db.commit()

    @classmethod
    def custom_query(
        self, 
        filters: Dict[str, Any] = {}, 
        sort_by: str = "created_at", 
        order: str = "desc", 
        page: int = 1, 
        per_page: int = 10
    ):
        """Custom query with filtering, sorting, and pagination"""
        
        db = next(get_db())
        
        query = db.query(self)
        # Apply filters
        for field, value in filters.items():
            query = query.filter(getattr(self, field) == value)

        # Apply soft delete filter
        query = query.filter_by(is_deleted=False)

        # Sorting
        if order == "desc":
            query = query.order_by(sa.desc(getattr(self, sort_by)))
        else:
            query = query.order_by(getattr(self, sort_by))

        # Pagination
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page).all()
    
    @classmethod
    def search(cls, search_fields: Dict[str, str], page: int = 1, per_page: int = 10):
        """
        Performs a search on the model based on the provided fields and values.

        :param search_fields: A dictionary where keys are field names and values are search terms.
        :param page: The page number for pagination (default is 1).
        :param per_page: The number of records per page (default is 10).
        :return: A list of matching records.
        """
        db = next(get_db())

        # Start building the query
        query = db.query(cls)

        # Apply search filters
        for field, value in search_fields.items():
            query = query.filter(getattr(cls, field).ilike(f"%{value}%"))

        # Exclude soft-deleted records
        query = query.filter(cls.is_deleted == False)

        # Apply pagination
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page).all()
    
    @classmethod
    def fetch_with_join(
        self,
        related_model, 
        join_field: str, 
        page: int = 1, 
        per_page: int = 10, 
        sort_by: str = "created_at", 
        order: str = "desc", 
        **kwargs
    ):
        """
        Fetch records with a join between this model and the related model, with pagination and sorting.

        :param related_model: The related model class (e.g., `User`, `Responder`, etc.)
        :param join_field: The field on which the join will be made (e.g., `Emergency.user_id == User.id`)
        :param page: The page number for pagination (default is 1)
        :param per_page: Number of records per page (default is 10)
        :param sort_by: The field to sort by (default is 'created_at')
        :param order: Sort order, either 'asc' for ascending or 'desc' for descending (default is 'asc')
        :param kwargs: Optional filter parameters
        """
        
        db = next(get_db())

        # Construct the join condition
        query = db.query(self).join(related_model, join_field)

        # Apply filters
        for field, value in kwargs.items():
            query = query.filter(getattr(self, field) == value)

        # Apply soft delete filter (ignoring deleted records)
        query = query.filter(self.is_deleted == False)

        # Handle sorting
        if order == "desc":
            query = query.order_by(sa.desc(getattr(self, sort_by)))
        else:
            query = query.order_by(getattr(self, sort_by))

        # Handle pagination
        offset = (page - 1) * per_page
        return query.offset(offset).limit(per_page).all()
