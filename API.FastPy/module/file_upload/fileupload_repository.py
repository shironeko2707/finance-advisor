from sqlalchemy.orm import Session, aliased
from typing import List, Optional
from module.file_upload.FileUploadModel import UploadedFile
from module.user_mgmt.UserModel import User

class FileUploadRepository:

    def get_uploaded_file_by_id(self, db: Session, file_id: int) -> Optional[UploadedFile]:
        """Get uploaded file by ID"""
        return db.query(UploadedFile).filter(UploadedFile.id == file_id).first()

    def get_uploaded_files(self, db: Session, skip: int = 0, limit: int = 100,
                           search: Optional[str] = None) -> List[UploadedFile]:
        """Get uploaded files with optional filtering and user info"""
        UserUploader = aliased(User)
        query = db.query(
            UploadedFile,
            UserUploader.first_name.label("uploader_first_name"),
            UserUploader.last_name.label("uploader_last_name")
        )\
                  .outerjoin(UserUploader, UploadedFile.uploaded_by == UserUploader.id)

        if search:
            search_term = f"%{search}%"
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    UploadedFile.original_filename.ilike(search_term),
                    UploadedFile.stored_filename.ilike(search_term),
                    UploadedFile.file_type.ilike(search_term)
                )
            )

        files_with_user_info = query.order_by(UploadedFile.uploaded_at.desc()).offset(skip).limit(limit).all()

        result_files = []
        for uploaded_file, uploader_first_name, uploader_last_name in files_with_user_info:
            if uploader_first_name and uploader_last_name:
                uploaded_file.uploaded_by_user = f"{uploader_first_name} {uploader_last_name}"
            elif uploader_first_name:
                uploaded_file.uploaded_by_user = uploader_first_name
            else:
                uploaded_file.uploaded_by_user = None
            result_files.append(uploaded_file)
        return result_files

    def get_uploaded_files_count(self, db: Session, search: Optional[str] = None) -> int:
        """Get total count of uploaded files with filtering"""
        query = db.query(UploadedFile)

        if search:
            search_term = f"%{search}%"
            from sqlalchemy import or_
            query = query.filter(
                or_(
                    UploadedFile.original_filename.ilike(search_term),
                    UploadedFile.stored_filename.ilike(search_term),
                    UploadedFile.file_type.ilike(search_term)
                )
            )
        return query.count()

    def create_uploaded_file(self, db: Session, file_info: dict) -> UploadedFile:
        """Create a new uploaded file record"""
        uploaded_file = UploadedFile(**file_info)
        db.add(uploaded_file)
        db.commit()
        db.refresh(uploaded_file)
        return uploaded_file

    def delete_uploaded_file(self, db: Session, file_id: int) -> bool:
        """Delete an uploaded file record by ID"""
        db_file = self.get_uploaded_file_by_id(db, file_id)
        if not db_file:
            return False
        db.delete(db_file)
        db.commit()
        return True

# Create a global instance to be imported by other modules
fileupload_repository = FileUploadRepository()