from pydantic import BaseModel, Field, root_validator

class Setting(BaseModel):
    setting_basic_name: str
    setting_value: str
    setting_category: str
    is_custom_setting: bool
    
    @root_validator(pre=True)
    def check_category_length(cls, values):
        category = values.get('setting_category')
        if category and len(category) > 36:
            raise ValueError('setting_category must not exceed 36 characters')
        return values