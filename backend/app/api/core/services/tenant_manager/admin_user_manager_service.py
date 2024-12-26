from pydantic import BaseModel, Field
from typing import List
from uuid import UUID
from fastapi import HTTPException
from utils.database import mongodb
from model.tenant.tenant import Tenant, AdminUser
from model.responses.tenant_manager.admin_response import GetAdminUserResponse
from utils.hash_utils import hash_password
from pymongo import ASCENDING

SUPPORTED_ROLES_STR = {"Ruleset Admin", "Schema Admin", "Tenant Admin"}

class AdminUserService:

    @staticmethod
    async def create_indexes():
        """
        Create indexes for ensuring unique admin user IDs within each tenant.
        """
        collection = mongodb.db["tenants"]
        await collection.create_index(
            [("tenant_id", ASCENDING), ("admins.user_id", ASCENDING)],
            unique=True
        )

    @staticmethod
    async def get_admin(tenant_id: str, user_id: str) -> GetAdminUserResponse:
        """
        Retrieve a specific admin by tenant ID and user ID.
        """
        tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = Tenant(**tenant_data)
        admin = next((admin for admin in tenant.admins if admin.user_id == user_id), None)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        return GetAdminUserResponse(user_id=admin.user_id, role=admin.role)

    @staticmethod
    async def get_admins(tenant_id: str) -> List[GetAdminUserResponse]:
        """
        Retrieve all admins associated with a given tenant ID.
        """
        tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = Tenant(**tenant_data)
        return [GetAdminUserResponse(user_id=admin.user_id, role=admin.role) for admin in tenant.admins]


    @staticmethod
    async def add_admin(tenant_id: str, admin: AdminUser) -> GetAdminUserResponse:
        """
        Add a new admin to the specified tenant.
        """
        if admin.role not in SUPPORTED_ROLES_STR:
            raise HTTPException(status_code=400, detail="Invalid admin role")

        # Check if user_id already exists in admins array
        tenant_data = await mongodb.db["tenants"].find_one({"tenant_id": tenant_id})
        if not tenant_data:
            raise HTTPException(status_code=404, detail="Tenant not found")

        tenant = Tenant(**tenant_data)
        if any(existing_admin.user_id == admin.user_id for existing_admin in tenant.admins):
            raise HTTPException(status_code=400, detail="Admin with this user_id already exists")

        admin.password = hash_password(admin.password)
        
        # Add the admin
        result = await mongodb.db["tenants"].update_one(
            {"tenant_id": tenant_id},
            {"$push": {"admins": admin.dict()}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Tenant not found")

        return GetAdminUserResponse(user_id=admin.user_id, role=admin.role)


    @staticmethod
    async def update_admin(tenant_id: str, user_id: str, updated_admin: AdminUser) -> GetAdminUserResponse:
        """
        Update admin details by user_id within a tenant.
        """
        result = await mongodb.db["tenants"].update_one(
            {"tenant_id": tenant_id, "admins.user_id": user_id},
            {"$set": {"admins.$": updated_admin.dict()}}
        )
        
        updated_admin.password = hash_password(updated_admin.password)
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Admin not found or Tenant not found")
        return GetAdminUserResponse(user_id=updated_admin.user_id, role=updated_admin.role)

    @staticmethod
    async def delete_admin(tenant_id: str, user_id: str):
        """
        Delete an admin by user_id within a tenant.
        """
        result = await mongodb.db["tenants"].update_one(
            {"tenant_id": tenant_id},
            {"$pull": {"admins": {"user_id": user_id}}}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Admin not found or Tenant not found")
