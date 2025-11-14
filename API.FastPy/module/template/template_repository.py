from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from sqlalchemy.orm import aliased
from module.template.TemplateModel import Template
from module.template.TemplateDTO import TemplateCreateDTO, TemplateUpdateDTO
from module.user_mgmt.UserModel import User

class TemplateRepository:

    def get_template_by_id(self, db: Session, template_id: int) -> Optional[Template]:
        """Get template by ID"""
        return db.query(Template).filter(Template.id == template_id).first()

    def get_template_by_name(self, db: Session, name: str) -> Optional[Template]:
        """Get template by name"""
        return db.query(Template).filter(Template.name == name).first()

    def get_templates(self, db: Session, skip: int = 0, limit: int = 100,
                     category: Optional[str] = None, search: Optional[str] = None) -> List[Template]:
        """Get templates with optional filtering"""
        UserCreator = aliased(User)
        UserModifier = aliased(User)
        query = db.query(
            Template,
            UserCreator.first_name.label("creator_first_name"),
            UserCreator.last_name.label("creator_last_name"),
            UserModifier.first_name.label("modifier_first_name"),
            UserModifier.last_name.label("modifier_last_name")
        )\
                  .outerjoin(UserCreator, Template.created_by == UserCreator.id)\
                  .outerjoin(UserModifier, Template.modified_by == UserModifier.id)

        # Filter by category if provided
        if category:
            query = query.filter(Template.category == category)

        # Search in name or category if search term provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Template.name.ilike(search_term),
                    Template.category.ilike(search_term)
                )
            )

        templates_with_user_info = query.order_by(Template.created_at.desc()).offset(skip).limit(limit).all()

        # Reconstruct the list of Template objects with creator_name and modifier_name
        result_templates = []
        for template, creator_first_name, creator_last_name, modifier_first_name, modifier_last_name in templates_with_user_info:
            if creator_first_name and creator_last_name:
                template.creator_name = f"{creator_first_name} {creator_last_name}"
            elif creator_first_name:
                template.creator_name = creator_first_name
            else:
                template.creator_name = None

            if modifier_first_name and modifier_last_name:
                template.modifier_name = f"{modifier_first_name} {modifier_last_name}"
            elif modifier_first_name:
                template.modifier_name = modifier_first_name
            else:
                template.modifier_name = None
            result_templates.append(template)
        return result_templates

    def get_templates_count(self, db: Session, category: Optional[str] = None,
                           search: Optional[str] = None) -> int:
        """Get total count of templates with filtering"""
        UserCreator = aliased(User)
        UserModifier = aliased(User)
        query = db.query(Template)\
                  .outerjoin(UserCreator, Template.created_by == UserCreator.id)\
                  .outerjoin(UserModifier, Template.modified_by == UserModifier.id)

        if category:
            query = query.filter(Template.category == category)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Template.name.ilike(search_term),
                    Template.category.ilike(search_term)
                )
            )

        return query.count()

    def get_templates_by_category(self, db: Session, category: str) -> List[Template]:
        """Get all templates in a specific category"""
        return db.query(Template).filter(Template.category == category).order_by(Template.name).all()

    def get_templates_by_user(self, db: Session, user_id: int) -> List[Template]:
        """Get all templates created by a specific user"""
        return db.query(Template).filter(Template.created_by == user_id).order_by(Template.created_at.desc()).all()

    def get_categories(self, db: Session) -> List[str]:
        """Get all unique template categories"""
        result = db.query(Template.category).distinct().all()
        return [category[0] for category in result]

    def create_template(self, db: Session, template: TemplateCreateDTO) -> Template:
        """Create a new template"""
        db_template = Template(**template.model_dump())
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return db_template

    def update_template(self, db: Session, template_id: int, template_update: TemplateUpdateDTO) -> Optional[Template]:
        """Update an existing template"""
        db_template = self.get_template_by_id(db, template_id)
        if not db_template:
            return None

        # Update only provided fields
        update_data = template_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)
        
        # Ensure modified_by is updated if present in the DTO
        if template_update.modified_by is not None:
            db_template.modified_by = template_update.modified_by

        db.commit()
        db.refresh(db_template)
        return db_template

    def delete_template(self, db: Session, template_id: int) -> bool:
        """Delete a template by ID"""
        db_template = self.get_template_by_id(db, template_id)
        if not db_template:
            return False

        db.delete(db_template)
        db.commit()
        return True

    def check_name_exists(self, db: Session, name: str, exclude_id: Optional[int] = None) -> bool:
        """Check if template name already exists (excluding specific ID for updates)"""
        query = db.query(Template).filter(Template.name == name)
        if exclude_id:
            query = query.filter(Template.id != exclude_id)
        return query.first() is not None

# Create a global instance to be imported by other modules
template_repository = TemplateRepository()
